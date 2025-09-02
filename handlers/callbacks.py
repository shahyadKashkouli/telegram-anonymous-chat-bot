import logging
from telegram import Update
from telegram.ext import ContextTypes
from database import db_manager
from .auth import is_owner
from .channel import check_channel_membership
from .keyboards import get_cancel_reply_keyboard

logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    data = query.data
    
    # Check channel membership
    if data == "check_membership":
        user_id = query.from_user.id
        is_member = await check_channel_membership(context, user_id)
        
        if is_member:
            await query.answer()
            user_name = query.from_user.first_name
            await query.edit_message_text(
                f"🌟 Welcome to the anonymous bot, {user_name}!\n\n🔹 The bot owner will respond to your messages\n🔹 Please avoid sending spam messages\n\n✨ Send your message..."
            )
        else:
            await query.answer("❌ You haven't joined the channel yet! Please join the channel first.", show_alert=True)
        return
    
    # Other callbacks are only for owner
    await query.answer()
    
    if not is_owner(query.from_user.id):
        await query.message.reply_text("❌ Access denied.")
        return
    
    if data.startswith('block_'):
        await handle_block_callback(query, context, data)
    elif data.startswith('unblock_'):
        await handle_unblock_callback(query, context, data)
    elif data.startswith('reply_'):
        await handle_reply_callback(query, context, data)

async def handle_block_callback(query, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle user blocking"""
    user_id = int(data.split('_')[1])
    await db_manager.block_user(user_id)
    
    # Get blocked user information
    username, first_name, last_name = await db_manager.get_user_info(user_id)
    user_info = f"🆔 {user_id}"
    if username:
        user_info += f" | @{username}"
    if first_name:
        user_info += f" | {first_name}"
    if last_name:
        user_info += f" {last_name}"
    
    await query.edit_message_text(f"✅ User successfully blocked:\n{user_info}")
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ You have been blocked by the bot owner and cannot send messages."
        )
    except:
        pass

async def handle_unblock_callback(query, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle user unblocking"""
    user_id = int(data.split('_')[1])
    await db_manager.unblock_user(user_id)
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="🎉 You have been unblocked by the owner! You can now send messages."
        )
    except:
        pass
    
    await query.edit_message_text(f"✅ User {user_id} successfully unblocked and notification sent.")

async def handle_reply_callback(query, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle reply to user"""
    user_id = int(data.split('_')[1])
    context.user_data['replying_to'] = user_id
    
    # Get information of user being replied to
    username, first_name, last_name = await db_manager.get_user_info(user_id)
    target_info = f"🆔 {user_id}"
    if username:
        target_info += f" | @{username}"
    if first_name:
        target_info += f" | {first_name}"
    if last_name:
        target_info += f" {last_name}"
    
    cancel_keyboard = get_cancel_reply_keyboard()
    
    await query.message.reply_text(
        f"📝 Replying to user:\n{target_info}\n\nPlease enter your reply:",
        reply_markup=cancel_keyboard
    )