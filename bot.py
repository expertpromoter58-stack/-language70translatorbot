import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from googletrans import Translator, LANGUAGES

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()

# Language dictionary (70+ languages)
LANGUAGES_70 = {
    'af': 'Afrikaans', 'am': 'Amharic', 'ar': 'Arabic', 'az': 'Azerbaijani',
    'be': 'Belarusian', 'bg': 'Bulgarian', 'bn': 'Bengali', 'bs': 'Bosnian',
    'ca': 'Catalan', 'ceb': 'Cebuano', 'co': 'Corsican', 'cs': 'Czech',
    'cy': 'Welsh', 'da': 'Danish', 'de': 'German', 'el': 'Greek',
    'en': 'English', 'eo': 'Esperanto', 'es': 'Spanish', 'et': 'Estonian',
    'eu': 'Basque', 'fa': 'Persian', 'fi': 'Finnish', 'fr': 'French',
    'fy': 'Frisian', 'ga': 'Irish', 'gd': 'Scots Gaelic', 'gl': 'Galician',
    'gu': 'Gujarati', 'ha': 'Hausa', 'haw': 'Hawaiian', 'he': 'Hebrew',
    'hi': 'Hindi', 'hmn': 'Hmong', 'hr': 'Croatian', 'ht': 'Haitian Creole',
    'hu': 'Hungarian', 'hy': 'Armenian', 'id': 'Indonesian', 'ig': 'Igbo',
    'is': 'Icelandic', 'it': 'Italian', 'ja': 'Japanese', 'jw': 'Javanese',
    'ka': 'Georgian', 'kk': 'Kazakh', 'km': 'Khmer', 'kn': 'Kannada',
    'ko': 'Korean', 'ku': 'Kurdish', 'ky': 'Kyrgyz', 'la': 'Latin',
    'lb': 'Luxembourgish', 'lo': 'Lao', 'lt': 'Lithuanian', 'lv': 'Latvian',
    'mg': 'Malagasy', 'mi': 'Maori', 'mk': 'Macedonian', 'ml': 'Malayalam',
    'mn': 'Mongolian', 'mr': 'Marathi', 'ms': 'Malay', 'mt': 'Maltese',
    'my': 'Burmese', 'ne': 'Nepali', 'nl': 'Dutch', 'no': 'Norwegian',
    'ny': 'Chichewa', 'or': 'Odia', 'pa': 'Punjabi', 'pl': 'Polish',
    'ps': 'Pashto', 'pt': 'Portuguese', 'ro': 'Romanian', 'ru': 'Russian',
    'rw': 'Kinyarwanda', 'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak',
    'sl': 'Slovenian', 'sm': 'Samoan', 'sn': 'Shona', 'so': 'Somali',
    'sq': 'Albanian', 'sr': 'Serbian', 'st': 'Sesotho', 'su': 'Sundanese',
    'sv': 'Swedish', 'sw': 'Swahili', 'ta': 'Tamil', 'te': 'Telugu',
    'tg': 'Tajik', 'th': 'Thai', 'tk': 'Turkmen', 'tl': 'Tagalog',
    'tr': 'Turkish', 'tt': 'Tatar', 'ug': 'Uyghur', 'uk': 'Ukrainian',
    'ur': 'Urdu', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'xh': 'Xhosa',
    'yi': 'Yiddish', 'yo': 'Yoruba', 'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)', 'zu': 'Zulu'
}

# User preferences storage
user_preferences = {}

# Language selection pages
LANGUAGES_PER_PAGE = 15

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {'target': 'en'}
    
    current = user_preferences[user_id]['target']
    current_name = LANGUAGES_70.get(current, current)
    
    welcome = (
        f"🌍 *Hello {user.first_name}!*\n\n"
        f"I translate between 70+ languages.\n\n"
        f"🔤 Current target: *{current_name}*\n\n"
        "📌 *Commands:*\n"
        "/language - Change target language\n"
        "/languages - List all languages\n"
        "/settings - View settings\n"
        "/help - Get help\n\n"
        "✏️ *Just send text to translate!*"
    )
    
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "🤖 *Help*\n\n"
        "📋 *Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/language - Change target language\n"
        "/languages - List all languages\n"
        "/settings - View current settings\n\n"
        "🌍 *How to use:*\n"
        "1. Set your target language with /language\n"
        "2. Send any text message\n"
        "3. I'll detect and translate it!\n\n"
        "💡 *Tip:* If text is already in target language, I'll let you know."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command."""
    user_id = update.effective_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {'target': 'en'}
    
    target = user_preferences[user_id]['target']
    name = LANGUAGES_70.get(target, target)
    
    settings_text = (
        f"⚙️ *Your Settings*\n\n"
        f"Target Language: *{name}* (`{target}`)\n\n"
        f"Use /language to change it."
    )
    
    await update.message.reply_text(settings_text, parse_mode='Markdown')

async def list_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /languages command."""
    # Get first page of languages
    lang_items = list(LANGUAGES_70.items())
    total_pages = (len(lang_items) + LANGUAGES_PER_PAGE - 1) // LANGUAGES_PER_PAGE
    
    message = f"🌍 *Languages (1/{total_pages}):*\n\n"
    
    for code, name in lang_items[:LANGUAGES_PER_PAGE]:
        message += f"• {name} `({code})`\n"
    
    # Add navigation buttons
    keyboard = [[InlineKeyboardButton("Next ➡️", callback_data="lang_page_1")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)

async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language command."""
    # Get first page of languages
    lang_items = list(LANGUAGES_70.items())
    keyboard = []
    row = []
    
    for code, name in lang_items[:12]:  # Show 12 languages per page
        row.append(InlineKeyboardButton(name[:12], callback_data=f"set_{code}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Add navigation
    keyboard.append([
        InlineKeyboardButton("📋 All Languages", callback_data="show_langs"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current = user_preferences.get(update.effective_user.id, {}).get('target', 'en')
    current_name = LANGUAGES_70.get(current, current)
    
    await update.message.reply_text(
        f"🌍 *Select Target Language*\n"
        f"Current: {current_name} ({current})\n\n"
        f"Choose a language:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    # Handle language setting
    if data.startswith('set_'):
        lang_code = data.replace('set_', '')
        lang_name = LANGUAGES_70.get(lang_code, lang_code)
        
        if user_id not in user_preferences:
            user_preferences[user_id] = {}
        
        user_preferences[user_id]['target'] = lang_code
        
        await query.edit_message_text(
            f"✅ *Language Updated!*\n\n"
            f"Target set to: {lang_name} ({lang_code})\n\n"
            f"Send any text to translate!",
            parse_mode='Markdown'
        )
    
    # Handle show all languages
    elif data == 'show_langs':
        await list_languages(update, context)
        await query.delete_message()
    
    # Handle language pagination
    elif data.startswith('lang_page_'):
        page_num = int(data.replace('lang_page_', ''))
        lang_items = list(LANGUAGES_70.items())
        total_pages = (len(lang_items) + LANGUAGES_PER_PAGE - 1) // LANGUAGES_PER_PAGE
        
        start_idx = page_num * LANGUAGES_PER_PAGE
        end_idx = min(start_idx + LANGUAGES_PER_PAGE, len(lang_items))
        
        message = f"🌍 *Languages ({page_num + 1}/{total_pages}):*\n\n"
        for code, name in lang_items[start_idx:end_idx]:
            message += f"• {name} `({code})`\n"
        
        # Navigation buttons
        keyboard = []
        nav_row = []
        
        if page_num > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"lang_page_{page_num - 1}"))
        if page_num < total_pages - 1:
            nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"lang_page_{page_num + 1}"))
        
        if nav_row:
            keyboard.append(nav_row)
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_lang")])
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # Handle back to language menu
    elif data == 'back_to_lang':
        await language_selection(update, context)
    
    # Handle cancel
    elif data == 'cancel':
        await query.edit_message_text("❌ Cancelled. Your settings remain unchanged.")

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages and translate them."""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Skip very long messages
    if len(text) > 5000:
        await update.message.reply_text("❌ Message too long (max 5000 characters).")
        return
    
    # Get user's target language
    if user_id not in user_preferences:
        user_preferences[user_id] = {'target': 'en'}
    
    target_lang = user_preferences[user_id]['target']
    target_name = LANGUAGES_70.get(target_lang, target_lang)
    
    try:
        # Send typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Detect source language
        detection = translator.detect(text)
        src_lang = detection.lang
        src_name = LANGUAGES.get(src_lang, src_lang)
        
        # If source and target are the same, don't translate
        if src_lang == target_lang:
            await update.message.reply_text(
                f"ℹ️ This text is already in *{target_name}*.\n"
                f"No translation needed.",
                parse_mode='Markdown'
            )
            return
        
        # Translate
        translation = translator.translate(text, dest=target_lang)
        translated_text = translation.text
        
        # Format response
        response = (
            f"🔄 *Detected:* {src_name}\n"
            f"📝 *Target:* {target_name}\n\n"
            f"📖 *Translation:*\n"
            f"{translated_text}"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't translate that text.\n"
            "Please try again with a different message."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors globally."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ An unexpected error occurred. Please try again."
            )
        except:
            pass

def main():
    """Start the bot."""
    # Get token from environment variable
    token = os.environ.get('TELEGRAM_TOKEN')
    
    if not token:
        logger.error("❌ TELEGRAM_TOKEN environment variable not set!")
        logger.info("Please set TELEGRAM_TOKEN in Railway environment variables")
        return
    
    try:
        # Create application
        app = Application.builder().token(token).build()
        
        # Add command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("settings", settings_command))
        app.add_handler(CommandHandler("languages", list_languages))
        app.add_handler(CommandHandler("language", language_selection))
        
        # Add callback handler
        app.add_handler(CallbackQueryHandler(handle_callback))
        
        # Add message handler
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
        
        # Add error handler
        app.add_error_handler(error_handler)
        
        logger.info("🚀 Bot starting successfully!")
        logger.info(f"✨ Supporting {len(LANGUAGES_70)} languages")
        logger.info(f"🤖 Bot username: @language70translatorbot")
        
        # Start polling
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
