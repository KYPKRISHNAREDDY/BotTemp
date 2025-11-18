# Admin Guide

Complete guide for managing your Telegram Coupon Bot.

## Admin Panel Overview

Send `/admin` to access the admin panel. You'll see:

```
🎛️ ADMIN PANEL

Bot Status: 🔴 OFFLINE

📊 Statistics:
• Total Sales: 0
• Total Revenue: ₹0
• Pending Verifications: 0
• Total Users: 0

📦 Stock:
• ₹1000: 0 available
• ₹2000: 0 available
• ₹4000: 0 available

[🟢 Turn ON]
[➕ Add Coupons] [📊 View Stats]
[🔍 Pending Verifications] [📢 Send Announcement]
[✏️ Edit Offline Message]
```

## Features Explained

### 1. Bot ON/OFF Control

**Purpose**: Control when users can purchase coupons.

**Usage**:
- Click "🟢 Turn ON" to start selling
- Click "🔴 Turn OFF" to stop selling

**When ON**:
- Users see available stock
- Users can make purchases
- You receive payment notifications

**When OFF**:
- Users see: "⏰ Currently OUT OF STOCK"
- Users cannot purchase
- Your custom offline message is shown

**Your Workflow**:
- Keep bot OFF by default
- Turn ON when you're ready to sell (e.g., 7-8 PM)
- Turn OFF when done for the day

---

### 2. Add Coupons

**Purpose**: Add coupon codes to your inventory.

**Steps**:
1. Click "➕ Add Coupons"
2. Bot asks for codes in format: `TYPE:CODE`
3. Send your codes (one per line or all together)

**Format Examples**:

Single code:
```
1000:ABCD-1234-EFGH-5678
```

Multiple codes:
```
1000:ABCD-1234-EFGH
1000:IJKL-5678-MNOP
2000:QRST-9012-UVWX
2000:YZAB-3456-CDEF
4000:GHIJ-7890-KLMN
```

**Coupon Types**:
- `1000` = ₹1000 coupon (sells for ₹300)
- `2000` = ₹2000 coupon (sells for ₹550)
- `4000` = ₹4000 coupon (sells for ₹900)

**Tips**:
- Prepare codes in a text file beforehand
- Copy-paste all at once
- Bot will tell you how many were added successfully
- Duplicate codes are automatically rejected

---

### 3. Payment Verification

**How it works**:

1. **User Makes Purchase**:
   - User selects a coupon
   - Sees payment instructions
   - Buys Amazon Gift Card
   - Sends gift card code to bot

2. **You Get Notification**:
   ```
   🔔 NEW PAYMENT RECEIVED

   👤 User: @username
   🆔 User ID: 123456789
   💳 Product: ₹1000 Coupon
   💰 Price: ₹300
   🎁 Gift Card Code: ABCD-EFGH12-JKLM

   📋 Transaction ID: 1

   [✅ Approve] [❌ Reject]
   ```

3. **Verify Gift Card**:
   - Go to Amazon.in
   - Account → Gift Cards → Redeem a Gift Card
   - Enter the code
   - Check if it's valid and matches amount

4. **Take Action**:
   - **If Valid**: Click "✅ Approve"
     - User gets coupon code instantly
     - Code is marked as sold in database
     - Transaction recorded

   - **If Invalid**: Click "❌ Reject"
     - User gets rejection message
     - Can contact support
     - No coupon is delivered

**Verification Tips**:
- Verify within 5-10 minutes for good customer experience
- Check gift card validity before approving
- Don't complete Amazon redemption if you just want to verify
- Keep track of approved transactions

---

### 4. Pending Verifications

**Purpose**: See all payments waiting for approval.

**Usage**:
1. Click "🔍 Pending Verifications"
2. See list of all unverified payments

**Shows**:
- User info
- Coupon type and price
- Gift card code
- Transaction ID

**When to use**:
- Check if you missed any notifications
- Review queue before starting verification session
- See how many payments need attention

---

### 5. Send Announcement

**Purpose**: Broadcast message to all users.

**Usage**:
1. Click "📢 Send Announcement"
2. Type your message
3. Bot sends to all users who have used the bot

**Use cases**:
- "🟢 We're LIVE NOW! Stock available for 1 hour!"
- "📦 New stock added! Grab your coupons!"
- "⏰ Last chance! Closing in 15 minutes"
- "📢 Special offer: Buy 2 get 10% off!"

**Example Message**:
```
🔥 FLASH SALE ALERT!

📦 Fresh stock just added:
• ₹1000 Coupons - LIMITED
• ₹2000 Coupons - Available
• ₹4000 Coupons - Few left

⏰ Sale ends at 8:00 PM

Hurry! /start
```

**Tips**:
- Send announcements when turning bot ON
- Alert users when stock is back
- Create urgency with time limits
- Keep messages short and clear

---

### 6. View Statistics

**Auto-shown** in admin panel. Includes:

**Sales Stats**:
- Total Sales: Number of completed transactions
- Total Revenue: Total money earned
- Pending Verifications: Payments waiting for approval

**Stock Stats**:
- Available count for each coupon type
- Updated in real-time

**User Stats**:
- Total users who agreed to terms
- Your customer base size

**Usage**:
- Track daily sales
- Monitor inventory levels
- Know when to restock
- Calculate profits

---

### 7. Edit Offline Message

**Purpose**: Customize message shown when bot is offline.

**Default Message**:
```
⏰ Currently OUT OF STOCK

📦 New stock arrives: Evening 6:30 PM - 7:30 PM

Check back later!
```

**How to change**:
1. Edit `.env` file
2. Modify `OFFLINE_MESSAGE=` line
3. Restart bot

**Example Custom Messages**:

Weekend only:
```
OFFLINE_MESSAGE=🔴 Store Closed\n\n📅 Next sale: Saturday 8 PM\n\nFollow @yourchannel for updates!
```

Flash sales:
```
OFFLINE_MESSAGE=⏰ Sale Starts Soon!\n\n🕐 Next session: Today at 7 PM\n\nSet your reminder!
```

---

## Daily Workflow

### Morning (Preparation)
1. Collect coupon codes from your source
2. Prepare them in format: `TYPE:CODE`
3. Have them ready in a text file

### 6:30 PM (Setup)
1. Send `/admin`
2. Click "➕ Add Coupons"
3. Paste all codes
4. Verify stock count in admin panel
5. Click "🟢 Turn ON"
6. Click "📢 Send Announcement" (optional)

### 7:00 - 8:00 PM (Active Sales)
1. Monitor notifications
2. Verify each gift card code
3. Approve or reject quickly
4. Keep admin panel open for stats

### 8:00 PM (Closing)
1. Send `/admin`
2. Click "🔴 Turn OFF"
3. Check "🔍 Pending Verifications"
4. Complete any remaining verifications
5. Review daily stats

### Anytime (Support)
- You'll get support messages from users
- Reply using "📢 Send Announcement" or handle manually

---

## Tips for Success

### Inventory Management
- ✅ Add coupons before turning bot ON
- ✅ Have backup stock ready
- ✅ Monitor stock levels during sales
- ✅ Turn OFF when stock depletes

### Customer Service
- ✅ Verify payments within 10 minutes
- ✅ Be online during active hours
- ✅ Respond to support messages
- ✅ Be fair with rejections

### Security
- ✅ Keep bot token private
- ✅ Don't share admin credentials
- ✅ Verify gift cards carefully
- ✅ Watch for fraud patterns

### Marketing
- ✅ Use announcements to create urgency
- ✅ Be consistent with timing
- ✅ Build trust with quick service
- ✅ Encourage word-of-mouth

---

## Advanced Features

### Multiple Admins

Add second admin in `.env`:
```env
ADMIN_IDS=640957500,987654321
```

Both admins can:
- Access `/admin` panel
- Verify payments
- Add coupons
- Send announcements

### Grace Period

Users have **10-minute grace period** after your closing time:
- If they start payment at 7:55 PM
- They can complete until 8:05 PM
- You can verify later at your convenience

### Support System

Users can click "📞 Contact Support":
- They type their message
- You receive it as notification
- Reply using announcements or manually
- Their identity is shown to you, yours is hidden to them

---

## Troubleshooting

### No payment notifications?
- Check bot is running (`python bot.py`)
- Verify your admin ID in `.env`
- Test by making a purchase yourself

### Can't approve payments?
- Check stock availability
- Make sure coupon type exists in database
- Restart bot if issue persists

### Users complain bot is offline?
- Check admin panel - is it ON?
- Add coupons if stock is zero
- Test with `/start` yourself

### Lost transaction?
- Check "🔍 Pending Verifications"
- Check terminal logs
- Look in `data/bot.db` database

---

## Database Backup

**Important**: Backup your database regularly!

```bash
# Backup
cp data/bot.db backups/bot-$(date +%Y%m%d).db

# Restore
cp backups/bot-20240315.db data/bot.db
```

Schedule daily backups on your server.

---

## Support & Updates

For issues:
1. Check terminal for error messages
2. Review this guide
3. Check README.md
4. Test in a fresh environment

Good luck with your sales! 🚀
