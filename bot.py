import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from telegram.constants import ParseMode
import config
from database import db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_GIFT_CARD = 1
WAITING_FOR_SUPPORT_MESSAGE = 2
WAITING_FOR_COUPON_CODES = 3
WAITING_FOR_BROADCAST_MESSAGE = 4

# Coupon types and prices
COUPON_TYPES = {
    1000: 300,
    2000: 550,
    4000: 900
}


def is_admin(user_id: int) -> bool:
    """Check if user is an admin"""
    return user_id in config.ADMIN_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user

    # Add user to database
    db.add_user(user.id, user.username, user.first_name)

    # Check if bot is online
    if not db.is_bot_online() and not is_admin(user.id):
        offline_msg = db.get_offline_message()
        await update.message.reply_text(offline_msg)
        return

    # Check if user already agreed to terms
    if db.has_user_agreed(user.id):
        await show_main_menu(update, context)
        return

    # Show terms and conditions
    keyboard = [
        [
            InlineKeyboardButton("✅ Agree", callback_data="agree_terms"),
            InlineKeyboardButton("❌ Decline", callback_data="decline_terms")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_msg = f"👋 Welcome to Coupon Store, {user.first_name}!\n\n"
    welcome_msg += config.TERMS_AND_CONDITIONS

    await update.message.reply_text(welcome_msg, reply_markup=reply_markup)


async def handle_terms_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle terms agreement response"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "agree_terms":
        db.user_agreed_to_terms(user_id)
        await query.edit_message_text("✅ Thank you for agreeing to our terms!\n\nLoading store...")
        await show_main_menu_after_callback(query, context)
    elif query.data == "decline_terms":
        keyboard = [
            [InlineKeyboardButton("✅ I Agree Now", callback_data="agree_terms")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "❌ You must agree to our Terms and Conditions to proceed.\n\n"
            "Please click the button below when you're ready to agree.",
            reply_markup=reply_markup
        )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu with available coupons"""
    # Get available stock
    stock = db.get_available_stock()

    keyboard = []
    message = "🛍️ *Welcome to Coupon Store*\n\n"
    message += "📦 *Available Coupons:*\n\n"

    has_stock = False
    for coupon_type, price in COUPON_TYPES.items():
        available = stock.get(coupon_type, 0)
        if available > 0:
            has_stock = True
            message += f"💳 ₹{coupon_type} Coupon → *₹{price}*\n"
            message += f"   📊 Stock: {available} available\n\n"
            keyboard.append([
                InlineKeyboardButton(
                    f"Buy ₹{coupon_type} Coupon (₹{price})",
                    callback_data=f"buy_{coupon_type}"
                )
            ])
        else:
            message += f"💳 ₹{coupon_type} Coupon → ❌ *OUT OF STOCK*\n\n"

    if not has_stock:
        message = "⚠️ *All Coupons are OUT OF STOCK*\n\n"
        message += "Please check back later!"
    else:
        keyboard.append([InlineKeyboardButton("📞 Contact Support", callback_data="support")])

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    await update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )


async def show_main_menu_after_callback(query, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu after a callback query"""
    # Get available stock
    stock = db.get_available_stock()

    keyboard = []
    message = "🛍️ *Welcome to Coupon Store*\n\n"
    message += "📦 *Available Coupons:*\n\n"

    has_stock = False
    for coupon_type, price in COUPON_TYPES.items():
        available = stock.get(coupon_type, 0)
        if available > 0:
            has_stock = True
            message += f"💳 ₹{coupon_type} Coupon → *₹{price}*\n"
            message += f"   📊 Stock: {available} available\n\n"
            keyboard.append([
                InlineKeyboardButton(
                    f"Buy ₹{coupon_type} Coupon (₹{price})",
                    callback_data=f"buy_{coupon_type}"
                )
            ])
        else:
            message += f"💳 ₹{coupon_type} Coupon → ❌ *OUT OF STOCK*\n\n"

    if not has_stock:
        message = "⚠️ *All Coupons are OUT OF STOCK*\n\n"
        message += "Please check back later!"
    else:
        keyboard.append([InlineKeyboardButton("📞 Contact Support", callback_data="support")])

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    await query.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )


async def handle_buy_coupon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle coupon purchase"""
    query = update.callback_query
    await query.answer()

    # Extract coupon type from callback data
    coupon_type = int(query.data.split('_')[1])
    price = COUPON_TYPES[coupon_type]

    # Check stock
    stock = db.get_available_stock()
    if stock.get(coupon_type, 0) <= 0:
        await query.edit_message_text("❌ Sorry, this coupon is out of stock!")
        return

    # Store selected coupon in user context
    context.user_data['selected_coupon'] = coupon_type
    context.user_data['selected_price'] = price

    # Show payment instructions
    message = f"💳 *Purchase ₹{coupon_type} Coupon*\n\n"
    message += f"💰 Amount to pay: *₹{price}*\n\n"
    message += "📝 *Payment Instructions:*\n\n"
    message += "1️⃣ Go to Amazon Gift Cards:\n"
    message += "   https://www.amazon.in/gift-cards\n\n"
    message += "2️⃣ Select *'Email'* gift card\n\n"
    message += f"3️⃣ Enter amount: *₹{price}*\n\n"
    message += "4️⃣ Enter *YOUR email* (you'll receive the code)\n\n"
    message += "5️⃣ Complete payment\n\n"
    message += "6️⃣ Copy the 14-digit gift card code\n\n"
    message += "7️⃣ Send the code here\n\n"
    message += "⏰ Please complete payment and send the code.\n\n"
    message += "_Example code format: ABCD-EFGH12-JKLM_"

    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_purchase")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

    return WAITING_FOR_GIFT_CARD


async def handle_gift_card_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gift card code submission"""
    user_id = update.effective_user.id
    gift_card_code = update.message.text.strip()

    # Get selected coupon from context
    coupon_type = context.user_data.get('selected_coupon')
    price = context.user_data.get('selected_price')

    if not coupon_type:
        await update.message.reply_text("❌ Error: No coupon selected. Please start over with /start")
        return ConversationHandler.END

    # Check stock again
    stock = db.get_available_stock()
    if stock.get(coupon_type, 0) <= 0:
        await update.message.reply_text("❌ Sorry, this coupon is now out of stock!")
        context.user_data.clear()
        return ConversationHandler.END

    # Create transaction
    transaction_id = db.create_transaction(user_id, coupon_type, price, gift_card_code)

    # Notify user
    await update.message.reply_text(
        "✅ *Payment Submitted Successfully!*\n\n"
        "🔍 Your payment is being verified by our admin.\n\n"
        "⏳ You will receive your coupon code shortly.\n\n"
        "Thank you for your patience!",
        parse_mode=ParseMode.MARKDOWN
    )

    # Notify all admins
    user = update.effective_user
    username_display = f"@{user.username}" if user.username else user.first_name

    for admin_id in config.ADMIN_IDS:
        try:
            admin_message = f"🔔 *NEW PAYMENT RECEIVED*\n\n"
            admin_message += f"👤 User: {username_display}\n"
            admin_message += f"🆔 User ID: `{user_id}`\n"
            admin_message += f"💳 Product: ₹{coupon_type} Coupon\n"
            admin_message += f"💰 Price: ₹{price}\n"
            admin_message += f"🎁 Gift Card Code:\n`{gift_card_code}`\n\n"
            admin_message += f"📋 Transaction ID: `{transaction_id}`"

            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{transaction_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{transaction_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

    # Clear user context
    context.user_data.clear()

    return ConversationHandler.END


async def handle_admin_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin approval/rejection"""
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("⛔ Unauthorized", show_alert=True)
        return

    action, transaction_id = query.data.split('_')
    transaction_id = int(transaction_id)

    # Get transaction details
    transaction = db.get_transaction(transaction_id)
    if not transaction:
        await query.edit_message_text("❌ Transaction not found!")
        return

    if transaction['status'] != 'pending':
        await query.edit_message_text(f"⚠️ Transaction already {transaction['status']}!")
        return

    if action == "approve":
        # Check if coupon is available
        coupon_id = db.get_available_coupon(transaction['coupon_type'])

        if not coupon_id:
            await query.edit_message_text(
                "❌ *Approval Failed*\n\n"
                "No coupons available for this type!\n"
                "Please add more coupons first.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Approve transaction
        db.approve_transaction(transaction_id, coupon_id, query.from_user.id)

        # Mark coupon as sold
        db.mark_coupon_sold(coupon_id, transaction['user_id'])

        # Get coupon code
        coupon_code = db.get_coupon_code(coupon_id)

        # Send coupon to user
        try:
            user_message = "🎉 *PAYMENT VERIFIED!*\n\n"
            user_message += f"✅ Your ₹{transaction['coupon_type']} Coupon Code:\n\n"
            user_message += f"`{coupon_code}`\n\n"
            user_message += "Thank you for your purchase! 💚\n\n"
            user_message += "Use /start to buy more coupons!"

            await context.bot.send_message(
                chat_id=transaction['user_id'],
                text=user_message,
                parse_mode=ParseMode.MARKDOWN
            )

            # Update admin message
            updated_msg = query.message.text + f"\n\n✅ *APPROVED* by {query.from_user.first_name}"
            await query.edit_message_text(updated_msg, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Failed to send coupon to user: {e}")
            await query.answer("⚠️ Approved but failed to notify user", show_alert=True)

    elif action == "reject":
        # Reject transaction
        db.reject_transaction(transaction_id, query.from_user.id)

        # Notify user
        try:
            user_message = "❌ *Payment Verification Failed*\n\n"
            user_message += "Your payment could not be verified.\n"
            user_message += "The gift card code provided was invalid or already used.\n\n"
            user_message += "Please contact support if you believe this is an error.\n"
            user_message += "Use /start to try again."

            await context.bot.send_message(
                chat_id=transaction['user_id'],
                text=user_message,
                parse_mode=ParseMode.MARKDOWN
            )

            # Update admin message
            updated_msg = query.message.text + f"\n\n❌ *REJECTED* by {query.from_user.first_name}"
            await query.edit_message_text(updated_msg, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Failed to notify user about rejection: {e}")
            await query.answer("⚠️ Rejected but failed to notify user", show_alert=True)


async def cancel_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel purchase"""
    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    await query.edit_message_text("❌ Purchase cancelled.\n\nUse /start to browse coupons again.")

    return ConversationHandler.END


async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle support request"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📞 *Contact Support*\n\n"
        "Please type your message below and we'll get back to you soon.\n\n"
        "Type /cancel to go back.",
        parse_mode=ParseMode.MARKDOWN
    )

    return WAITING_FOR_SUPPORT_MESSAGE


async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle support message from user"""
    user_id = update.effective_user.id
    message = update.message.text

    # Save message to database
    db.add_support_message(user_id, message)

    # Notify user
    await update.message.reply_text(
        "✅ *Message sent to support!*\n\n"
        "We'll review your message and get back to you soon.\n\n"
        "Use /start to return to the main menu.",
        parse_mode=ParseMode.MARKDOWN
    )

    # Notify admins
    user = update.effective_user
    username_display = f"@{user.username}" if user.username else user.first_name

    for admin_id in config.ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"💬 *NEW SUPPORT MESSAGE*\n\n"
                     f"👤 From: {username_display}\n"
                     f"🆔 User ID: `{user_id}`\n\n"
                     f"Message:\n{message}",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

    return ConversationHandler.END


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Unauthorized access.")
        return

    bot_online = db.is_bot_online()
    stats = db.get_stats()
    pending_count = len(db.get_pending_transactions())

    status_emoji = "🟢" if bot_online else "🔴"
    status_text = "ONLINE" if bot_online else "OFFLINE"

    message = f"🎛️ *ADMIN PANEL*\n\n"
    message += f"Bot Status: {status_emoji} *{status_text}*\n\n"
    message += f"📊 *Statistics:*\n"
    message += f"• Total Sales: {stats['total_sales']}\n"
    message += f"• Total Revenue: ₹{stats['total_revenue']}\n"
    message += f"• Pending Verifications: {pending_count}\n"
    message += f"• Total Users: {stats['total_users']}\n\n"
    message += f"📦 *Stock:*\n"

    for coupon_type in [1000, 2000, 4000]:
        count = stats['stock'].get(coupon_type, 0)
        message += f"• ₹{coupon_type}: {count} available\n"

    keyboard = [
        [
            InlineKeyboardButton(
                "🟢 Turn ON" if not bot_online else "🔴 Turn OFF",
                callback_data="toggle_bot"
            )
        ],
        [
            InlineKeyboardButton("➕ Add Coupons", callback_data="add_coupons"),
            InlineKeyboardButton("📊 View Stats", callback_data="view_stats")
        ],
        [
            InlineKeyboardButton("🔍 Pending Verifications", callback_data="pending_verifications"),
            InlineKeyboardButton("📢 Send Announcement", callback_data="send_announcement")
        ],
        [
            InlineKeyboardButton("✏️ Edit Offline Message", callback_data="edit_offline_msg")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)


async def toggle_bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle bot online/offline"""
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    current_status = db.is_bot_online()
    new_status = not current_status
    db.set_bot_online(new_status)

    status_text = "ONLINE" if new_status else "OFFLINE"

    await query.answer(f"✅ Bot is now {status_text}", show_alert=True)

    # Refresh admin panel
    await refresh_admin_panel(query, context)


async def refresh_admin_panel(query, context: ContextTypes.DEFAULT_TYPE):
    """Refresh admin panel"""
    bot_online = db.is_bot_online()
    stats = db.get_stats()
    pending_count = len(db.get_pending_transactions())

    status_emoji = "🟢" if bot_online else "🔴"
    status_text = "ONLINE" if bot_online else "OFFLINE"

    message = f"🎛️ *ADMIN PANEL*\n\n"
    message += f"Bot Status: {status_emoji} *{status_text}*\n\n"
    message += f"📊 *Statistics:*\n"
    message += f"• Total Sales: {stats['total_sales']}\n"
    message += f"• Total Revenue: ₹{stats['total_revenue']}\n"
    message += f"• Pending Verifications: {pending_count}\n"
    message += f"• Total Users: {stats['total_users']}\n\n"
    message += f"📦 *Stock:*\n"

    for coupon_type in [1000, 2000, 4000]:
        count = stats['stock'].get(coupon_type, 0)
        message += f"• ₹{coupon_type}: {count} available\n"

    keyboard = [
        [
            InlineKeyboardButton(
                "🟢 Turn ON" if not bot_online else "🔴 Turn OFF",
                callback_data="toggle_bot"
            )
        ],
        [
            InlineKeyboardButton("➕ Add Coupons", callback_data="add_coupons"),
            InlineKeyboardButton("📊 View Stats", callback_data="view_stats")
        ],
        [
            InlineKeyboardButton("🔍 Pending Verifications", callback_data="pending_verifications"),
            InlineKeyboardButton("📢 Send Announcement", callback_data="send_announcement")
        ],
        [
            InlineKeyboardButton("✏️ Edit Offline Message", callback_data="edit_offline_msg")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)


async def handle_add_coupons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add coupons request"""
    query = update.callback_query
    await query.answer()

    message = "➕ *Add Coupons*\n\n"
    message += "Please send coupon codes in the following format:\n\n"
    message += "`TYPE:CODE`\n\n"
    message += "*Examples:*\n"
    message += "`1000:ABC123XYZ`\n"
    message += "`2000:DEF456UVW`\n"
    message += "`4000:GHI789RST`\n\n"
    message += "You can send multiple codes, one per line.\n"
    message += "Type /cancel to go back."

    await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)

    return WAITING_FOR_COUPON_CODES


async def handle_coupon_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle coupon codes submission"""
    text = update.message.text.strip()
    lines = text.split('\n')

    added = 0
    failed = 0
    errors = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        try:
            parts = line.split(':')
            if len(parts) != 2:
                errors.append(f"Invalid format: {line}")
                failed += 1
                continue

            coupon_type = int(parts[0].strip())
            code = parts[1].strip()

            if coupon_type not in COUPON_TYPES:
                errors.append(f"Invalid type {coupon_type}: {line}")
                failed += 1
                continue

            price = COUPON_TYPES[coupon_type]

            if db.add_coupon(code, coupon_type, price):
                added += 1
            else:
                errors.append(f"Duplicate code: {code}")
                failed += 1

        except Exception as e:
            errors.append(f"Error: {line} - {str(e)}")
            failed += 1

    response = f"✅ *Coupons Added Successfully!*\n\n"
    response += f"Added: {added}\n"
    response += f"Failed: {failed}\n"

    if errors:
        response += f"\n*Errors:*\n"
        for error in errors[:5]:  # Show first 5 errors
            response += f"• {error}\n"
        if len(errors) > 5:
            response += f"...and {len(errors) - 5} more\n"

    response += "\nUse /admin to return to admin panel."

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    return ConversationHandler.END


async def handle_pending_verifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending verifications"""
    query = update.callback_query
    await query.answer()

    pending = db.get_pending_transactions()

    if not pending:
        await query.edit_message_text(
            "✅ No pending verifications!\n\nUse /admin to return to admin panel."
        )
        return

    message = f"🔍 *Pending Verifications ({len(pending)})*\n\n"

    for txn in pending[:5]:  # Show first 5
        username = f"@{txn['username']}" if txn['username'] else txn['first_name']
        message += f"👤 {username}\n"
        message += f"💳 ₹{txn['coupon_type']} Coupon (₹{txn['price']})\n"
        message += f"🎁 Code: `{txn['gift_card_code']}`\n"
        message += f"Transaction ID: `{txn['id']}`\n\n"

    if len(pending) > 5:
        message += f"...and {len(pending) - 5} more\n\n"

    message += "Use /admin to verify transactions."

    await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)


async def handle_send_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle send announcement"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📢 *Send Announcement*\n\n"
        "Type your announcement message below.\n"
        "It will be sent to all users who have used the bot.\n\n"
        "Type /cancel to go back.",
        parse_mode=ParseMode.MARKDOWN
    )

    return WAITING_FOR_BROADCAST_MESSAGE


async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast message"""
    message = update.message.text
    users = db.get_all_users()

    sent = 0
    failed = 0

    status_msg = await update.message.reply_text(f"📤 Sending to {len(users)} users...")

    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 *ANNOUNCEMENT*\n\n{message}",
                parse_mode=ParseMode.MARKDOWN
            )
            sent += 1
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")
            failed += 1

    await status_msg.edit_text(
        f"✅ *Broadcast Complete!*\n\n"
        f"Sent: {sent}\n"
        f"Failed: {failed}\n\n"
        f"Use /admin to return to admin panel.",
        parse_mode=ParseMode.MARKDOWN
    )

    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current conversation"""
    await update.message.reply_text(
        "❌ Cancelled.\n\nUse /start or /admin to continue."
    )
    return ConversationHandler.END


def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))

    # Terms agreement handler
    application.add_handler(CallbackQueryHandler(handle_terms_response, pattern="^(agree|decline)_terms$"))

    # Purchase conversation handler
    purchase_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_buy_coupon, pattern="^buy_")],
        states={
            WAITING_FOR_GIFT_CARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gift_card_code)]
        },
        fallbacks=[
            CallbackQueryHandler(cancel_purchase, pattern="^cancel_purchase$"),
            CommandHandler("cancel", cancel_conversation)
        ]
    )
    application.add_handler(purchase_conv)

    # Support conversation handler
    support_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_support, pattern="^support$")],
        states={
            WAITING_FOR_SUPPORT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support_message)]
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )
    application.add_handler(support_conv)

    # Add coupons conversation handler
    add_coupons_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_add_coupons, pattern="^add_coupons$")],
        states={
            WAITING_FOR_COUPON_CODES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_coupon_codes)]
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )
    application.add_handler(add_coupons_conv)

    # Broadcast conversation handler
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_send_announcement, pattern="^send_announcement$")],
        states={
            WAITING_FOR_BROADCAST_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_message)]
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )
    application.add_handler(broadcast_conv)

    # Admin callback handlers
    application.add_handler(CallbackQueryHandler(toggle_bot_status, pattern="^toggle_bot$"))
    application.add_handler(CallbackQueryHandler(handle_admin_verification, pattern="^(approve|reject)_"))
    application.add_handler(CallbackQueryHandler(handle_pending_verifications, pattern="^pending_verifications$"))

    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
