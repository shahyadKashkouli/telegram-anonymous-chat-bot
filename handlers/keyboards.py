from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_owner_keyboard():
    """Owner keyboard"""
    keyboard = [
        [KeyboardButton("📩 Send to specific user"), KeyboardButton("📨 Send broadcast message")],
        [KeyboardButton("🚫 Block list"), KeyboardButton("👥 User list")],
        [KeyboardButton("📊 System statistics")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_join_channel_keyboard(channel_username):
    """Channel membership keyboard"""
    keyboard = [
        [InlineKeyboardButton("🔗 Join channel", url=f"https://t.me/{channel_username[1:]}")],
        [InlineKeyboardButton("✅ I joined", callback_data="check_membership")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_reply_block_keyboard(user_id):
    """Reply and block keyboard"""
    keyboard = [
        [InlineKeyboardButton("📨 Reply", callback_data=f"reply_{user_id}"),
         InlineKeyboardButton("🚫 Block", callback_data=f"block_{user_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_reply_keyboard():
    """Cancel reply keyboard"""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("❌ Cancel reply")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_confirmation_keyboard():
    """Send confirmation keyboard"""
    keyboard = [
        [KeyboardButton("✅ Yes, send it"), KeyboardButton("✖️ Cancel sending")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)