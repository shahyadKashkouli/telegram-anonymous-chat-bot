import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes
from database import db_manager

# Load environment variables
load_dotenv()
OWNER_USER_ID = int(os.getenv('OWNER_USER_ID', 0))
from .auth import is_owner
from .keyboards import get_owner_keyboard, get_reply_block_keyboard, get_confirmation_keyboard
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

async def ask_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, target_user_id: int, message_type: str):
    """Request confirmation for sending message"""
    # Get target user information
    username, first_name, last_name = await db_manager.get_user_info(target_user_id)
    target_info = f"🆔 {target_user_id}"
    if username:
        target_info += f" | @{username}"
    if first_name:
        target_info += f" | {first_name}"
    if last_name:
        target_info += f" {last_name}"
    
    # Save message in context for later sending
    context.user_data['pending_message'] = {
        'target_user_id': target_user_id,
        'message': update.message,
        'message_type': message_type
    }
    
    confirmation_text = f"""
📤 Are you sure you want to send this {message_type}?

👤 Destination: {target_info}

✅ Select "Yes, send it" to confirm
❌ Select "Cancel sending" to cancel
    """
    
    await update.message.reply_text(
        confirmation_text,
        reply_markup=get_confirmation_keyboard()
    )

async def handle_owner_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle owner messages"""
    user = update.effective_user
    
    if not is_owner(user.id):
        # Handle regular user messages
        await handle_user_message(update, context)
        return
    
    # Handle owner menu buttons
    if update.message.text:
        message_text = update.message.text
        
        # Handle confirmation buttons
        if 'pending_message' in context.user_data:
            if message_text == "✅ Yes, send it":
                await send_pending_message(update, context)
                return
            elif message_text == "✖️ Cancel sending":
                await cancel_pending_message(update, context)
                return
        
        # Handle replying_to state
        if 'replying_to' in context.user_data:
            if message_text in ["❌ Cancel", "❌ Cancel reply"]:
                context.user_data.pop('replying_to', None)
                await update.message.reply_text("🚫 Reply cancelled.", reply_markup=get_owner_keyboard())
                return
            else:
                target_user_id = context.user_data['replying_to']
                await ask_confirmation(update, context, target_user_id, "reply")
                return
        
        # Handle sending_to_user state
        if 'sending_to_user' in context.user_data:
            if message_text == "❌ Cancel":
                context.user_data.pop('sending_to_user', None)
                await update.message.reply_text("🚫 Send cancelled.", reply_markup=get_owner_keyboard())
                return
            else:
                target_user_id = context.user_data['sending_to_user']
                await ask_confirmation(update, context, target_user_id, "message")
                return
        
        # Handle main menu buttons
        if message_text == "📩 Send to specific user":
            await update.message.reply_text(
                "🆔 Please enter the user ID or username:\n\n" +
                "Example: 123456789 or @username",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("❌ Cancel")]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
            )
            context.user_data['waiting_for_user_id'] = True
            return
            
        elif message_text == "📨 Send broadcast message":
            await update.message.reply_text(
                "📢 Enter your broadcast message:",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("❌ Cancel")]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
            )
            context.user_data['broadcast_mode'] = True
            return
            
        elif message_text == "🚫 Block list":
            blocked_users = await db_manager.get_blocked_users()
            if not blocked_users:
                await update.message.reply_text("📋 No blocked users found.")
            else:
                blocked_list = "🚫 Blocked Users List:\n\n"
                for user_id, username, first_name, last_name in blocked_users:
                    user_info = f"🆔 {user_id}"
                    if username:
                        user_info += f" | @{username}"
                    if first_name:
                        user_info += f" | {first_name}"
                    if last_name:
                        user_info += f" {last_name}"
                    blocked_list += f"• {user_info}\n"
                
                # Add unblock buttons
                keyboard = []
                for user_id, _, _, _ in blocked_users[:10]:  # Limited to 10 users
                    keyboard.append([InlineKeyboardButton(f"🔓 Unblock {user_id}", callback_data=f"unblock_{user_id}")])
                
                reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                await update.message.reply_text(blocked_list, reply_markup=reply_markup)
            return
            
        elif message_text == "👥 User list":
            all_users = await db_manager.get_all_users()
            if not all_users:
                await update.message.reply_text("📋 No users registered.")
            else:
                users_list = "👥 All Users List:\n\n"
                for user_id, username, first_name, last_name, _, is_blocked in all_users[:20]:  # Limited to 20 users
                    user_info = f"🆔 {user_id}"
                    if username:
                        user_info += f" | @{username}"
                    if first_name:
                        user_info += f" | {first_name}"
                    if last_name:
                        user_info += f" {last_name}"
                    
                    status = "🚫 Blocked" if is_blocked else "✅ Active"
                    users_list += f"• {user_info} - {status}\n"
                
                await update.message.reply_text(users_list)  # Without parse_mode
            return
            
        elif message_text == "📊 System statistics":
            stats = await db_manager.get_stats()
            stats_text = f"""📊 System Statistics:

👥 Total Users: {stats['total_users']}
✅ Active Users: {stats['active_users']}
🚫 Blocked Users: {stats['blocked_users']}
💬 Total Messages: {stats['total_messages']}"""
            
            await update.message.reply_text(stats_text)  # Without parse_mode
            return
        
        # Handle waiting_for_user_id
        if 'waiting_for_user_id' in context.user_data:
            if message_text == "❌ Cancel":
                context.user_data.pop('waiting_for_user_id', None)
                await update.message.reply_text("🚫 Operation cancelled.", reply_markup=get_owner_keyboard())
                return
            
            # Try to find user
            target_user_id = None
            
            # Check if it's a numeric ID
            if message_text.isdigit():
                target_user_id = int(message_text)
            # Check if it's a username
            elif message_text.startswith('@'):
                username = message_text[1:]  # Remove @
                user_info = await db_manager.get_user_by_username(username)
                if user_info:
                    target_user_id = user_info[0]  # First element is ID
            
            if target_user_id:
                context.user_data.pop('waiting_for_user_id', None)
                context.user_data['sending_to_user'] = target_user_id
                
                # Display user information
                user_info = await db_manager.get_user_info(target_user_id)
                if user_info:
                    username, first_name, last_name = user_info
                    target_info = f"🆔 {target_user_id}"
                    if username:
                        target_info += f" | @{username}"
                    if first_name:
                        target_info += f" | {first_name}"
                    if last_name:
                        target_info += f" {last_name}"
                    
                    await update.message.reply_text(
                        f"📝 Sending message to:\n{target_info}\n\nPlease enter your message:",
                        reply_markup=ReplyKeyboardMarkup(
                            [[KeyboardButton("❌ Cancel")]],
                            resize_keyboard=True,
                            one_time_keyboard=True
                        )
                    )
                else:
                    await update.message.reply_text(
                        "❌ User not found. Please enter a valid ID or username.",
                        reply_markup=get_owner_keyboard()
                    )
            else:
                await update.message.reply_text(
                    "❌ Invalid format! Please enter a numeric ID or username with @.\n\nExample: 123456789 or @username"
                )
            return
        
        # Handle broadcast_mode
        if 'broadcast_mode' in context.user_data:
            if message_text == "❌ Cancel":
                context.user_data.pop('broadcast_mode', None)
                await update.message.reply_text("🚫 Broadcast cancelled.", reply_markup=get_owner_keyboard())
                return
            
            # Send broadcast message
            all_users = await db_manager.get_all_users()
            active_users = [user for user in all_users if not user[5]]  # Non-blocked users (is_blocked at index 5)
            
            success_count = 0
            fail_count = 0
            
            progress_message = await update.message.reply_text("📤 Sending broadcast message...")
            
            for user_id, _, _, _, _, _ in active_users:  # 6 values: user_id, username, first_name, last_name, join_date, is_blocked
                try:
                    await context.bot.send_message(chat_id=user_id, text=message_text)
                    success_count += 1
                except Exception as e:
                    fail_count += 1
                    logger.error(f"Failed to send broadcast to {user_id}: {e}")
            
            context.user_data.pop('broadcast_mode', None)
            
            await progress_message.edit_text(
                f"✅ Broadcast completed!\n\n" +
                f"📤 Successful sends: {success_count}\n" +
                f"❌ Failed sends: {fail_count}"
            )
            
            await update.message.reply_text("Return to main menu", reply_markup=get_owner_keyboard())
            return

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular user messages"""
    user = update.effective_user
    
    # Check if user is blocked
    is_blocked = await db_manager.is_user_blocked(user.id)
    if is_blocked:
        await update.message.reply_text("❌ You have been blocked by the bot owner and cannot send messages.")
        return
    
    if update.message.text:
        sender_info = f"👤 Sender: ID {user.id}"
        if user.username:
            sender_info += f" | @{user.username}"
        if user.first_name:
            sender_info += f" | {user.first_name}"
        if user.last_name:
            sender_info += f" {user.last_name}"
        
        full_message = f"{sender_info}\n\n{update.message.text}"
        
        await db_manager.save_message(user.id, update.message.text)
        
        reply_markup = get_reply_block_keyboard(user.id)
        
        await context.bot.send_message(
            chat_id=OWNER_USER_ID,
            text=full_message,
            reply_markup=reply_markup
        )
        
        await update.message.reply_text("✅ Your message has been sent successfully!")

async def send_pending_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send pending message"""
    pending = context.user_data['pending_message']
    target_user_id = pending['target_user_id']
    message = pending['message']
    message_type = pending['message_type']
    
    # Check if we are in reply mode
    is_reply = 'replying_to' in context.user_data
    
    try:
        # Send message based on its type
        if message.text:
            if is_reply:
                # Add admin reply header only for replies
                admin_reply_text = f"`📝 Admin Reply:`\n\n{message.text}"
                await context.bot.send_message(chat_id=target_user_id, text=admin_reply_text, parse_mode='Markdown')
            else:
                # Normal send without header
                await context.bot.send_message(chat_id=target_user_id, text=message.text)
        elif message.photo:
            original_caption = message.caption or ""
            if is_reply:
                new_caption = f"`📝 Admin Reply:`\n\n{original_caption}" if original_caption else "`📝 Admin Reply:`"
                parse_mode = 'Markdown'
            else:
                new_caption = original_caption
                parse_mode = None
            await context.bot.send_photo(
                chat_id=target_user_id,
                photo=message.photo[-1].file_id,
                caption=new_caption,
                parse_mode=parse_mode
            )
        elif message.video:
            original_caption = message.caption or ""
            if is_reply:
                new_caption = f"`📝 Admin Reply:`\n\n{original_caption}" if original_caption else "`📝 Admin Reply:`"
                parse_mode = 'Markdown'
            else:
                new_caption = original_caption
                parse_mode = None
            await context.bot.send_video(
                chat_id=target_user_id,
                video=message.video.file_id,
                caption=new_caption,
                parse_mode=parse_mode
            )
        elif message.document:
            original_caption = message.caption or ""
            if is_reply:
                new_caption = f"`📝 Admin Reply:`\n\n{original_caption}" if original_caption else "`📝 Admin Reply:`"
                parse_mode = 'Markdown'
            else:
                new_caption = original_caption
                parse_mode = None
            await context.bot.send_document(
                chat_id=target_user_id,
                document=message.document.file_id,
                caption=new_caption,
                parse_mode=parse_mode
            )
        elif message.audio:
            original_caption = message.caption or ""
            if is_reply:
                new_caption = f"`📝 Admin Reply:`\n\n{original_caption}" if original_caption else "`📝 Admin Reply:`"
                parse_mode = 'Markdown'
            else:
                new_caption = original_caption
                parse_mode = None
            await context.bot.send_audio(
                chat_id=target_user_id,
                audio=message.audio.file_id,
                caption=new_caption,
                parse_mode=parse_mode
            )
        elif message.voice:
            if is_reply:
                # For voice, send separate message
                await context.bot.send_message(chat_id=target_user_id, text="`📝 Admin Reply:`", parse_mode='Markdown')
            await context.bot.send_voice(
                chat_id=target_user_id,
                voice=message.voice.file_id,
                caption=message.caption
            )
        elif message.sticker:
            if is_reply:
                # For sticker, send separate message
                await context.bot.send_message(chat_id=target_user_id, text="`📝 Admin Reply:`", parse_mode='Markdown')
            await context.bot.send_sticker(
                chat_id=target_user_id,
                sticker=message.sticker.file_id
            )
        
        # Clear temporary data
        context.user_data.pop('pending_message', None)
        context.user_data.pop('replying_to', None)
        context.user_data.pop('sending_to_user', None)
        
        await update.message.reply_text(
            f"✅ {message_type} sent successfully!",
            reply_markup=get_owner_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await update.message.reply_text(
            f"❌ Error sending {message_type}. Please try again later.",
            reply_markup=get_owner_keyboard()
        )

async def cancel_pending_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel pending message"""
    context.user_data.pop('pending_message', None)
    context.user_data.pop('replying_to', None)
    context.user_data.pop('sending_to_user', None)
    
    await update.message.reply_text(
        "🚫 Send cancelled.",
        reply_markup=get_owner_keyboard()
    )