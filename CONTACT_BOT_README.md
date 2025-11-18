# Contact Bot - Anonymous Two-Way Communication

A simple Telegram bot that allows people to contact you anonymously with two-way messaging.

## Features

- ✅ Users can message you without knowing your identity
- ✅ You receive all messages with user info
- ✅ Reply to users easily with `/reply` command
- ✅ View active conversations
- ✅ Message history tracking
- ✅ Handle multiple users (10-20+)
- ✅ Privacy protected (your identity hidden)

## Quick Start

### 1. Get Bot Token from @BotFather

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Name your bot: `Contact Support Bot`
4. Username: `your_contact_support_bot` (must end with 'bot')
5. Copy the token

### 2. Setup

1. Edit `contact_bot_config.py`:
   - Add your bot token
   - Add your Telegram user ID (get from @userinfobot)

2. Install dependencies (if not already installed):
```bash
pip install python-telegram-bot python-dotenv
```

3. Run the bot:
```bash
python contact_bot.py
```

## How to Use

### For Users
1. Find your bot on Telegram
2. Send `/start`
3. Type any message
4. Receive confirmation
5. Wait for admin reply

### For You (Admin)

#### Receive Messages
When someone messages your bot, you'll get:
```
💬 NEW MESSAGE

From: @username (John Doe)
User ID: 123456789

Message:
"Hello, I need help with..."

Reply using: /reply 123456789 Your message here
```

#### Reply to Messages
```
/reply 123456789 Thank you for contacting! How can I help?
```

User receives:
```
📩 Reply from Support:

Thank you for contacting! How can I help?
```

#### View Active Conversations
```
/conversations
```

Shows list of people who messaged you.

#### View Message History
```
/history 123456789
```

Shows full conversation with that user.

## Commands

### User Commands
- `/start` - Start conversation

### Admin Commands
- `/reply USER_ID message` - Reply to a user
- `/conversations` - View all active conversations
- `/history USER_ID` - View conversation history
- `/broadcast message` - Send message to all users
- `/stats` - View statistics

## File Structure

```
BotTemp/
├── contact_bot.py              # Main contact bot
├── contact_bot_config.py       # Configuration
├── contact_bot_db.py          # Database for messages
└── contact_data/
    └── messages.db            # SQLite database
```

## Example Workflow

### Scenario: 3 people message you

**Person 1 (ID: 111):** "Hello!"
- You receive: "💬 NEW MESSAGE from @user1: Hello!"
- You reply: `/reply 111 Hi! How can I help?`

**Person 2 (ID: 222):** "I have a question"
- You receive: "💬 NEW MESSAGE from @user2: I have a question"
- You reply: `/reply 222 Sure, go ahead!`

**Person 3 (ID: 333):** "Thanks!"
- You receive: "💬 NEW MESSAGE from @user3: Thanks!"
- You reply: `/reply 333 You're welcome!`

**View all conversations:**
```
/conversations

Active Conversations (3):
1. @user1 (111) - Last: 2 mins ago
2. @user2 (222) - Last: 1 min ago
3. @user3 (333) - Last: 30 secs ago
```

## Tips for Managing 10-20 Messages

1. **Quick Replies:** Use `/reply` command immediately
2. **Check Regularly:** Run `/conversations` to see pending messages
3. **Organized:** Use `/history` to review past conversations
4. **Broadcast:** Use `/broadcast` for announcements to all users
5. **Copy User ID:** Copy-paste user ID from notification to reply faster

## Privacy & Security

- ✅ Users never see your Telegram username
- ✅ All replies show as "Support" or your bot name
- ✅ Your user ID is private
- ✅ Messages stored in local database only

## Deployment

Same as your coupon bot - run on VPS for 24/7 availability:
```bash
tmux new -s contact-bot
python contact_bot.py
# Ctrl+B then D to detach
```

## Troubleshooting

**Bot doesn't respond?**
- Check bot token in config
- Make sure bot is running

**Can't reply?**
- Check user ID is correct
- Use format: `/reply 123456789 message`

**No message notifications?**
- Verify your admin ID in config
- Check bot is running

---

This is a standalone bot separate from your coupon bot. Both can run simultaneously!
