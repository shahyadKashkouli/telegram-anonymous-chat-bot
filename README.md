# Telegram Anonymous Chat Bot - Privacy-Focused Communication

A powerful Telegram bot that enables users to send messages to administrators while keeping the administrator's identity protected. This bot provides administrators with a secure management panel to handle user messages and media while maintaining admin anonymity.

## 🌟 Features

- 🔒 **Admin Identity Protection**: Administrators remain completely anonymous to users
- 📱 **Multi-Media Support**: Handle user text, photos, videos, documents, and voice messages
- 🛡️ **Admin Management Panel**: Comprehensive interface for administrators to manage user communications
- 👥 **User Management**: View and manage users with full administrative control
- 📢 **Admin Broadcast System**: Send announcements to all users while staying anonymous
- 🔗 **Channel Integration**: Optional channel membership requirement for enhanced security
- 💾 **Efficient Data Storage**: SQLite database storing user data and message history

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))
- Your Telegram User ID

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shahyadKashkouli/telegram-anonymous-bot.git
   cd telegram-anonymous-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Your bot token from @BotFather
   API_TOKEN=your_bot_token_here
   
   # Your Telegram user ID (you can get it from @userinfobot)
   OWNER_USER_ID=your_user_id_here
   
   # Optional: Channel username for forced subscription
   FORCE_CHANNEL=@your_channel_username
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## 📋 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|-----------|
| `API_TOKEN` | Your Telegram bot token from @BotFather | ✅ Yes |
| `OWNER_USER_ID` | Your Telegram user ID (admin) | ✅ Yes |
| `FORCE_CHANNEL` | Channel username for forced subscription | ❌ Optional |

### Getting Your User ID

1. Start a chat with [@userinfobot](https://t.me/userinfobot)
2. Send any message
3. Copy your user ID from the response

## 🎮 Usage

### For Users

1. **Start the bot** by sending `/start`
2. **Send messages** - text, photos, videos, documents, or voice messages
3. **Receive admin responses** - get replies from anonymous administrators
4. **No registration required** - instant communication with admin

### For Administrators

1. **Access admin panel** with `/admin` command (owner only)
2. **Manage user messages** - view and respond to user messages anonymously
3. **User management** - view user list, block/unblock users
4. **Broadcast system** - send messages to all users while staying anonymous
5. **System monitoring** - track statistics and bot performance
6. **Identity protection** - maintain complete anonymity from users

## 🏗️ Project Structure

```
telegram-anonymous-bot/
├── handlers/
│   ├── __init__.py
│   ├── auth.py          # Authentication and authorization
│   ├── callbacks.py     # Inline keyboard callbacks
│   ├── channel.py       # Channel membership verification
│   ├── commands.py      # Bot commands (/start, etc.)
│   ├── keyboards.py     # Keyboard layouts
│   ├── media.py         # Media message handling
│   └── messages.py      # Text message handling
├── database.py          # Database operations
├── main.py             # Main bot application
├── states.py           # Bot state management
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
└── README.md          # This file
```

## 🛠️ Dependencies

- `python-telegram-bot==21.0.1` - Telegram Bot API wrapper
- `python-dotenv==1.0.1` - Environment variable management

## 🔒 Security Features

- **🔐 Admin Identity Protection**: Administrators remain completely anonymous to users
- **🛡️ Secure Communication**: All messages are handled securely within Telegram's infrastructure
- **👨‍💼 Admin Authentication**: Only authorized administrators can access the management panel
- **✅ Input Validation**: All user inputs are validated and sanitized for security
- **💾 Database Security**: SQLite database with secure data storage
- **⚡ Rate Limiting**: Built-in protection against spam and abuse
- **🔄 Session Management**: Secure handling of user sessions and states
- **📊 User Tracking**: Full visibility of user interactions for administrative purposes
- **🚫 User Management**: Complete control over user access and permissions

## 📊 Database Schema

The bot uses SQLite database with the following tables:

- **users**: Stores user information, join dates, and block status
- **messages**: Stores message history and metadata

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/shahyadKashkouli/telegram-anonymous-bot/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your setup and the issue

## 🔄 Updates

To update the bot to the latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## ⚠️ Important Notes

- Keep your bot token secure and never share it publicly
- Regularly backup your database file (`anonymous_bot.db`)
- Monitor bot logs for any unusual activity
- Ensure your server has sufficient resources for your user base

---

**Made with ❤️ for the Telegram community**