import logging
import os
from dotenv import load_dotenv
from telegram import Update, User
from telegram.ext import ContextTypes
from .keyboards import get_reply_block_keyboard

# Load environment variables
load_dotenv()
OWNER_USER_ID = int(os.getenv('OWNER_USER_ID', 0))

logger = logging.getLogger(__name__)

async def forward_media_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User):
    """Send media to owner"""
    try:
        sender_info = f"👤 Sender: ID {user.id}"
        if user.username:
            sender_info += f" | @{user.username}"
        if user.first_name:
            sender_info += f" | {user.first_name}"
        if user.last_name:
            sender_info += f" {user.last_name}"
        
        reply_markup = get_reply_block_keyboard(user.id)
        
        # Check media type and send to owner
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            caption = update.message.caption or ""
            full_caption = f"{sender_info}\n\n{caption}" if caption else sender_info
            
            await context.bot.send_photo(
                chat_id=OWNER_USER_ID,
                photo=file_id,
                caption=full_caption,
                reply_markup=reply_markup
            )
            
        elif update.message.video:
            file_id = update.message.video.file_id
            caption = update.message.caption or ""
            full_caption = f"{sender_info}\n\n{caption}" if caption else sender_info
            
            await context.bot.send_video(
                chat_id=OWNER_USER_ID,
                video=file_id,
                caption=full_caption,
                reply_markup=reply_markup
            )
            
        elif update.message.document:
            file_id = update.message.document.file_id
            caption = update.message.caption or ""
            full_caption = f"{sender_info}\n\n{caption}" if caption else sender_info
            
            await context.bot.send_document(
                chat_id=OWNER_USER_ID,
                document=file_id,
                caption=full_caption,
                reply_markup=reply_markup
            )
            
        elif update.message.audio:
            file_id = update.message.audio.file_id
            caption = update.message.caption or ""
            full_caption = f"{sender_info}\n\n{caption}" if caption else sender_info
            
            await context.bot.send_audio(
                chat_id=OWNER_USER_ID,
                audio=file_id,
                caption=full_caption,
                reply_markup=reply_markup
            )
            
        elif update.message.voice:
            file_id = update.message.voice.file_id
            await context.bot.send_voice(
                chat_id=OWNER_USER_ID,
                voice=file_id,
                caption=sender_info,
                reply_markup=reply_markup
            )
            
        elif update.message.sticker:
            file_id = update.message.sticker.file_id
            await context.bot.send_sticker(
                chat_id=OWNER_USER_ID,
                sticker=file_id,
                reply_markup=reply_markup
            )
        
        await update.message.reply_text("✅ Your media was sent successfully!")
        
    except Exception as e:
        logger.error(f"Error sending media: {e}")
        await update.message.reply_text("❌ Error sending media. Please try again later.")
        
async def forward_media_from_owner(message, context: ContextTypes.DEFAULT_TYPE, target_user_id: int):
    """Send media from owner to user"""
    try:
        # Check media type and send to user
        if message.photo:
            file_id = message.photo[-1].file_id
            caption = message.caption or ""
            await context.bot.send_photo(chat_id=target_user_id, photo=file_id, caption=caption)
            
        elif message.video:
            file_id = message.video.file_id
            caption = message.caption or ""
            await context.bot.send_video(chat_id=target_user_id, video=file_id, caption=caption)
            
        elif message.document:
            file_id = message.document.file_id
            caption = message.caption or ""
            await context.bot.send_document(chat_id=target_user_id, document=file_id, caption=caption)
            
        elif message.audio:
            file_id = message.audio.file_id
            caption = message.caption or ""
            await context.bot.send_audio(chat_id=target_user_id, audio=file_id, caption=caption)
            
        elif message.voice:
            file_id = message.voice.file_id
            await context.bot.send_voice(chat_id=target_user_id, voice=file_id)
            
        elif message.sticker:
            file_id = message.sticker.file_id
            await context.bot.send_sticker(chat_id=target_user_id, sticker=file_id)
        
        return True
        
    except Exception as e:
        logger.error(f"Error forwarding media to user: {e}")
        return False