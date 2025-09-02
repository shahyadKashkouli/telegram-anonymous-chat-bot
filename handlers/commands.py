from telegram import Update
from telegram.ext import ContextTypes
from database import db_manager
from .auth import is_owner
from .keyboards import get_owner_keyboard
from .channel import check_channel_membership, send_join_channel_message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user
    await db_manager.add_user(user.id, user.username, user.first_name, user.last_name)
    
    if is_owner(user.id):
        welcome_text = f"""
        👑 Welcome to the management panel, dear owner!

        🔹 You have full access to all features
        🔹 You can manage users
        🔹 View system statistics

        Use the keyboard below:
        """
        await update.message.reply_text(welcome_text, reply_markup=get_owner_keyboard())
    else:
        # Check channel membership
        is_member = await check_channel_membership(context, user.id)
        if not is_member:
            await send_join_channel_message(update, context)
            return
        
        welcome_text = f"""
        🌟 Welcome to the anonymous bot, {user.first_name}!

        🔹 You can send messages anonymously
        🔹 The bot owner will respond to your messages
        🔹 Please avoid sending spam messages

        ✨ Send your message...
        """
        await update.message.reply_text(welcome_text)