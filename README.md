# Telegram Coupon Payment Bot

A fully-featured Telegram bot for selling coupons with Amazon Gift Card payment verification.

## Features

### User Features
- ✅ Terms & Conditions agreement flow
- 📦 Real-time stock display
- 💳 Three coupon types: ₹1000 (₹300), ₹2000 (₹550), ₹4000 (₹900)
- 🎁 Amazon Gift Card payment
- ⏰ Payment timer and instructions
- 📞 Support messaging system
- 🔒 Privacy-first design (admin identity hidden)

### Admin Features
- 🎛️ **Bot ON/OFF Control** - Turn bot online/offline anytime
- ➕ **Add Coupons** - Bulk add coupon codes
- 🔍 **Payment Verification** - Approve/reject payments with one click
- 📊 **Statistics Dashboard** - Sales, revenue, stock, users
- 📢 **Broadcast Announcements** - Send messages to all users
- ✏️ **Custom Offline Message** - Edit the message shown when bot is offline
- 👥 **Multi-admin Support** - 2+ admins can manage the bot

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download

```bash
# If using git
git clone <repository-url>
cd BotTemp

# Or just download and extract the files
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your details:
   ```env
   BOT_TOKEN=your_bot_token_here
   ADMIN_IDS=640957500,second_admin_id
   ```

### Step 4: Run the Bot

```bash
python bot.py
```

## Configuration

### Getting Your Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the token (e.g., `1234567890:ABCdefGHI...`)
5. Paste it in `.env` file

### Getting Your User ID

1. Open Telegram and search for `@userinfobot`
2. Send any message
3. Copy your User ID (e.g., `640957500`)
4. Add it to `.env` file

### Adding Multiple Admins

In `.env`, separate admin IDs with commas:
```env
ADMIN_IDS=640957500,987654321
```

## Usage Guide

### For Admins

#### Starting the Bot

```bash
python bot.py
```

The bot starts in OFFLINE mode by default.

#### Admin Commands

1. **Open Admin Panel**: Send `/admin` to the bot

2. **Turn Bot ON/OFF**:
   - Click "🟢 Turn ON" to allow users to purchase
   - Click "🔴 Turn OFF" to close the store

3. **Add Coupons**:
   - Click "➕ Add Coupons"
   - Send codes in format: `TYPE:CODE`
   - Example:
     ```
     1000:ABCD-1234-EFGH
     2000:IJKL-5678-MNOP
     4000:QRST-9012-UVWX
     ```
   - Send multiple codes, one per line

4. **Verify Payments**:
   - You'll receive notifications when users submit payments
   - Click "✅ Approve" to deliver the coupon
   - Click "❌ Reject" if gift card is invalid

5. **View Pending Payments**:
   - Click "🔍 Pending Verifications"
   - See all payments waiting for approval

6. **Send Announcements**:
   - Click "📢 Send Announcement"
   - Type your message
   - It will be sent to all users

7. **View Statistics**:
   - Admin panel shows real-time stats
   - Total sales, revenue, pending payments, stock levels

### For Users

1. **Start**: Send `/start` to the bot
2. **Agree to Terms**: Click "✅ Agree"
3. **Browse Coupons**: See available stock and prices
4. **Purchase**: Click on a coupon to buy
5. **Payment**: Follow instructions to buy Amazon Gift Card
6. **Submit Code**: Send the 14-digit gift card code
7. **Wait**: Admin will verify and send your coupon
8. **Receive**: Get your coupon code instantly after approval

## File Structure

```
BotTemp/
├── bot.py                  # Main bot logic
├── config.py              # Configuration loader
├── database.py            # Database operations
├── requirements.txt       # Python dependencies
├── .env                   # Your configuration (not in git)
├── .env.example          # Example configuration
├── README.md             # This file
└── data/
    └── bot.db            # SQLite database (auto-created)
```

## Database

The bot uses SQLite database with the following tables:
- `users` - User information and terms agreement
- `coupons` - Coupon codes and availability
- `transactions` - Payment records
- `bot_settings` - Bot configuration (online/offline, messages)
- `support_messages` - User support requests

## Hosting Options

### Option 1: Local Computer (Testing)
- Run `python bot.py` on your computer
- Keep terminal open
- Good for testing only

### Option 2: VPS (Recommended for Production)
- DigitalOcean, Linode, Hetzner, etc.
- Install Python and dependencies
- Use `tmux` or `screen` to keep bot running
- Cost: ₹300-500/month

### Option 3: Free Hosting (Railway, Render, Fly.io)
- Good for starting
- May have limitations
- Follow their Python deployment guides

### Running 24/7 on VPS

```bash
# Install tmux
sudo apt install tmux

# Start tmux session
tmux new -s coupon-bot

# Run bot
python bot.py

# Detach: Press Ctrl+B, then D
# Reattach: tmux attach -t coupon-bot
```

## Customization

### Change Coupon Prices

Edit `bot.py`:
```python
COUPON_TYPES = {
    1000: 300,  # ₹1000 coupon for ₹300
    2000: 550,  # ₹2000 coupon for ₹550
    4000: 900   # ₹4000 coupon for ₹900
}
```

### Change Terms & Conditions

Edit `.env`:
```env
TERMS_AND_CONDITIONS=Your custom terms here...
```

### Change Offline Message

Edit `.env` or use admin panel "✏️ Edit Offline Message"

## Troubleshooting

### Bot doesn't respond
- Check if bot is running (`python bot.py`)
- Verify bot token in `.env`
- Check internet connection

### Users see "OUT OF STOCK"
- Bot is in OFFLINE mode
- Use `/admin` and click "🟢 Turn ON"
- Or add coupons first

### Can't verify payments
- Check admin ID in `.env`
- Make sure you're using `/admin` command
- Check bot logs for errors

### Database errors
- Delete `data/bot.db` to reset
- Restart bot to recreate database

## Security Notes

- ✅ Admin IDs are private and stored securely
- ✅ Users never see admin information
- ✅ Gift card codes are stored in encrypted database
- ⚠️ Keep `.env` file private (never share or commit to git)
- ⚠️ Regularly backup `data/bot.db` file

## Backup

### Backup Database
```bash
cp data/bot.db data/bot.db.backup
```

### Restore Database
```bash
cp data/bot.db.backup data/bot.db
```

## Support

For issues or questions:
1. Check this README
2. Review error messages in terminal
3. Check Telegram Bot API documentation

## License

Private use only.

## Credits

Built for coupon sales with Amazon Gift Card payment integration.
