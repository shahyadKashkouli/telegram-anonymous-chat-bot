import logging
import os
from dotenv import load_dotenv
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from .keyboards import get_join_channel_keyboard

# Load environment variables
load_dotenv()
force_chanel = os.getenv('FORCE_CHANNEL')

logger = logging.getLogger(__name__)

async def check_channel_membership(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """Check user membership in mandatory channel"""
    try:
        member = await context.bot.get_chat_member(chat_id=force_chanel, user_id=user_id)
        is_member = member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
        logger.info(f"Checking membership for user {user_id}, result: {is_member}")
        return is_member
    except Exception as e:
        logger.error(f"Error checking channel membership for user {user_id}: {e}")
        return False

async def send_join_channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send channel membership message"""
    reply_markup = get_join_channel_keyboard(force_chanel)
    
    message_text = f"""
🔒 To use the bot, you must first join our channel:

📢 Channel: {force_chanel}

✅ After joining, click the "I Joined" button.
    """
    
    await update.message.reply_text(message_text, reply_markup=reply_markup)