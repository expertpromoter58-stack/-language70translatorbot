import os
import logging
import asyncio
from typing import Dict, Optional
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
    'af': 'Afrikaans',
    'am': 'Amharic',
    'ar': 'Arabic',
    'az': 'Azerbaijani',
    'be': 'Belarusian',
    'bg': 'Bulgarian',
    'bn': 'Bengali',
    'bs': 'Bosnian',
    'ca': 'Catalan',
    'ceb': 'Cebuano',
    'co': 'Corsican',
    'cs': 'Czech',
    'cy': 'Welsh',
    'da': 'Danish',
    'de': 'German',
    'el': 'Greek',
    'en': 'English',
    'eo': 'Esperanto',
    'es': 'Spanish',
    'et': 'Estonian',
    'eu': 'Basque',
    'fa': 'Persian',
    'fi': 'Finnish',
    'fr': 'French',
    'fy': 'Frisian',
    'ga': 'Irish',
    'gd': 'Scots Gaelic',
    'gl': 'Galician',
    'gu': 'Gujarati',
    'ha': 'Hausa',
    'haw': 'Hawaiian',
    'he': 'Hebrew',
    'hi': 'Hindi',
    'hmn': 'Hmong',
    'hr': 'Croatian',
    'ht': 'Haitian Creole',
    'hu': 'Hungarian',
    'hy': 'Armenian',
    'id': 'Indonesian',
    'ig': 'Igbo',
    'is': 'Icelandic',
    'it': 'Italian',
    'ja': 'Japanese',
    'jw': 'Javanese',
    'ka': 'Georgian',
    'kk': 'Kazakh',
    'km': 'Khmer',
    'kn': 'Kannada',
    'ko': 'Korean',
    'ku': 'Kurdish',
    'ky': 'Kyrgyz',
    'la': 'Latin',
    'lb': 'Luxembourgish',
    'lo': 'Lao',
    'lt': 'Lithuanian',
    'lv': 'Latvian',
    'mg': 'Malagasy',
    'mi': 'Maori',
    'mk': 'Macedonian',
    'ml': 'Malayalam',
    'mn': 'Mongolian',
    'mr': 'Marathi',
    'ms': 'Malay',
    'mt': 'Maltese',
    'my': 'Burmese',
    'ne': 'Nepali',
    'nl': 'Dutch',
    'no': 'Norwegian',
    'ny': 'Chichewa',
    'or': 'Odia',
    'pa': 'Punjabi',
    'pl': 'Polish',
    'ps': 'Pashto',
    'pt': 'Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'rw': 'Kinyarwanda',
    'sd': 'Sindhi',
    'si': 'Sinhala',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'sm': 'Samoan',
    'sn': 'Shona',
    'so': 'Somali',
    'sq': 'Albanian',
    'sr': 'Serbian',
    'st': 'Sesotho',
    'su': 'Sundanese',
    'sv': 'Swedish',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'te': 'Telugu',
    'tg': 'Tajik',
    'th': 'Thai',
    'tk': 'Turkmen',
    'tl': 'Tagalog',
    'tr': 'Turkish',
    'tt': 'Tatar',
    'ug': 'Uyghur',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'uz': 'Uzbek',
    'vi': 'Vietnamese',
    'xh': 'Xhosa',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'zu': 'Zulu'
}

# User preferences storage
user_preferences: Dict[int, Dict[str, str]] = {}

# Constants
MAX_MESSAGE_LENGTH = 4096
LANGUAGES_PER_PAGE = 20

class TranslationBot:
    """Main bot class to handle all functionality."""
    
    def __init__(self, token: str):
        self.token = token
        self.application = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        user_id = user.id
        
        # Set default language preference
        if user_id not in user_preferences:
            user_preferences[user_id] = {'target': 'en'}
        
        welcome_message = (
            f"🌍 *Hello {user.first_name}!*\n\n"
            "Welcome to Language70 Translator Bot!\n"
            "I can translate text between *70+ languages*.\n\n"
            "📌 *Quick Guide:*\n"
            "• Send me any text to translate\n"
            "• /language - Change target language\n"
            "• /languages - List all languages\n"
            "• /settings - View your settings\n"
            "• /help - Get detailed help\n\n"
            f"🔤 *Current target language:* English (en)\n"
            "Use /language to change it."
        )
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_text = (
            "🤖 *Language70 Translator Bot Help*\n\n"
            "*Basic Commands:*\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/language - Change target language\n"
            "/languages - List all supported languages\n"
            "/settings - View current settings\n"
            "/about - About this bot\n\n"
            "*How to Translate:*\n"
            "1. Set your target language with /language\n"
            "2. Send any text message\n"
            "3. I'll detect the source language and translate it\n\n"
            "*Example:*\n"
            "If your target is Spanish (es) and you send 'Hello',\n"
            "I'll reply with 'Hola'\n\n"
            "*Tips:*\n"
            "• I auto-detect source languages\n"
            "• Translations work in groups too\n"
            "• Support for 70+ languages"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /about command."""
        about_text = (
            "🌍 *About Language70 Translator Bot*\n\n"
            "Version: 2.0.0\n"
            "Languages: 70+\n"
            "Powered by: Google Translate API\n"
            "Framework: python-telegram-bot\n\n"
            "*Features:*\n"
            "• Auto language detection\n"
            "• 70+ language support\n"
            "• Customizable target language\n"
            "• Fast and accurate translations\n"
            "• User-friendly interface\n\n"
            "*Created for:* @language70translatorbot"
        )
        
        await update.message.reply_text(about_text, parse_mode='Markdown')
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /settings command."""
        user_id = update.effective_user.id
        
        if user_id not in user_preferences:
            user_preferences[user_id] = {'target': 'en'}
        
        target_lang = user_preferences[user_id]['target']
        target_name = LANGUAGES_70.get(target_lang, target_lang)
        
        settings_text = (
            f"⚙️ *Your Settings*\n\n"
            f"Target Language: {target_name} ({target_lang})\n\n"
            "To change your target language, use /language"
        )
        
        await update.message.reply_text(settings_text, parse_mode='Markdown')
    
    async def list_languages(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /languages command."""
        # Create language list with codes
        lang_list = []
        for code, name in sorted(LANGUAGES_70.items()):
            lang_list.append(f"• *{name}* `({code})`")
        
        # Split into chunks
        chunks = []
        for i in range(0, len(lang_list), LANGUAGES_PER_PAGE):
            chunks.append(lang_list[i:i + LANGUAGES_PER_PAGE])
        
        # Send first page
        if chunks:
            message = "🌍 *Supported Languages ({}):*\n\n".format(len(LANGUAGES_70))
            message += "\n".join(chunks[0])
            
            if len(chunks) > 1:
                message += f"\n\n*Page 1/{len(chunks)}*"
                keyboard = [
                    [InlineKeyboardButton("Next ➡️", callback_data=f"lang_page_1")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(message, parse_mode='Markdown')
    
    async def language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /language command - Show language selection keyboard."""
        # Create keyboard with languages
        keyboard = []
        row = []
        
        for code, name in sorted(LANGUAGES_70.items()):
            row.append(InlineKeyboardButton(
                f"{name[:15]}", 
                callback_data=f"set_lang_{code}"
            ))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        
        if row:
            keyboard.append(row)
        
        # Add navigation buttons
        keyboard.append([
            InlineKeyboardButton("📋 List All", callback_data="show_all_langs"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_lang")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        current_lang = user_preferences.get(update.effective_user.id, {}).get('target', 'en')
        current_name = LANGUAGES_70.get(current_lang, current_lang)
        
        await update.message.reply_text(
            f"🌍 *Select Target Language*\n\n"
            f"Current: {current_name} ({current_lang})\n"
            "Choose a language from the buttons below:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle all callback queries."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        # Handle language pagination
        if data.startswith('lang_page_'):
            page_num = int(data.replace('lang_page_', ''))
            lang_list = list(LANGUAGES_70.items())
            total_pages = (len(lang_list) + LANGUAGES_PER_PAGE - 1) // LANGUAGES_PER_PAGE
            
            start_idx = page_num * LANGUAGES_PER_PAGE
            end_idx = min(start_idx + LANGUAGES_PER_PAGE, len(lang_list))
            
            message = "🌍 *Supported Languages ({}):*\n\n".format(len(LANGUAGES_70))
            for code, name in lang_list[start_idx:end_idx]:
                message += f"• *{name}* `({code})`\n"
            
            # Navigation buttons
            keyboard = []
            nav_row = []
            
            if page_num > 0:
                nav_row.append(InlineKeyboardButton(
                    "⬅️ Previous", 
                    callback_data=f"lang_page_{page_num - 1}"
                ))
            if page_num < total_pages - 1:
                nav_row.append(InlineKeyboardButton(
                    "Next ➡️", 
                    callback_data=f"lang_page_{page_num + 1}"
                ))
            
            if nav_row:
                keyboard.append(nav_row)
            
            keyboard.append([
                InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_lang_menu")
            ])
            
            message += f"\n*Page {page_num + 1}/{total_pages}*"
            
            await query.edit_message_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        # Handle language setting
        elif data.startswith('set_lang_'):
            lang_code = data.replace('set_lang_', '')
            lang_name = LANGUAGES_70.get(lang_code, lang_code)
            
            if user_id not in user_preferences:
                user_preferences[user_id] = {}
            
            user_preferences[user_id]['target'] = lang_code
            
            await query.edit_message_text(
                f"✅ *Language Updated!*\n\n"
                f"Target language set to: {lang_name} ({lang_code})\n\n"
                f"Now send me any text to translate it to {lang_name}!",
                parse_mode='Markdown'
            )
        
        # Handle show all languages
        elif data == 'show_all_langs':
            await self.list_languages(update, context)
        
        # Handle back to language menu
        elif data == 'back_to_lang_menu':
            await self.language_selection(update, context)
        
        # Handle cancel
        elif data == 'cancel_lang':
            await query.edit_message_text(
                "❌ Language selection cancelled.\n\n"
                "Your settings remain unchanged."
            )
    
    async def translate_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages and translate them."""
        user_id = update.effective_user.id
        text = update.message.text
        
        # Skip very long messages
        if len(text) > 5000:
            await update.message.reply_text(
                "❌ Message is too long (max 5000 characters). Please send a shorter message."
            )
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
                    f"ℹ️ The text is already in {target_name}.\n"
                    f"No translation needed."
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
            
            # Split long messages
            if len(response) > MAX_MESSAGE_LENGTH:
                response = response[:MAX_MESSAGE_LENGTH - 100] + "\n\n... (truncated)"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't translate that text.\n"
                "Please try again with a different message."
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors globally."""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An unexpected error occurred. Please try again."
            )
    
    def run(self) -> None:
        """Start the bot."""
        try:
            # Create application
            self.application = Application.builder().token(self.token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("about", self.about_command))
            self.application.add_handler(CommandHandler("settings", self.settings_command))
            self.application.add_handler(CommandHandler("languages", self.list_languages))
            self.application.add_handler(CommandHandler("language", self.language_selection))
            
            # Add callback handler for inline keyboards
            self.application.add_handler(CallbackQueryHandler(self.handle_callback))
            
            # Add message handler for translations
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.translate_text)
            )
            
            # Add error handler
            self.application.add_error_handler(self.error_handler)
            
            logger.info("🚀 Bot started successfully!")
            logger.info(f"✨ Supporting {len(LANGUAGES_70)} languages")
            
            # Start polling
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise

def main():
    """Main entry point."""
    # Get token from environment variable
    token = os.environ.get('TELEGRAM_TOKEN')
    
    if not token:
        logger.error("❌ TELEGRAM_TOKEN environment variable not set!")
        logger.info("Please set TELEGRAM_TOKEN in Railway environment variables")
        return
    
    # Create and run bot
    bot = TranslationBot(token)
    bot.run()

if __name__ == '__main__':
    main()
