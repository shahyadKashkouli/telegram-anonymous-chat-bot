import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers.commands import start

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
from handlers.messages import handle_owner_message
from handlers.callbacks import handle_callback
from handlers.media import forward_media_to_owner
from handlers.auth import is_owner

# Log settings
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_message(update, context):
    """General message handling"""
    user = update.effective_user
    
    # Check media
    if (update.message.photo or update.message.video or 
        update.message.document or update.message.audio or 
        update.message.voice or update.message.sticker):
        
        if not is_owner(user.id):
            await forward_media_to_owner(update, context, user)
        else:
            await handle_owner_message(update, context)
    else:
        # Text message
        await handle_owner_message(update, context)

def main():
    """Main function to start the bot"""
    # Create Application
    application = Application.builder().token(API_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Start bot
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()