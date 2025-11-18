"""
Contact Bot - Anonymous Two-Way Communication
Allows users to contact admin with message forwarding and reply functionality
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode
from datetime import datetime
import contact_bot_config as config
from contact_bot_db import db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == config.ADMIN_ID


def format_user_display(username: str = None, first_name: str = None, last_name: str = None) -> str:
    """Format user display name"""
    if username:
        return f"@{username}"
    name_parts = []
    if first_name:
        name_parts.append(first_name)
    if last_name:
        name_parts.append(last_name)
    return " ".join(name_parts) if name_parts else "Anonymous User"


def format_time_ago(timestamp_str: str) -> str:
    """Format timestamp as 'X mins/hours ago'"""
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        now = datetime.now()
        delta = now - timestamp

        if delta.seconds < 60:
            return "just now"
        elif delta.seconds < 3600:
            mins = delta.seconds // 60
            return f"{mins} min{'s' if mins != 1 else ''} ago"
        elif delta.seconds < 86400:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = delta.days
            return f"{days} day{'s' if days != 1 else ''} ago"
    except:
        return timestamp_str


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user

    # Add user to database
    db.add_user(user.id, user.username, user.first_name, user.last_name)

    # If admin, show admin commands
    if is_admin(user.id):
        admin_msg = "🛠️ *Admin Mode*\n\n"
        admin_msg += "Available commands:\n"
        admin_msg += "• `/reply USER_ID message` - Reply to a user\n"
        admin_msg += "• `/conversations` - View active conversations\n"
        admin_msg += "• `/history USER_ID` - View conversation history\n"
        admin_msg += "• `/broadcast message` - Send to all users\n"
        admin_msg += "• `/stats` - View statistics\n\n"
        admin_msg += "You'll receive notifications when users message you."

        await update.message.reply_text(admin_msg, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(config.WELCOME_MESSAGE)


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages from users"""
    user = update.effective_user
    message_text = update.message.text

    # Ignore if admin is sending message (they should use /reply)
    if is_admin(user.id):
        return

    # Add user to database
    db.add_user(user.id, user.username, user.first_name, user.last_name)

    # Save message to database
    db.add_message(user.id, message_text, from_admin=False)

    # Confirm to user
    await update.message.reply_text(
        "✅ *Message received!*\n\n"
        "Thank you for contacting us. We'll get back to you soon!",
        parse_mode=ParseMode.MARKDOWN
    )

    # Notify admin
    user_display = format_user_display(user.username, user.first_name, user.last_name)

    admin_notification = f"💬 *NEW MESSAGE*\n\n"
    admin_notification += f"From: {user_display}\n"
    admin_notification += f"User ID: `{user.id}`\n\n"
    admin_notification += f"Message:\n{message_text}\n\n"
    admin_notification += f"━━━━━━━━━━━━━━━━━\n"
    admin_notification += f"Reply: `/reply {user.id} Your message here`"

    try:
        await context.bot.send_message(
            chat_id=config.ADMIN_ID,
            text=admin_notification,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")


async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reply command from admin"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ This command is only for admins.")
        return

    # Parse command: /reply USER_ID message
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ *Invalid format*\n\n"
            "Usage: `/reply USER_ID Your message here`\n\n"
            "Example: `/reply 123456789 Thank you for contacting!`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    try:
        user_id = int(context.args[0])
        reply_message = " ".join(context.args[1:])

        # Check if user exists
        user_info = db.get_user_info(user_id)
        if not user_info:
            await update.message.reply_text(
                f"❌ User ID `{user_id}` not found in database.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Send message to user
        user_message = config.REPLY_PREFIX + reply_message

        await context.bot.send_message(
            chat_id=user_id,
            text=user_message
        )

        # Save to database
        db.add_message(user_id, reply_message, from_admin=True)

        # Confirm to admin
        user_display = format_user_display(
            user_info['username'],
            user_info['first_name'],
            user_info['last_name']
        )

        await update.message.reply_text(
            f"✅ *Reply sent to {user_display}*\n\n"
            f"Your message:\n{reply_message}",
            parse_mode=ParseMode.MARKDOWN
        )

    except ValueError:
        await update.message.reply_text(
            "❌ Invalid user ID. It must be a number.\n\n"
            "Example: `/reply 123456789 Your message`",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error sending reply: {e}")
        await update.message.reply_text(
            f"❌ Failed to send reply: {str(e)}",
            parse_mode=ParseMode.MARKDOWN
        )


async def conversations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show active conversations"""
    if not is_admin(update.effective_user.id):
        return

    conversations = db.get_active_conversations(limit=30)

    if not conversations:
        await update.message.reply_text("📭 No conversations yet.")
        return

    message = f"💬 *Active Conversations ({len(conversations)})*\n\n"

    for i, conv in enumerate(conversations[:20], 1):  # Show first 20
        user_display = format_user_display(
            conv['username'],
            conv['first_name'],
            conv['last_name']
        )
        time_ago = format_time_ago(conv['last_contact'])

        message += f"{i}. {user_display}\n"
        message += f"   ID: `{conv['user_id']}`\n"
        message += f"   Messages: {conv['message_count']} | Last: {time_ago}\n\n"

    if len(conversations) > 20:
        message += f"...and {len(conversations) - 20} more\n\n"

    message += "━━━━━━━━━━━━━━━━━\n"
    message += "Use `/history USER_ID` to view conversation\n"
    message += "Use `/reply USER_ID message` to reply"

    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show conversation history with a user"""
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ Usage: `/history USER_ID`\n\n"
            "Example: `/history 123456789`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    try:
        user_id = int(context.args[0])

        # Get user info
        user_info = db.get_user_info(user_id)
        if not user_info:
            await update.message.reply_text(
                f"❌ User ID `{user_id}` not found.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Get conversation history
        history = db.get_conversation_history(user_id, limit=30)

        if not history:
            await update.message.reply_text(
                f"📭 No messages from this user yet."
            )
            return

        user_display = format_user_display(
            user_info['username'],
            user_info['first_name'],
            user_info['last_name']
        )

        message = f"📜 *Conversation with {user_display}*\n"
        message += f"User ID: `{user_id}`\n\n"
        message += "━━━━━━━━━━━━━━━━━\n\n"

        for msg in history[-15:]:  # Show last 15 messages
            sender = "👤 You" if msg['from_admin'] else f"💬 {user_display}"
            timestamp = format_time_ago(msg['timestamp'])
            message += f"{sender} ({timestamp}):\n"
            message += f"{msg['text']}\n\n"

        if len(history) > 15:
            message += f"_({len(history) - 15} earlier messages not shown)_\n\n"

        message += "━━━━━━━━━━━━━━━━━\n"
        message += f"Reply: `/reply {user_id} Your message`"

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    except ValueError:
        await update.message.reply_text(
            "❌ Invalid user ID. Must be a number.",
            parse_mode=ParseMode.MARKDOWN
        )


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users"""
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 1:
        await update.message.reply_text(
            "❌ Usage: `/broadcast Your message here`\n\n"
            "Example: `/broadcast Hello everyone! We have new updates.`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    broadcast_message = " ".join(context.args)
    user_ids = db.get_all_user_ids()

    # Remove admin from broadcast list
    user_ids = [uid for uid in user_ids if uid != config.ADMIN_ID]

    if not user_ids:
        await update.message.reply_text("📭 No users to broadcast to.")
        return

    status_msg = await update.message.reply_text(
        f"📤 Broadcasting to {len(user_ids)} users..."
    )

    sent = 0
    failed = 0

    for user_id in user_ids:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 *Announcement*\n\n{broadcast_message}",
                parse_mode=ParseMode.MARKDOWN
            )
            sent += 1
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")
            failed += 1

    await status_msg.edit_text(
        f"✅ *Broadcast Complete*\n\n"
        f"Sent: {sent}\n"
        f"Failed: {failed}",
        parse_mode=ParseMode.MARKDOWN
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    if not is_admin(update.effective_user.id):
        return

    total_users = db.get_total_users()
    total_messages = db.get_total_messages()
    recent_conversations = db.get_active_conversations(limit=5)

    message = "📊 *Contact Bot Statistics*\n\n"
    message += f"👥 Total Users: {total_users}\n"
    message += f"💬 Total Messages: {total_messages}\n\n"

    if recent_conversations:
        message += "*Recent Conversations:*\n"
        for conv in recent_conversations[:5]:
            user_display = format_user_display(
                conv['username'],
                conv['first_name'],
                conv['last_name']
            )
            time_ago = format_time_ago(conv['last_contact'])
            message += f"• {user_display} - {time_ago}\n"

    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


def main():
    """Start the contact bot"""
    # Create application
    application = Application.builder().token(config.CONTACT_BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reply", reply_command))
    application.add_handler(CommandHandler("conversations", conversations_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # Message handler (for user messages)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

    # Start bot
    logger.info("Contact Bot started!")
    print("✅ Contact Bot is running...")
    print(f"Admin ID: {config.ADMIN_ID}")
    print("\nWaiting for messages...\n")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
