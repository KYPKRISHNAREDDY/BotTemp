# Quick Start Guide

Get your bot running in 5 minutes!

## Step 1: Get Bot Token (2 minutes)

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Enter bot name: `My Coupon Store`
5. Enter username: `my_coupon_store_bot` (must end with 'bot')
6. **Copy the token** - looks like: `1234567890:ABCdefGHI...`

## Step 2: Get Your User ID (1 minute)

1. Search for `@userinfobot` on Telegram
2. Send any message
3. **Copy your User ID** - looks like: `640957500`

## Step 3: Install & Configure (2 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# The bot is already configured with your token and ID!
# Check .env file if you need to add a second admin
```

Your `.env` is already set up with:
- ✅ Bot Token: `8284461494:AAGmAjqXlQVduJ_XQAMZ92ZpNyw2letJT-U`
- ✅ Admin ID: `640957500`

## Step 4: Add Coupons (Before Starting)

You mentioned you'll add coupons before starting. Once bot is running:

1. Send `/admin` to your bot
2. Click "➕ Add Coupons"
3. Send codes in this format:
   ```
   1000:YOUR-COUPON-CODE-1
   2000:YOUR-COUPON-CODE-2
   4000:YOUR-COUPON-CODE-3
   ```

## Step 5: Start Bot

```bash
python bot.py
```

You should see: `Bot started!`

## Step 6: Test It

1. Open Telegram and find your bot
2. Send `/start`
3. You should see Terms & Conditions
4. Click "✅ Agree"
5. You'll see the main menu (but stock will be empty until you add coupons)

## Step 7: Admin Panel

1. Send `/admin` to your bot
2. You should see the admin panel
3. Bot is **OFFLINE** by default

## Your Daily Workflow

### Before Selling (6:30 PM)

1. Send `/admin`
2. Click "➕ Add Coupons" (if needed)
3. Add your coupon codes
4. Click "🟢 Turn ON"
5. **Optional**: Click "📢 Send Announcement" to notify users

### During Sales (7:00 - 8:00 PM)

1. When users buy, you'll get notifications
2. Each notification shows:
   - User info
   - Gift card code they sent
   - Approve/Reject buttons
3. Verify the gift card code on Amazon
4. Click "✅ Approve" → User gets coupon instantly
5. Or click "❌ Reject" if code is invalid

### After Selling (8:00 PM)

1. Send `/admin`
2. Click "🔴 Turn OFF"
3. Bot shows "OUT OF STOCK" message
4. You can still verify pending payments at your convenience

## Quick Commands

- `/start` - Start bot / Main menu (users)
- `/admin` - Admin panel (admins only)
- `/cancel` - Cancel current operation

## Testing Payment Flow (Without Real Money)

1. Turn bot ON via `/admin`
2. Send `/start` (in bot chat)
3. Agree to terms
4. Click "Buy ₹1000 Coupon (₹300)"
5. You'll see payment instructions
6. Send any test code like: `TEST-1234-5678`
7. You'll get admin notification
8. Approve it to see the complete flow

## Common Issues

**Bot doesn't respond?**
- Make sure `python bot.py` is running
- Check terminal for errors

**Can't access admin panel?**
- Verify your User ID in `.env` is correct
- Use `/admin` command

**Users see "OUT OF STOCK"?**
- Bot is OFFLINE - turn it ON via admin panel
- Or you haven't added coupons yet

**No notifications when user pays?**
- Check bot is running
- Verify admin ID is correct

## Next Steps

1. **Customize Terms**: Edit `.env` file, change `TERMS_AND_CONDITIONS`
2. **Change Prices**: Edit `bot.py`, modify `COUPON_TYPES` dictionary
3. **Add Second Admin**: Edit `.env`, add to `ADMIN_IDS=640957500,second_id`
4. **Setup Hosting**: See README.md for VPS/cloud hosting options

## Need Help?

Check `README.md` for detailed documentation!

---

## Deployment to VPS (Optional)

Once you're ready for 24/7 operation:

```bash
# On VPS (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip tmux git

# Upload your files or git clone
# Install dependencies
pip3 install -r requirements.txt

# Run in background
tmux new -s bot
python3 bot.py

# Detach: Ctrl+B then D
# Bot keeps running even after you logout!
```

**That's it! Your bot is ready to sell coupons!** 🚀
