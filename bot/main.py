import os
import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from datetime import datetime

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Config
TOKEN = os.environ.get('BOT_TOKEN', '')
AWIN_API_KEY = os.environ.get('AWIN_API_KEY', '')
IMPACT_API_KEY = os.environ.get('IMPACT_API_KEY', '')
BASE_URL = os.environ.get('BASE_URL', os.environ.get('VERCEL_URL', ''))
if BASE_URL and not BASE_URL.startswith('http'):
    BASE_URL = f'https://{BASE_URL}'

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛹 Skateboarding", callback_data='cat_skate')],
        [InlineKeyboardButton("🏄 Surf", callback_data='cat_surf')],
        [InlineKeyboardButton("🏂 Snowboard", callback_data='cat_snow')],
        [InlineKeyboardButton("🚴 BMX/MTB", callback_data='cat_bmx')],
        [InlineKeyboardButton("🔥 Ofertas del Día", callback_data='deals')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🏂 *KEMICAL EXTREME* 🛹
"
        "Tu dosis de adrenalina, sin limites.
"
        "50+ marcas • Mejor precio garantizado • Envio directo"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == 'cat_skate':
        await show_skate(query)
    elif data == 'deals':
        await show_deals(query)
    elif data == 'main_menu':
        await start(update, context)
    else:
        await query.edit_message_text(f"Categoria {data} en desarrollo.")

async def show_skate(query):
    keyboard = [
        [InlineKeyboardButton("🛹 Tablas Completas", callback_data='skate_completes')],
        [InlineKeyboardButton("👟 Zapatos (Nike SB, Vans)", callback_data='skate_shoes')],
        [InlineKeyboardButton("🔙 Volver", callback_data='main_menu')]
    ]
    await query.edit_message_text("*SKATEBOARDING*
Selecciona subcategoria:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_deals(query):
    text = "*OFERTAS DEL DIA*
1. Blue Tomato: 20% en Snowwear
2. Tillys: 2x1 en Graphic Tees"
    keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data='main_menu')]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# Bot app global
bot_app = None

async def get_bot_app():
    global bot_app
    if bot_app is None:
        bot_app = Application.builder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler('start', start))
        bot_app.add_handler(CallbackQueryHandler(handle_callback))
        await bot_app.initialize()
    return bot_app

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        application = loop.run_until_complete(get_bot_app())
        update = Update.de_json(data, application.bot)
        loop.run_until_complete(application.process_update(update))
        loop.close()
        return jsonify({'ok': True})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'ok', 'bot': 'Kemical Extreme Bot'})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
