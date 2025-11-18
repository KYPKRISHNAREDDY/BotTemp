# Contact Bot - Quick Setup Guide

Get your contact bot running in 5 minutes!

## Step 1: Create New Bot (2 minutes)

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Name your bot: `My Contact Bot` (or any name)
4. Username: `your_contact_bot` (must end with 'bot')
5. **Copy the token** - looks like: `1234567890:ABCdefGHI...`

## Step 2: Configure (1 minute)

1. Open `contact_bot_config.py`
2. Replace `YOUR_CONTACT_BOT_TOKEN_HERE` with your token
3. Your admin ID is already set: `640957500`
4. Save the file

**Example:**
```python
CONTACT_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
ADMIN_ID = 640957500
```

## Step 3: Run Bot (1 minute)

```bash
python contact_bot.py
```

You should see:
```
✅ Contact Bot is running...
Admin ID: 640957500

Waiting for messages...
```

## Step 4: Test It! (1 minute)

1. Find your bot on Telegram (search for the username you created)
2. Send `/start`
3. Type: "Hello, this is a test message"
4. **You'll receive a notification** with the message!
5. Reply using: `/reply YOUR_USER_ID Hi! Thanks for testing`

---

## How to Handle 10-20 Messages

### Scenario: 5 people message you

**Person 1 messages:** "Hi, I need help"

You receive:
```
💬 NEW MESSAGE

From: @person1
User ID: 111222333

Message:
Hi, I need help

━━━━━━━━━━━━━━━━━
Reply: /reply 111222333 Your message here
```

**You reply:**
```
/reply 111222333 Hi! How can I help you?
```

Person 1 receives:
```
📩 Reply from Support:

Hi! How can I help you?
```

---

**Person 2 messages:** "Thanks!"

You receive notification...

**You reply:**
```
/reply 222333444 You're welcome!
```

---

### View All Conversations

```
/conversations
```

Shows:
```
💬 Active Conversations (5)

1. @person1
   ID: 111222333
   Messages: 4 | Last: 2 mins ago

2. @person2
   ID: 222333444
   Messages: 2 | Last: 5 mins ago

3. @person3
   ID: 333444555
   Messages: 1 | Last: 10 mins ago

...

━━━━━━━━━━━━━━━━━
Use /history USER_ID to view conversation
Use /reply USER_ID message to reply
```

### View Message History

```
/history 111222333
```

Shows full conversation with that person.

---

## All Admin Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `/reply` | `/reply 123456789 Your message` | Reply to a user |
| `/conversations` | `/conversations` | See all active chats |
| `/history` | `/history 123456789` | View chat history with user |
| `/broadcast` | `/broadcast Hello everyone!` | Send to all users |
| `/stats` | `/stats` | View statistics |

---

## Tips for Managing Messages

### 1. Quick Reply Workflow
- Copy user ID from notification
- Type `/reply ` then paste ID
- Type your message
- Send!

### 2. Check Regularly
```
/conversations
```
See who messaged and when.

### 3. Review Before Replying
```
/history 123456789
```
See full conversation context.

### 4. Announcements
```
/broadcast We have new updates!
```
Send to everyone at once.

### 5. Keep Track
All messages saved in database - you won't lose anything!

---

## Example Session (Managing 5 People)

**7:00 PM** - Start bot
```bash
python contact_bot.py
```

**7:05 PM** - Person 1 messages
```
💬 NEW MESSAGE from @user1
```
You reply: `/reply 111 Hi there!`

**7:10 PM** - Person 2 messages
```
💬 NEW MESSAGE from @user2
```
You reply: `/reply 222 Thanks for contacting!`

**7:15 PM** - Person 3, 4, 5 message
```
💬 NEW MESSAGE from @user3
💬 NEW MESSAGE from @user4
💬 NEW MESSAGE from @user5
```

Check all: `/conversations`
```
Active Conversations (5)
1. @user1 (111) - 10 mins ago
2. @user2 (222) - 5 mins ago
3. @user3 (333) - just now
4. @user4 (444) - just now
5. @user5 (555) - just now
```

Reply to each:
```
/reply 333 Hello!
/reply 444 Got your message!
/reply 555 Thanks!
```

**7:30 PM** - Check stats
```
/stats
```

---

## Running Both Bots Together

You can run both bots simultaneously!

**Terminal 1:**
```bash
python bot.py
```
(Your coupon bot)

**Terminal 2:**
```bash
python contact_bot.py
```
(Your contact bot)

Or on VPS with tmux:
```bash
# Coupon bot
tmux new -s coupon
python bot.py
# Ctrl+B then D

# Contact bot
tmux new -s contact
python contact_bot.py
# Ctrl+B then D
```

---

## Privacy & Security

✅ Users never see your Telegram username
✅ Users don't know your phone number
✅ You stay anonymous - they only see "Support"
✅ All messages private between you and each user
✅ Database stored locally, secure

---

## Troubleshooting

**Bot doesn't start?**
- Check token in `contact_bot_config.py`
- Make sure you're using contact bot token (not coupon bot token)

**Don't receive notifications?**
- Check admin ID is correct: `640957500`
- Test with `/start` from your own account first

**Can't reply?**
- Copy user ID exactly from notification
- Use format: `/reply 123456789 message`
- Don't forget space after ID

**Messages not saving?**
- Check if `contact_data/` folder was created
- Bot creates it automatically

---

## What Makes This Bot Perfect for You

✅ **Simple** - Just copy user ID and reply
✅ **Fast** - Handle 10-20 messages in minutes
✅ **Private** - Your identity protected
✅ **History** - Never lose a conversation
✅ **Organized** - See all chats at a glance
✅ **Flexible** - Reply anytime, not just when they message

---

## Next Steps

1. ✅ Setup bot (5 minutes)
2. ✅ Test with yourself
3. ✅ Share bot link with others
4. ✅ Start receiving messages!

---

That's it! Your contact bot is ready. Start it now:

```bash
python contact_bot.py
```

And send `/start` to your bot on Telegram! 🚀
