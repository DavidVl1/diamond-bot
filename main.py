import asyncio
import random
import string
import aiosqlite
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ====================================================
# CONFIG
# ====================================================
# В КОНЦЕ РАЗДЕЛА КОНФИГ (после bot = Bot(...))
user_video_messages = {}
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [7727853285, 7931357584, 7855710591]
MANAGER_USERNAME = "DiamondManager"
COMMISSION_PERCENT = 2
REFERRAL_PERCENT = 50

DB_NAME = "astral.db"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
router = Router()

# ====================================================
# ТВОИ ПРЕМИУМ ЭМОДЗИ ID (для текста приветствия и цитаты)
# ====================================================

ID_WELCOME_START = "5258332798409783582"  # 🎁 в начале
ID_WELCOME_END = "5395732581780040886"  # 🤝 в конце
ID_SHIELD_TITLE = "5258203794772085854"  # 🛡 перед "Ваш надёжный P2P-гарант"
ID_ROCKET = "5794164805065514131"  # 🚀 для 1 пункта
ID_SHIELD_1 = "5794085322400733645"  # 🛡 первый для 2 пункта
ID_SHIELD_2 = "5902016123972358349"  # 🛡 второй для 2 пункта
ID_COIN_1 = "5794280000383358988"  # 🪙 первый для 3 пункта
ID_COIN_2 = "5424912684078348533"  # 🪙 второй для 3 пункта
ID_BOX_1 = "5794241397217304511"  # 📦 первый для 4 пункта
ID_BOX_2 = "5778672437122045013"  # 📦 второй для 4 пункта
ID_HAND_START = "5422439311196834318"  # 👇 перед "Выберите действие"
ID_HAND_END = "5406745015365943482"  # 👇 после "Выберите действие"

# ID ДЛЯ КНОПОК (через icon_custom_emoji_id)
ID_BTN_REKV = "6032745346390560408"  # 💳
ID_BTN_CREATE = "5395732581780040886"  # 🤝
ID_BTN_BALANCE = "5409048419211682843"  # 💰
ID_BTN_DEALS = "5859393109045024271"  # 📦
ID_BTN_REFERRALS = "5902449142575141204"  # 👥
ID_BTN_LANG = "5902432207519093015"  # 🌐
ID_BTN_SUPPORT = "5893494861612455015"  # 🛠

# ID ДЛЯ РАЗДЕЛА МОИ РЕКВИЗИТЫ
ID_MY_REKV_TITLE = "5445221832074483553"  # Мои реквизиты
ID_TON = "5843606192244398823"           # TON кошелёк
ID_CARD = "5231449120635370684"          # Карта
ID_STARS = "5438496463044752972"         # Stars
ID_USDT = "5240147597640876449"          # USDT
ID_BTC = "5816788957614053645"           # BTC
ID_BACK_MENU = "6032745346390560408"     # Назад в меню (у тебя уже есть ID_BTN_REKV? Этот новый)


def pe(emoji_id, default_emoji="•"):
    return f'<tg-emoji emoji-id="{emoji_id}">{default_emoji}</tg-emoji>'


# ====================================================
# ПРИВЕТСТВЕННЫЙ ТЕКСТ (ВСЕ ПРЕМИУМ ЭМОДЗИ ПО ТВОИМ ID)
# ====================================================

WELCOME_TEXT_HTML = f"""
{pe(ID_WELCOME_START, '🎁')} <b>Добро пожаловать в Diamond Gift</b> {pe(ID_WELCOME_END, '🤝')}

<blockquote>
{pe(ID_SHIELD_TITLE, '🛡')} <b>Ваш надёжный P2P-гарант:</b>

{pe(ID_ROCKET, '🚀')} Автоматические сделки с NFT и подарками
{pe(ID_SHIELD_1, '🛡')}{pe(ID_SHIELD_2, '🛡')} Полная защита обеих сторон
{pe(ID_COIN_1, '🪙')}{pe(ID_COIN_2, '🪙')} Реферальная программа — 50% от комиссии
{pe(ID_BOX_1, '📦')}{pe(ID_BOX_2, '📦')} Передача товаров через менеджера: @DiamondManager
</blockquote>

{pe(ID_HAND_START, '👇')} <b>Выберите действие ниже</b> {pe(ID_HAND_END, '👇')}
"""

# ====================================================
# ТЕКСТЫ (внутри разделов — ОБЫЧНЫЕ ЭМОДЗИ)
# ====================================================

TEXTS = {
    'ru': {
        'welcome': WELCOME_TEXT_HTML,

        # Кнопки (текст без эмодзи, эмодзи через icon_custom_emoji_id)
        'btn_my_rekv': "Мои реквизиты",
        'btn_create_deal': "Создать сделку",
        'btn_balance': "Баланс",
        'btn_my_deals': "Мои сделки",
        'btn_referrals': "Рефералы",
        'btn_language': "Язык / Lang",
        'btn_support': "Техподдержка",
        'btn_admin': "⚙️ Админ панель",
        'back_to_menu': "Назад в меню",

        # Баланс (обычные эмодзи)
        'balance_title': "💰 *Diamond Balance*",
        'stars': "⭐ STARS",
        'rub': "🇷🇺 RUB",
        'uah': "🇺🇦 UAH",
        'completed_deals': "✅ Завершённых сделок",
        'withdraw_label': "📤 *Вывод средств* — создайте заявку",
        'transactions_label': "📜 *Транзакции* — история операций",
        'withdraw_btn': "📤 Вывод средств",
        'transactions_btn': "📜 Транзакции",

        # Вывод
        'select_currency_withdraw': "💸 *Выберите валюту для вывода:*",
        'enter_amount': "💸 *Введите сумму вывода в {}:*\n\nМинимальная сумма: 10 {}",
        'min_amount_error': "❌ Минимальная сумма вывода — 10",
        'invalid_number': "❌ Введите число",
        'insufficient_funds': "❌ Недостаточно средств. Доступно: {} {}",
        'enter_details': "🏦 *Отправьте реквизиты для вывода:*\n\nПример:\n`Номер карты: 1234 5678 9012 3456`",
        'withdraw_request_sent': "✅ *Заявка на вывод отправлена администратору.*\n\nОжидайте обработки.",

        # Транзакции
        'transactions_title': "📜 *История транзакций (последние 10)*",
        'no_transactions': "📭 *У вас пока нет транзакций.*",
        'type_deposit': "Пополнение",
        'type_withdraw': "Вывод",
        'type_deal_freeze': "Заморозка",
        'type_deal_income': "Доход от сделки",
        'type_referral_bonus': "Реферальный бонус",

        # Реквизиты
        'my_rekv_title': "💳 *Ваши реквизиты*",
        'not_specified': "❌ не указаны",
        'select_currency_rekv': "📌 *Выберите валюту для добавления/изменения реквизитов:*",
        'enter_rekv_rub': "💳 *Введите ваши реквизиты для RUB:*\n\nПример:\n`Номер карты: XXXX`\n`Имя: Иван`",
        'enter_rekv_uah': "💳 *Введите ваши реквизиты для UAH:*\n\nПример:\n`Номер карты: XXXX`\n`Имя: Иван`",
        'rekv_saved': "✅ *Реквизиты для {} сохранены!*",

        # Рефералы
        'referral_title': "👥 *Реферальная программа*",
        'earned': "💰 Заработано",
        'invited': "👥 Приглашено",
        'referral_desc': "📊 Вы получаете *{}%* от комиссии бота (комиссия {}%) с каждой сделки вашего реферала.",
        'referral_link': "🔗 *Ваша реферальная ссылка:*",
        'share_link': "📤 Поделитесь ссылкой с друзьями!",

        # Сделки
        'my_deals_title': "📦 *Ваши сделки (последние 20)*",
        'no_deals': "📦 *У вас пока нет сделок.*",
        'deal_detail_hint': "\n🔍 *Подробнее:* `/deal DEAL_ID`",

        # Создание сделки
        'enter_seller': "👤 *Отправьте @username продавца:*",
        'seller_not_found': "❌ *Пользователь не найден.*\n\nПродавец должен сначала запустить бота.",
        'self_deal_error': "❌ *Нельзя создать сделку с самим собой.*",
        'enter_gift': "🎁 *Отправьте название NFT подарка:*",
        'enter_amount_deal': "💰 *Введите сумму сделки:*",
        'amount_positive': "❌ Сумма должна быть больше нуля.",
        'select_currency_deal': "💳 *Выберите валюту:*",
        'insufficient_funds_deal': "❌ *Недостаточно средств.*\n\nДоступно: {} {}",
        'deal_created': "✅ *Сделка создана!*\n\n🆔 `{}`\n🎁 {}\n💰 {} {}\n📊 Комиссия: {:.2f} {}\n\n⏳ Ожидайте, пока продавец передаст подарок менеджеру.",

        # Уведомления
        'new_paid_deal': "🔔 *Новая оплаченная сделка!*\n\n🆔 `{}`\n🎁 NFT: {}\n💰 Сумма: {} {}\n\n📌 *Передайте подарок менеджеру:* @{}\n✅ После передачи нажмите кнопку ниже.",
        'gift_sent_btn': "✅ Я передал подарок",
        'support_btn': "🛠 Написать менеджеру",

        # Подтверждение
        'gift_sent_notification': "📦 *Продавец сообщил, что передал подарок менеджеру.*\n\n🆔 `{}`\n\n✅ Подтвердите получение или откройте спор.",
        'confirm_btn': "✅ Получил подарок",
        'dispute_btn': "❌ Открыть спор",
        'waiting_confirmation': "⏳ *Ожидаем подтверждение покупателя...*",

        # Завершение
        'deal_completed': "🎉 *Сделка успешно завершена!*\n\n🆔 `{}`\n\n💰 Средства переведены продавцу.\n⭐ Не забудьте оставить отзыв!",
        'seller_paid': "💰 *Покупатель подтвердил получение подарка!*\n\n🆔 `{}`\n💵 Средства ({} {}) поступили на ваш баланс.",

        # Спор
        'dispute_opened': "⚠️ *Спор открыт!*\n\n🆔 `{}`\n\nАдминистратор свяжется с вами в ближайшее время.",
        'new_dispute_admin': "🚨 *НОВЫЙ СПОР!*\n\n🆔 `{}`\n👤 Покупатель: {}\n👤 Продавец: {}\n💰 {} {}",

        # Язык
        'language_title': "🌐 *Выберите язык*",
        'language_changed': "🌐 *Язык изменён на Русский*",
        'select_language': "🌐 *Выберите язык / Choose language*",

        # Команды
        'top_title': "🏆 *Топ пользователей по сделкам*",
        'deals_count': "сделок",
        'info_text': "🤖 *Diamond Gift Bot*\n\n🛡 P2P гарант для NFT подарков\n💰 Комиссия: {}%\n🎁 Реферальная программа: {}% от комиссии\n\n📞 Поддержка: @{}",
    },
    'en': {
        'welcome': WELCOME_TEXT_HTML.replace("Добро пожаловать в Diamond Gift", "Welcome to Diamond Gift").replace(
            "Ваш надёжный P2P-гарант", "Your reliable P2P guarantor").replace("Автоматические сделки с NFT и подарками",
                                                                              "Automatic NFT and gift deals").replace(
            "Полная защита обеих сторон", "Full protection for both parties").replace(
            "Реферальная программа — 50% от комиссии", "Referral program — 50% of commission").replace(
            "Передача товаров через менеджера: @DiamondManager", "Delivery through manager: @DiamondManagerr").replace(
            "Выберите действие ниже", "Choose an action below"),

        'btn_my_rekv': "My requisites",
        'btn_create_deal': "Create deal",
        'btn_balance': "Balance",
        'btn_my_deals': "My deals",
        'btn_referrals': "Referrals",
        'btn_language': "Language / Lang",
        'btn_support': "Support",
        'btn_admin': "⚙️ Admin panel",
        'back_to_menu': "🔙 Back to menu",

        'balance_title': "💰 *Diamond Balance*",
        'stars': "⭐ STARS",
        'rub': "🇷🇺 RUB",
        'uah': "🇺🇦 UAH",
        'completed_deals': "✅ Completed deals",
        'withdraw_label': "📤 *Withdraw* — create a request",
        'transactions_label': "📜 *Transactions* — history",
        'withdraw_btn': "📤 Withdraw",
        'transactions_btn': "📜 Transactions",

        'select_currency_withdraw': "💸 *Select currency for withdrawal:*",
        'enter_amount': "💸 *Enter withdrawal amount in {}:*\n\nMinimum amount: 10 {}",
        'min_amount_error': "❌ Minimum withdrawal amount is 10",
        'invalid_number': "❌ Enter a number",
        'insufficient_funds': "❌ Insufficient funds. Available: {} {}",
        'enter_details': "🏦 *Enter your withdrawal details:*\n\nExample:\n`Card number: 1234 5678 9012 3456`",
        'withdraw_request_sent': "✅ *Withdrawal request sent to admin.*\n\nPlease wait for processing.",

        'transactions_title': "📜 *Transaction history (last 10)*",
        'no_transactions': "📭 *You have no transactions yet.*",
        'type_deposit': "Deposit",
        'type_withdraw': "Withdrawal",
        'type_deal_freeze': "Freeze",
        'type_deal_income': "Deal income",
        'type_referral_bonus': "Referral bonus",

        'my_rekv_title': "💳 *Your requisites*",
        'not_specified': "❌ not specified",
        'select_currency_rekv': "📌 *Select currency to add/edit requisites:*",
        'enter_rekv_rub': "💳 *Enter your RUB requisites:*\n\nExample:\n`Card number: XXXX`\n`Name: Ivan`",
        'enter_rekv_uah': "💳 *Enter your UAH requisites:*\n\nExample:\n`Card number: XXXX`\n`Name: Ivan`",
        'rekv_saved': "✅ *Requisites for {} saved!*",

        'referral_title': "👥 *Referral Program*",
        'earned': "💰 Earned",
        'invited': "👥 Invited",
        'referral_desc': "📊 You get *{}%* of the bot's commission (commission {}%) from each deal of your referral.",
        'referral_link': "🔗 *Your referral link:*",
        'share_link': "📤 Share the link with friends!",

        'my_deals_title': "📦 *Your deals (last 20)*",
        'no_deals': "📦 *You have no deals yet.*",
        'deal_detail_hint': "\n🔍 *Details:* `/deal DEAL_ID`",

        'enter_seller': "👤 *Send @username of the seller:*",
        'seller_not_found': "❌ *User not found.*\n\nThe seller must start the bot first.",
        'self_deal_error': "❌ *You cannot create a deal with yourself.*",
        'enter_gift': "🎁 *Send the NFT gift name:*",
        'enter_amount_deal': "💰 *Enter the deal amount:*",
        'amount_positive': "❌ Amount must be greater than zero.",
        'select_currency_deal': "💳 *Select currency:*",
        'insufficient_funds_deal': "❌ *Insufficient funds.*\n\nAvailable: {} {}",
        'deal_created': "✅ *Deal created!*\n\n🆔 `{}`\n🎁 {}\n💰 {} {}\n📊 Commission: {:.2f} {}\n\n⏳ Wait for the seller to transfer the gift to the manager.",

        'new_paid_deal': "🔔 *New paid deal!*\n\n🆔 `{}`\n🎁 NFT: {}\n💰 Amount: {} {}\n\n📌 *Transfer the gift to the manager:* @{}\n✅ Click the button after transfer.",
        'gift_sent_btn': "✅ I have transferred the gift",
        'support_btn': "🛠 Contact manager",

        'gift_sent_notification': "📦 *The seller reported that the gift was transferred to the manager.*\n\n🆔 `{}`\n\n✅ Confirm receipt or open a dispute.",
        'confirm_btn': "✅ Received gift",
        'dispute_btn': "❌ Open dispute",
        'waiting_confirmation': "⏳ *Waiting for buyer confirmation...*",

        'deal_completed': "🎉 *Deal completed successfully!*\n\n🆔 `{}`\n\n💰 Funds have been transferred to the seller.\n⭐ Don't forget to leave a review!",
        'seller_paid': "💰 *Buyer confirmed receipt of the gift!*\n\n🆔 `{}`\n💵 Funds ({} {}) have been added to your balance.",

        'dispute_opened': "⚠️ *Dispute opened!*\n\n🆔 `{}`\n\nAn administrator will contact you shortly.",
        'new_dispute_admin': "🚨 *NEW DISPUTE!*\n\n🆔 `{}`\n👤 Buyer: {}\n👤 Seller: {}\n💰 {} {}",

        'language_title': "🌐 *Select language*",
        'language_changed': "🌐 *Language changed to English*",
        'select_language': "🌐 *Select language*",

        'top_title': "🏆 *Top users by deals*",
        'deals_count': "deals",
        'info_text': "🤖 *Diamond Gift Bot*\n\n🛡 P2P guarantor for NFT gifts\n💰 Commission: {}%\n🎁 Referral program: {}% of commission\n\n📞 Support: @{}",
    }
}


# ====================================================
# FSM STATES
# ====================================================

class DealState(StatesGroup):
    wait_role = State()          # Продавец или покупатель
    wait_currency = State()      # Валюта
    wait_amount = State()        # Сумма
    wait_description = State()   # Описание товара


class WithdrawState(StatesGroup):
    wait_currency = State()
    wait_amount = State()
    wait_details = State()


class RekvState(StatesGroup):
    wait_currency = State()
    wait_rekv = State()


class AdminGiveState(StatesGroup):
    wait_user_id = State()
    wait_currency = State()
    wait_amount = State()

class ReviewState(StatesGroup):
    wait_rating = State()
    wait_text = State()


# ====================================================
# DATABASE
# ====================================================

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS users
                         (
                             user_id
                             INTEGER
                             PRIMARY
                             KEY,
                             username
                             TEXT,
                             stars
                             REAL
                             DEFAULT
                             0,
                             rub
                             REAL
                             DEFAULT
                             0,
                             uah
                             REAL
                             DEFAULT
                             0,
                             completed_deals
                             INTEGER
                             DEFAULT
                             0,
                             cancelled_deals
                             INTEGER
                             DEFAULT
                             0,
                             rating
                             REAL
                             DEFAULT
                             5,
                             reviews_count
                             INTEGER
                             DEFAULT
                             0,
                             referrer_id
                             INTEGER
                             DEFAULT
                             NULL,
                             total_earned
                             REAL
                             DEFAULT
                             0,
                             lang
                             TEXT
                             DEFAULT
                             'ru',
                             created_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """)

        await db.execute("""
                         CREATE TABLE IF NOT EXISTS deals
                         (
                             deal_id
                             TEXT
                             PRIMARY
                             KEY,
                             creator_id
                             INTEGER,
                             creator_role
                             TEXT,
                             buyer_id
                             INTEGER,
                             seller_id
                             INTEGER,
                             description
                             TEXT,
                             amount
                             REAL,
                             currency
                             TEXT,
                             commission
                             REAL
                             DEFAULT
                             0,
                             status
                             TEXT,
                             created_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP,
                             confirmed_at
                             TIMESTAMP
                         )
                         """)

        await db.execute("""
                         CREATE TABLE IF NOT EXISTS withdraws
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER,
                             currency
                             TEXT,
                             amount
                             REAL,
                             details
                             TEXT,
                             status
                             TEXT,
                             created_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """)

        await db.execute("""
                         CREATE TABLE IF NOT EXISTS rekv
                         (
                             user_id
                             INTEGER
                             PRIMARY
                             KEY,
                             ton
                             TEXT,
                             stars
                             TEXT,
                             rub
                             TEXT,
                             usdt
                             TEXT,
                             btc
                             TEXT,
                             updated_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """)

        await db.execute("""
                         CREATE TABLE IF NOT EXISTS transactions
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER,
                             type
                             TEXT,
                             currency
                             TEXT,
                             amount
                             REAL,
                             deal_id
                             TEXT,
                             created_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """)

        # ========== НОВАЯ ТАБЛИЦА ДЛЯ ОТЗЫВОВ ==========
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS reviews
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             deal_id
                             TEXT,
                             from_user_id
                             INTEGER,
                             to_user_id
                             INTEGER,
                             rating
                             INTEGER,
                             text
                             TEXT,
                             created_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """)

        await db.commit()
        print("✅ База данных инициализирована")


# ====================================================
# LANGUAGE FUNCTIONS
# ====================================================

async def get_user_lang(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT lang FROM users WHERE user_id=?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0]:
                return row[0]
            return 'ru'


async def set_user_lang(user_id, lang):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
        await db.commit()


async def get_text(user_id, key, *args):
    lang = await get_user_lang(user_id)
    text = TEXTS.get(lang, TEXTS['ru']).get(key, key)
    if args:
        return text.format(*args)
    return text


# ====================================================
# USER FUNCTIONS
# ====================================================

async def add_user(user_id, username, referrer_id=None):
    username = f"@{username}" if username else "Пользователь"
    async with aiosqlite.connect(DB_NAME) as db:
        # Используем INSERT OR IGNORE — если пользователь уже есть, просто игнорируем
        await db.execute(
            "INSERT OR IGNORE INTO users(user_id, username, referrer_id, lang) VALUES(?,?,?,?)",
            (user_id, username, referrer_id, 'ru')
        )
        await db.commit()


async def get_profile(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT stars, rub, uah, completed_deals, cancelled_deals, rating, reviews_count, total_earned FROM users WHERE user_id=?",
                (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row
            return (0, 0, 0, 0, 0, 5, 0, 0)


async def get_user_id(username):
    if not username.startswith("@"):
        username = "@" + username
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users WHERE username=?", (username,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def add_balance(user_id, currency, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"UPDATE users SET {currency.lower()} = {currency.lower()} + ? WHERE user_id=?",
                         (amount, user_id))
        await db.commit()
    await add_transaction(user_id, "deposit", currency, amount)


async def remove_balance(user_id, currency, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"UPDATE users SET {currency.lower()} = {currency.lower()} - ? WHERE user_id=?",
                         (amount, user_id))
        await db.commit()
    await add_transaction(user_id, "withdraw", currency, -amount)


async def add_transaction(user_id, type_, currency, amount, deal_id=None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO transactions(user_id, type, currency, amount, deal_id) VALUES(?,?,?,?,?)",
            (user_id, type_, currency, amount, deal_id)
        )
        await db.commit()


async def save_review(deal_id: str, from_user_id: int, to_user_id: int, rating: int, text: str = ""):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO reviews(deal_id, from_user_id, to_user_id, rating, text) VALUES(?,?,?,?,?)",
            (deal_id, from_user_id, to_user_id, rating, text)
        )
        await db.commit()

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT rating, reviews_count FROM users WHERE user_id=?",
            (to_user_id,)
        ) as cursor:
            row = await cursor.fetchone()

        if row:
            old_rating = row[0]
            reviews_count = row[1]
            new_rating = (old_rating * reviews_count + rating) / (reviews_count + 1)

            await db.execute(
                "UPDATE users SET rating=?, reviews_count=reviews_count+1 WHERE user_id=?",
                (round(new_rating, 2), to_user_id)
            )
            await db.commit()


def is_admin(user_id):
    return user_id in ADMINS


# ====================================================
# ГЛАВНОЕ МЕНЮ (КНОПКИ С ПРЕМИУМ ЭМОДЗИ ЧЕРЕЗ icon_custom_emoji_id)
# ====================================================

async def main_menu(user_id):
    lang = await get_user_lang(user_id)
    texts = TEXTS[lang]

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=texts['btn_my_rekv'],
            callback_data="my_rekv",
            icon_custom_emoji_id=ID_BTN_REKV
        ),
        InlineKeyboardButton(
            text=texts['btn_create_deal'],
            callback_data="create_deal",
            icon_custom_emoji_id=ID_BTN_CREATE
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=texts['btn_balance'],
            callback_data="balance",
            icon_custom_emoji_id=ID_BTN_BALANCE
        ),
        InlineKeyboardButton(
            text=texts['btn_my_deals'],
            callback_data="my_deals",
            icon_custom_emoji_id=ID_BTN_DEALS
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=texts['btn_referrals'],
            callback_data="referrals",
            icon_custom_emoji_id=ID_BTN_REFERRALS
        ),
        InlineKeyboardButton(
            text=texts['btn_language'],
            callback_data="language",
            icon_custom_emoji_id=ID_BTN_LANG
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=texts['btn_support'],
            url=f"https://t.me/{MANAGER_USERNAME}",
            icon_custom_emoji_id=ID_BTN_SUPPORT
        )
    )

    if is_admin(user_id):
        builder.row(
            InlineKeyboardButton(
                text=texts['btn_admin'],
                callback_data="admin_panel"
            )
        )

    return builder.as_markup()


async def back_button(user_id):
    lang = await get_user_lang(user_id)
    texts = TEXTS[lang]
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=texts['back_to_menu'], callback_data="back_to_menu"))
    return builder.as_markup()

async def edit_user_menu(user_id, text, reply_markup, parse_mode="HTML"):
    """Редактирует подпись у видео-сообщения пользователя"""
    if user_id in user_video_messages:
        try:
            await bot.edit_message_caption(
                chat_id=user_id,
                message_id=user_video_messages[user_id],
                caption=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        except Exception:
            # Если видео не найдено — отправляем новое сообщение
            await bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
    else:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )

# ====================================================
# START COMMAND
# ====================================================

async def join_deal_handler(message: types.Message, deal_id: str):
    user_id = message.from_user.id

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT creator_id, creator_role, description, amount, currency, status FROM deals WHERE deal_id=?",
                (deal_id,)) as cursor:
            deal = await cursor.fetchone()

    if not deal:
        await message.answer("❌ Сделка не найдена или уже удалена.")
        return

    creator_id, creator_role, description, amount, currency, status = deal

    if status != "AWAITING_PARTNER" and status != "WAITING_PARTNER":
        await message.answer(f"❌ Сделка уже {status}. Нельзя присоединиться.")
        return

    if user_id == creator_id:
        await message.answer("❌ Вы не можете присоединиться к своей собственной сделке.")
        return

    # Определяем роли
    if creator_role == "seller":
        buyer_id = user_id
        seller_id = creator_id
    else:
        buyer_id = creator_id
        seller_id = user_id

    # Обновляем сделку
    async with aiosqlite.connect(DB_NAME) as db:
        # Если создатель был покупателем - деньги уже заморожены, ставим PAID
        if creator_role == "buyer":
            await db.execute("UPDATE deals SET buyer_id=?, seller_id=?, status=? WHERE deal_id=?",
                             (buyer_id, seller_id, "PAID", deal_id))
        else:
            await db.execute("UPDATE deals SET buyer_id=?, seller_id=?, status=? WHERE deal_id=?",
                             (buyer_id, seller_id, "ACTIVE", deal_id))
        await db.commit()

    # Если создатель был покупателем - деньги уже заморожены
    if creator_role == "buyer":
        await message.answer(
            f"✅ *Вы присоединились к сделке как ПРОДАВЕЦ!*\n\n"
            f"📦 Товар: {description}\n"
            f"💰 Сумма: {amount} {currency}\n\n"
            f"📌 *Передайте товар менеджеру:* @{MANAGER_USERNAME}\n"
            f"✅ После передачи нажмите кнопку ниже.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardBuilder().row(
                InlineKeyboardButton(text="✅ Я передал товар", callback_data=f"gift_sent_{deal_id}")
            ).as_markup()
        )

        # Уведомляем покупателя (создателя)
        await bot.send_message(
            creator_id,
            f"🔔 *Продавец присоединился к сделке!*\n\n"
            f"🆔 `{deal_id}`\n"
            f"💰 Сумма: {amount} {currency}\n\n"
            f"⏳ Ожидайте, пока продавец передаст товар менеджеру.",
            parse_mode="Markdown"
        )

    else:  # creator_role == "buyer"
        # Создатель - продавец, присоединяется покупатель
        # Нужно заморозить деньги покупателя
        stars, rub, uah, _, _, _, _, _ = await get_profile(user_id)
        balances = {"STARS": stars, "RUB": rub, "UAH": uah}

        if balances[currency] < amount:
            await message.answer(f"❌ Недостаточно средств. Доступно: {balances[currency]} {currency}")
            # Откатываем сделку
            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute("UPDATE deals SET status='CANCELLED' WHERE deal_id=?", (deal_id,))
                await db.commit()
            return

        await remove_balance(user_id, currency, amount)
        await add_transaction(user_id, "deal_freeze", currency, -amount, deal_id)

        await message.answer(
            f"✅ *Вы присоединились к сделке как ПОКУПАТЕЛЬ!*\n\n"
            f"📦 Товар: {description}\n"
            f"💰 Сумма: {amount} {currency} (заморожена)\n\n"
            f"⏳ Ожидайте, пока продавец передаст товар менеджеру.",
            parse_mode="Markdown"
        )

        # Уведомляем продавца (создателя)
        await bot.send_message(
            creator_id,
            f"🔔 *Покупатель присоединился к сделке и заморозил {amount} {currency}!*\n\n"
            f"🆔 `{deal_id}`\n"
            f"📦 Товар: {description}\n\n"
            f"📌 *Передайте товар менеджеру:* @{MANAGER_USERNAME}\n"
            f"✅ После передачи нажмите кнопку ниже.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardBuilder().row(
                InlineKeyboardButton(text="✅ Я передал товар", callback_data=f"gift_sent_{deal_id}")
            ).as_markup()
        )

@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()

    args = message.text.split()

    # ПРОВЕРКА: присоединение к сделке
    if len(args) > 1 and args[1].startswith("deal_"):
        deal_id = args[1].replace("deal_", "")
        await join_deal_handler(message, deal_id)
        return

    # Обычная регистрация пользователя (рефералка)
    referrer_id = None
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id == message.from_user.id:
            referrer_id = None

    await add_user(message.from_user.id, message.from_user.username, referrer_id)

    lang = await get_user_lang(message.from_user.id)
    welcome_text = TEXTS[lang]['welcome']

    try:
        video = FSInputFile("video.mp4")
        msg = await message.answer_video(
            video=video,
            caption=welcome_text,
            parse_mode="HTML",
            reply_markup=await main_menu(message.from_user.id)
        )
        user_video_messages[message.from_user.id] = msg.message_id
    except:
        msg = await message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=await main_menu(message.from_user.id)
        )
        user_video_messages[message.from_user.id] = msg.message_id

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    welcome_text = TEXTS[lang]['welcome']

    await edit_user_menu(user_id, welcome_text, await main_menu(user_id), parse_mode="HTML")
    await callback.answer()

# ====================================================
# BALANCE (ОБЫЧНЫЕ ЭМОДЗИ)
# ====================================================

@router.callback_query(DealState.wait_role, F.data.startswith("deal_role_"))
async def deal_role_selected(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    role = callback.data.replace("deal_role_", "")

    await state.update_data(creator_role=role)
    await state.update_data(creator_id=user_id)

    # Удаляем сообщение с выбором роли (чтобы не висело)
    try:
        await callback.message.delete()
    except:
        pass

    if role == "buyer":
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT rub FROM rekv WHERE user_id=?", (user_id,)) as cursor:
                rekv = await cursor.fetchone()
            if not rekv or not rekv[0]:
                await edit_user_menu(user_id,
                                     "⚠️ *Реквизиты не добавлены!*\n\nПожалуйста, добавьте реквизиты в разделе *Мои реквизиты* перед созданием сделки.",
                                     await back_button(user_id), parse_mode="Markdown")
                await state.clear()
                return

    # Показываем выбор валюты (редактируем видео)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⭐ STARS", callback_data="deal_currency_STARS"),
        InlineKeyboardButton(text="🇷🇺 RUB", callback_data="deal_currency_RUB"),
        InlineKeyboardButton(text="🇺🇦 UAH", callback_data="deal_currency_UAH")
    )
    builder.row(InlineKeyboardButton(text=await get_text(user_id, 'back_to_menu'), callback_data="back_to_menu"))

    await edit_user_menu(user_id, "💳 *Способ оплаты:*\n\nКаким способом хотите оплатить сделку?", builder.as_markup(),
                         parse_mode="Markdown")

    await state.set_state(DealState.wait_currency)
    await callback.answer()

@router.callback_query(DealState.wait_currency, F.data.startswith("deal_currency_"))
async def deal_currency_selected(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    currency = callback.data.replace("deal_currency_", "")

    await state.update_data(currency=currency)

    # Удаляем сообщение с выбором валюты
    try:
        await callback.message.delete()
    except:
        pass

    await edit_user_menu(user_id, f"💰 *Укажите количество {currency}:*", await back_button(user_id), parse_mode="Markdown")
    await state.set_state(DealState.wait_amount)
    await callback.answer()


@router.message(DealState.wait_amount)
async def deal_amount_input(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    try:
        amount = float(message.text.strip())
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше нуля.", reply_markup=await back_button(user_id))
            return
    except:
        await message.answer("❌ Введите число.", reply_markup=await back_button(user_id))
        return

    await state.update_data(amount=amount)

    # Редактируем видео, чтобы показать следующий вопрос
    await edit_user_menu(
        user_id,
        "📝 *Введите описание товара:*\n\n**Например:**\nhttps://t.me/nft/ToyBear-32961\nили просто отправьте текстовое описание товара:",
        await back_button(user_id),
        parse_mode="Markdown"
    )
    await state.set_state(DealState.wait_description)


@router.message(DealState.wait_description)
async def deal_description_input(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()

    creator_id = data["creator_id"]
    creator_role = data["creator_role"]
    currency = data["currency"]
    amount = data["amount"]
    description = message.text.strip()
    commission = amount * COMMISSION_PERCENT / 100

    deal_id = generate_deal_id()

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
                         INSERT INTO deals(deal_id, creator_id, creator_role, description, amount, currency, commission,
                                           status)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                         """, (deal_id, creator_id, creator_role, description, amount, currency, commission,
                               "AWAITING_PARTNER"))
        await db.commit()

    # Замораживаем деньги если создатель - покупатель
    if creator_role == "buyer":
        stars, rub, uah, _, _, _, _, _ = await get_profile(user_id)
        balances = {"STARS": stars, "RUB": rub, "UAH": uah}

        if balances[currency] < amount:
            await message.answer(f"❌ Недостаточно средств. Доступно: {balances[currency]} {currency}")
            await state.clear()
            return

        await remove_balance(user_id, currency, amount)
        await update_deal_status(deal_id, "WAITING_PARTNER")
        await add_transaction(user_id, "deal_freeze", currency, -amount, deal_id)

    bot_username = (await bot.get_me()).username
    deal_link = f"https://t.me/{bot_username}?start=deal_{deal_id}"

    partner_role = "покупателя" if creator_role == "seller" else "продавца"

    result_text = (
        f"✅ *Сделка #{deal_id} успешно создана!*\n\n"
        f"1. Роль: {'Продавец' if creator_role == 'seller' else 'Покупатель'}\n"
        f"2. Валюта: {currency}\n"
        f"3. Сумма: {amount}\n"
        f"4. Описание: {description}\n\n"
        f"🔗 *Ссылка для {partner_role}:*\n"
        f"`{deal_link}`\n\n"
        f"📤 Отправьте эту ссылку второй стороне для присоединения к сделке."
    )

    # Отправляем результат как новое сообщение
    await message.answer(result_text, parse_mode="Markdown")

    # Возвращаем главное меню (редактируем видео)
    lang = await get_user_lang(user_id)
    welcome_text = TEXTS[lang]['welcome']

    if user_id in user_video_messages:
        try:
            await bot.edit_message_caption(
                chat_id=user_id,
                message_id=user_video_messages[user_id],
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=await main_menu(user_id)
            )
        except Exception as e:
            await bot.send_message(
                chat_id=user_id,
                text=welcome_text,
                parse_mode="HTML",
                reply_markup=await main_menu(user_id)
            )
    else:
        await bot.send_message(
            chat_id=user_id,
            text=welcome_text,
            parse_mode="HTML",
            reply_markup=await main_menu(user_id)
        )

    await state.clear()



@router.callback_query(F.data == "balance")
async def balance_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    stars, rub, uah, completed, _, _, _, _ = await get_profile(user_id)

    text = f"{await get_text(user_id, 'balance_title')}\n\n"
    text += f"{await get_text(user_id, 'stars')}: `{stars}`\n"
    text += f"{await get_text(user_id, 'rub')}: `{rub}`\n"
    text += f"{await get_text(user_id, 'uah')}: `{uah}`\n\n"
    text += f"{await get_text(user_id, 'completed_deals')}: `{completed}`\n\n"
    text += "➖➖➖➖➖➖➖\n\n"
    text += f"{await get_text(user_id, 'withdraw_label')}\n"
    text += f"{await get_text(user_id, 'transactions_label')}"

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=await get_text(user_id, 'withdraw_btn'), callback_data="withdraw_start"),
        InlineKeyboardButton(text=await get_text(user_id, 'transactions_btn'), callback_data="transactions")
    )
    builder.row(InlineKeyboardButton(text=await get_text(user_id, 'back_to_menu'), callback_data="back_to_menu"))

    await edit_user_menu(user_id, text, builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "transactions")
async def transactions_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT type, currency, amount, created_at FROM transactions WHERE user_id=? ORDER BY created_at DESC LIMIT 10",
                (user_id,)
        ) as cursor:
            transactions = await cursor.fetchall()

    if not transactions:
        text = await get_text(user_id, 'no_transactions')
        await edit_user_menu(user_id, text, await back_button(user_id), parse_mode="Markdown")
        await callback.answer()
        return

    text = f"{await get_text(user_id, 'transactions_title')}\n\n"
    type_names = {
        "deposit": await get_text(user_id, 'type_deposit'),
        "withdraw": await get_text(user_id, 'type_withdraw'),
        "deal_freeze": await get_text(user_id, 'type_deal_freeze'),
        "deal_income": await get_text(user_id, 'type_deal_income'),
        "referral_bonus": await get_text(user_id, 'type_referral_bonus')
    }

    for t in transactions:
        name = type_names.get(t[0], t[0])
        sign = "+" if t[2] > 0 else ""
        text += f"• {name}: {sign}{t[2]} {t[1]} — {t[3][:10]}\n"

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=await back_button(user_id))


# ====================================================
# WITHDRAW SYSTEM
# ====================================================

@router.callback_query(F.data == "withdraw_start")
async def withdraw_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⭐ STARS", callback_data="withdraw_STARS"),
        InlineKeyboardButton(text="🇷🇺 RUB", callback_data="withdraw_RUB"),
        InlineKeyboardButton(text="🇺🇦 UAH", callback_data="withdraw_UAH")
    )
    builder.row(InlineKeyboardButton(text=await get_text(user_id, 'back_to_menu'), callback_data="balance"))

    text = await get_text(user_id, 'select_currency_withdraw')
    await edit_user_menu(user_id, text, builder.as_markup(), parse_mode="Markdown")
    await state.set_state(WithdrawState.wait_currency)
    await callback.answer()

@router.callback_query(WithdrawState.wait_currency, F.data.startswith("withdraw_"))
async def withdraw_currency(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    currency = callback.data.replace("withdraw_", "")
    await state.update_data(currency=currency)

    text = await get_text(user_id, 'enter_amount', currency, currency)
    await edit_user_menu(user_id, text, await back_button(user_id), parse_mode="Markdown")
    await state.set_state(WithdrawState.wait_amount)
    await callback.answer()


@router.message(WithdrawState.wait_amount)
async def withdraw_amount(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    try:
        amount = float(message.text)
        if amount < 10:
            text = await get_text(user_id, 'min_amount_error')
            await message.answer(text, reply_markup=await back_button(user_id))
            return
    except:
        text = await get_text(user_id, 'invalid_number')
        await message.answer(text, reply_markup=await back_button(user_id))
        return

    data = await state.get_data()
    currency = data["currency"]

    stars, rub, uah, _, _, _, _, _ = await get_profile(user_id)
    balances = {"STARS": stars, "RUB": rub, "UAH": uah}

    if balances[currency] < amount:
        text = await get_text(user_id, 'insufficient_funds', balances[currency], currency)
        await message.answer(text, reply_markup=await back_button(user_id))
        return

    await state.update_data(amount=amount)
    text = await get_text(user_id, 'enter_details')
    await message.answer(text, parse_mode="Markdown", reply_markup=await back_button(user_id))
    await state.set_state(WithdrawState.wait_details)


@router.message(WithdrawState.wait_details)
async def withdraw_details(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO withdraws(user_id, currency, amount, details, status) VALUES(?,?,?,?,?)",
            (user_id, data["currency"], data["amount"], message.text, "pending")
        )
        await db.commit()

    for admin in ADMINS:
        try:
            await bot.send_message(
                admin,
                f"🆕 *Новая заявка на вывод*\n\n"
                f"👤 {user_id}\n"
                f"💰 {data['amount']} {data['currency']}\n"
                f"📝 {message.text}",
                parse_mode="Markdown"
            )
        except:
            pass

    await state.clear()
    text = await get_text(user_id, 'withdraw_request_sent')
    await message.answer(text, parse_mode="Markdown", reply_markup=await main_menu(user_id))


# ====================================================
# MY REKVIZIT
# ====================================================

@router.callback_query(F.data == "my_rekv")
async def my_rekv_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # Кнопки с премиум эмодзи
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="TON-кошелёк", callback_data="rekv_TON", icon_custom_emoji_id=ID_TON),
        InlineKeyboardButton(text="Stars", callback_data="rekv_STARS", icon_custom_emoji_id=ID_STARS)
    )
    builder.row(
        InlineKeyboardButton(text="Карта", callback_data="rekv_RUB", icon_custom_emoji_id=ID_CARD),
        InlineKeyboardButton(text="USDT (TRC20)", callback_data="rekv_USDT", icon_custom_emoji_id=ID_USDT)
    )
    builder.row(
        InlineKeyboardButton(text="BTC-кошелёк", callback_data="rekv_BTC", icon_custom_emoji_id=ID_BTC)
    )
    builder.row(
        InlineKeyboardButton(text=await get_text(user_id, 'back_to_menu'), callback_data="back_to_menu", icon_custom_emoji_id=ID_BACK_MENU)
    )

    # Получаем реквизиты из БД
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT ton, stars, rub, usdt, btc FROM rekv WHERE user_id=?", (user_id,)) as cursor:
            row = await cursor.fetchone()

    if row:
        ton = row[0] or "—"
        stars = row[1] or "—"
        rub = row[2] or "—"
        usdt = row[3] or "—"
        btc = row[4] or "—"
    else:
        ton = stars = rub = usdt = btc = "—"

    # Текст с премиум эмодзи (с обычными эмодзи-заглушками)
    text = f"{pe(ID_MY_REKV_TITLE, '💳')} Мои реквизиты\n\n"
    text += f"<blockquote>\n"
    text += f"{pe(ID_TON, '💎')} TON-кошелёк: {ton}\n"
    text += f"{pe(ID_CARD, '💳')} Карта: {rub}\n"
    text += f"{pe(ID_STARS, '⭐️')} Stars: {stars}\n"
    text += f"{pe(ID_USDT, '🪙')} USDT (TRC20): {usdt}\n"
    text += f"{pe(ID_BTC, '🪙')} BTC: {btc}\n"
    text += f"</blockquote>"

    await edit_user_menu(user_id, text, builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("rekv_"))
async def rekv_currency(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    currency = callback.data.replace("rekv_", "")
    await state.update_data(currency=currency)

    texts_map = {
        "TON": f"{pe(ID_TON, '💎')} Введите ваш TON-кошелёк:\n\nПример: UQCD...",
        "STARS": f"{pe(ID_STARS, '⭐️')} Введите ваш юзернейм (@username): \n\nПример: @LokiUSDT",
        "RUB": f"{pe(ID_CARD, '💳')} Введите номер карты:\n\nПример: 44004301985863",
        "USDT": f"{pe(ID_USDT, '🪙')} Введите USDT (TRC20) кошелёк: \n\nПример: TLisCh4HuCQNMofFhSsPZTpSePv7dCEJQh",
        "BTC": f"{pe(ID_BTC, '🪙')} Введите BTC кошелёк:\n\nПример: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    }

    text = texts_map.get(currency, "Введите реквизиты:")
    await edit_user_menu(user_id, text, await back_button(user_id), parse_mode="HTML")

    # ❗ ЭТА СТРОКА БЫЛА ПРОПУЩЕНА ❗
    await state.set_state(RekvState.wait_rekv)

    await callback.answer()


@router.message(RekvState.wait_rekv)
async def rekv_save(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    field = data["currency"].lower()

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            f"INSERT INTO rekv(user_id, {field}) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET {field}=excluded.{field}, updated_at=CURRENT_TIMESTAMP",
            (user_id, message.text)
        )
        await db.commit()

    await state.clear()

    # Отправляем подтверждение (новое сообщение)
    await message.answer(
        f"{pe(ID_MY_REKV_TITLE, '✅')} <b>Реквизиты для {data['currency']} сохранены!</b>",
        parse_mode="HTML"
    )

    # Возвращаем главное меню (редактируем видео)
    lang = await get_user_lang(user_id)
    welcome_text = TEXTS[lang]['welcome']

    if user_id in user_video_messages:
        try:
            await bot.edit_message_caption(
                chat_id=user_id,
                message_id=user_video_messages[user_id],
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=await main_menu(user_id)
            )
        except Exception as e:
            # Если не получилось отредактировать — отправляем новое сообщение
            await bot.send_message(
                chat_id=user_id,
                text=welcome_text,
                parse_mode="HTML",
                reply_markup=await main_menu(user_id)
            )
    else:
        await bot.send_message(
            chat_id=user_id,
            text=welcome_text,
            parse_mode="HTML",
            reply_markup=await main_menu(user_id)
        )

# ====================================================
# REFERRALS
# ====================================================

@router.callback_query(F.data == "referrals")
async def referrals_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT total_earned FROM users WHERE user_id=?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            total_earned = row[0] if row else 0

        async with db.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,)) as cursor:
            ref_count = (await cursor.fetchone())[0]

    bot_username = (await bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={user_id}"

    text = f"{await get_text(user_id, 'referral_title')}\n\n"
    text += f"{await get_text(user_id, 'earned')}: `{total_earned:.2f}`\n"
    text += f"{await get_text(user_id, 'invited')}: `{ref_count}`\n\n"
    text += await get_text(user_id, 'referral_desc', REFERRAL_PERCENT, COMMISSION_PERCENT) + "\n\n"
    text += f"{await get_text(user_id, 'referral_link')}\n`{ref_link}`\n\n"
    text += await get_text(user_id, 'share_link')

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=await get_text(user_id, 'back_to_menu'), callback_data="back_to_menu"))

    await edit_user_menu(user_id, text, builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

# ====================================================
# LANGUAGE
# ====================================================

@router.callback_query(F.data == "language")
async def language_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")
    )
    builder.row(InlineKeyboardButton(text=await get_text(user_id, 'back_to_menu'), callback_data="back_to_menu"))

    text = await get_text(user_id, 'select_language')
    await edit_user_menu(user_id, text, builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.replace("set_lang_", "")
    user_id = callback.from_user.id

    await set_user_lang(user_id, lang)

    if lang == 'ru':
        await callback.answer("🌐 Язык изменён на Русский", show_alert=True)
    else:
        await callback.answer("🌐 Language changed to English", show_alert=True)

    await edit_user_menu(user_id, "👇", await main_menu(user_id), parse_mode="Markdown")
    await callback.answer()

# ====================================================
# DEAL FUNCTIONS
# ====================================================

import secrets

def generate_deal_id():
    return secrets.token_hex(5)  # например: f9f3c018f3

async def get_deal(deal_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT buyer_id, seller_id, description, amount, currency, commission, status FROM deals WHERE deal_id=?",
                (deal_id,)
        ) as cursor:
            return await cursor.fetchone()


async def update_deal_status(deal_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE deals SET status=?, confirmed_at=CURRENT_TIMESTAMP WHERE deal_id=?", (status, deal_id))
        await db.commit()


async def release_money(deal_id):
    deal = await get_deal(deal_id)
    if not deal or deal[6] == "COMPLETED":
        return

    seller_id = deal[1]
    amount = deal[3]
    currency = deal[4]
    commission = deal[5]

    seller_amount = amount - commission

    if seller_amount > 0:
        await add_balance(seller_id, currency, seller_amount)

    await add_transaction(seller_id, "deal_income", currency, seller_amount, deal_id)

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT referrer_id FROM users WHERE user_id=?", (seller_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0]:
                referrer_bonus = commission * (REFERRAL_PERCENT / 100)
                await add_balance(row[0], currency, referrer_bonus)
                await add_transaction(row[0], "referral_bonus", currency, referrer_bonus, deal_id)

    await update_deal_status(deal_id, "COMPLETED")


# ====================================================
# CREATE DEAL FLOW
# ====================================================

@router.callback_query(F.data == "create_deal")
async def create_deal_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📦 Продавец", callback_data="deal_role_seller"),
        InlineKeyboardButton(text="🛍️ Покупатель", callback_data="deal_role_buyer")
    )
    builder.row(InlineKeyboardButton(text=await get_text(user_id, 'back_to_menu'), callback_data="back_to_menu"))

    await callback.message.answer(
        "🔄 *Новая сделка*\n\nКем вы выступаете в этой сделке?\n\n"
        "• Продавец — вы продаёте товар/услугу и получаете оплату.\n"
        "• Покупатель — вы платите и получаете товар/услугу.",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )
    await state.set_state(DealState.wait_role)
    await callback.answer()

@router.callback_query(F.data.startswith("gift_sent_"))
async def gift_sent(callback: types.CallbackQuery):
    deal_id = callback.data.replace("gift_sent_", "")
    deal = await get_deal(deal_id)

    if not deal:
        await callback.answer("❌ Сделка не найдена")
        return

    if callback.from_user.id != deal[1]:
        await callback.answer("❌ Это не ваша сделка", show_alert=True)
        return

    if deal[6] != "PAID":
        await callback.answer("❌ Сделка уже в другом статусе", show_alert=True)
        return

    await update_deal_status(deal_id, "GIFT_SENT")

    buyer_lang = await get_user_lang(deal[0])
    buyer_texts = TEXTS[buyer_lang]

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=buyer_texts['confirm_btn'], callback_data=f"confirm_{deal_id}"),
        InlineKeyboardButton(text=buyer_texts['dispute_btn'], callback_data=f"dispute_{deal_id}")
    )

    text = buyer_texts['gift_sent_notification'].format(deal_id)

    await bot.send_message(
        deal[0],
        text,
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )

    seller_lang = await get_user_lang(deal[1])
    seller_texts = TEXTS[seller_lang]
    await callback.message.edit_text(seller_texts['waiting_confirmation'], parse_mode="Markdown")


@router.callback_query(F.data.startswith("confirm_"))
async def confirm_deal(callback: types.CallbackQuery):
    deal_id = callback.data.replace("confirm_", "")
    deal = await get_deal(deal_id)

    if not deal:
        await callback.answer("❌ Сделка не найдена")
        return

    if callback.from_user.id != deal[0]:
        await callback.answer("❌ Это не ваша сделка", show_alert=True)
        return

    if deal[6] != "GIFT_SENT":
        await callback.answer("❌ Нельзя подтвердить эту сделку сейчас", show_alert=True)
        return

    await release_money(deal_id)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET completed_deals = completed_deals + 1 WHERE user_id IN (?, ?)",
                         (deal[0], deal[1]))
        await db.commit()

    buyer_lang = await get_user_lang(deal[0])
    buyer_texts = TEXTS[buyer_lang]

    await callback.message.edit_text(
        buyer_texts['deal_completed'].format(deal_id),
        parse_mode="Markdown"
    )

    seller_lang = await get_user_lang(deal[1])
    seller_texts = TEXTS[seller_lang]

    await bot.send_message(
        deal[1],
        seller_texts['seller_paid'].format(deal_id, deal[3], deal[4]),
        parse_mode="Markdown"
    )

    # ========== ОТЗЫВ ДЛЯ ПРОДАВЦА (покупатель оценивает продавца) ==========
    builder1 = InlineKeyboardBuilder()
    builder1.row(
        InlineKeyboardButton(text="⭐ Оценить продавца", callback_data=f"rate_seller_{deal_id}")
    )
    await bot.send_message(
        deal[0],
        f"🎉 *Сделка {deal_id} завершена!*\n\n"
        f"Оцените ПРОДАВЦА от 1 до 5 звёзд.",
        parse_mode="Markdown",
        reply_markup=builder1.as_markup()
    )

    # ========== ОТЗЫВ ДЛЯ ПОКУПАТЕЛЯ (продавец оценивает покупателя) ==========
    builder2 = InlineKeyboardBuilder()
    builder2.row(
        InlineKeyboardButton(text="⭐ Оценить покупателя", callback_data=f"rate_buyer_{deal_id}")
    )
    await bot.send_message(
        deal[1],
        f"🎉 *Сделка {deal_id} завершена!*\n\n"
        f"Оцените ПОКУПАТЕЛЯ от 1 до 5 звёзд.",
        parse_mode="Markdown",
        reply_markup=builder2.as_markup()
    )


@router.callback_query(F.data.startswith("dispute_"))
async def dispute_deal(callback: types.CallbackQuery):
    deal_id = callback.data.replace("dispute_", "")
    deal = await get_deal(deal_id)

    if not deal:
        await callback.answer("❌ Сделка не найдена")
        return

    await update_deal_status(deal_id, "DISPUTE")

    user_lang = await get_user_lang(callback.from_user.id)
    user_texts = TEXTS[user_lang]

    for admin in ADMINS:
        try:
            await bot.send_message(
                admin,
                user_texts['new_dispute_admin'].format(deal_id, deal[0], deal[1], deal[3], deal[4]),
                parse_mode="Markdown"
            )
        except:
            pass

    await callback.message.edit_text(
        user_texts['dispute_opened'].format(deal_id),
        parse_mode="Markdown"
    )


# ====================================================
# MY DEALS
# ====================================================

@router.callback_query(F.data == "my_deals")
async def my_deals(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    page = 1  # можно хранить в памяти или FSM, но для простоты начнём с 1
    await show_deals_page(callback, user_id, page)


async def show_deals_page(callback: types.CallbackQuery, user_id, page=1, search_query=None):
    items_per_page = 4  # показывать по 4 сделки на странице

    async with aiosqlite.connect(DB_NAME) as db:
        if search_query:
            # Поиск по deal_id
            async with db.execute(
                    "SELECT deal_id, description, amount, currency, status FROM deals WHERE (buyer_id=? OR seller_id=?) AND deal_id LIKE ? ORDER BY created_at DESC",
                    (user_id, user_id, f"%{search_query}%")
            ) as cursor:
                deals = await cursor.fetchall()
        else:
            async with db.execute(
                    "SELECT deal_id, description, amount, currency, status FROM deals WHERE buyer_id=? OR seller_id=? ORDER BY created_at DESC",
                    (user_id, user_id)
            ) as cursor:
                deals = await cursor.fetchall()

    total_deals = len(deals)
    completed_count = sum(1 for d in deals if d[4] == "COMPLETED")

    # Пагинация
    start = (page - 1) * items_per_page
    end = start + items_per_page
    page_deals = deals[start:end]

    total_pages = (total_deals + items_per_page - 1) // items_per_page if total_deals > 0 else 1

    # Формируем текст
    text = f"📋 *Мои сделки*\n\n"
    text += f"📊 Всего: `{total_deals}` | ✅ Завершено: `{completed_count}`\n\n"

    if not page_deals:
        text += "❌ *У вас пока нет сделок.*\n"
    else:
        # Показываем в две колонки (по желанию, можно просто в столбик)
        for i in range(0, len(page_deals), 2):
            line = ""
            deal1 = page_deals[i]
            status1 = "✅" if deal1[4] == "COMPLETED" else ("⏳" if deal1[4] == "PAID" else "📦")
            line += f"`{deal1[0]}` {deal1[2]} {deal1[3]} {status1}"
            if i + 1 < len(page_deals):
                deal2 = page_deals[i + 1]
                status2 = "✅" if deal2[4] == "COMPLETED" else ("⏳" if deal2[4] == "PAID" else "📦")
                line += f"    `{deal2[0]}` {deal2[2]} {deal2[3]} {status2}"
            text += line + "\n"

    # Пагинация
    if total_pages > 1:
        text += f"\n📄 *Страница {page} из {total_pages}*"

    # Кнопки
    builder = InlineKeyboardBuilder()

    # Навигация по страницам
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"deals_page_{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"deals_page_{page + 1}"))
    if nav_buttons:
        builder.row(*nav_buttons)

    # Поиск
    builder.row(InlineKeyboardButton(text="🔍 Поиск по коду", callback_data="deals_search"))
    builder.row(InlineKeyboardButton(text=await get_text(user_id, 'back_to_menu'), callback_data="back_to_menu"))

    await edit_user_menu(user_id, text, builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("deals_page_"))
async def deals_page(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    await show_deals_page(callback, user_id, page)


@router.callback_query(F.data == "deals_search")
async def deals_search(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("🔍 *Введите код сделки для поиска:*", parse_mode="Markdown")
    await state.set_state("waiting_deal_search")


@router.message(lambda msg: msg.text and msg.text.strip(), F.state == "waiting_deal_search")
async def deals_search_query(message: types.Message, state: FSMContext):
    query = message.text.strip()
    user_id = message.from_user.id
    await state.clear()

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT deal_id, description, amount, currency, status FROM deals WHERE (buyer_id=? OR seller_id=?) AND deal_id LIKE ? ORDER BY created_at DESC",
                (user_id, user_id, f"%{query}%")
        ) as cursor:
            deals = await cursor.fetchall()

    total_deals = len(deals)
    completed_count = sum(1 for d in deals if d[4] == "COMPLETED")

    text = f"📋 *Результаты поиска:* `{query}`\n\n"
    text += f"📊 Найдено: `{total_deals}` | ✅ Завершено: `{completed_count}`\n\n"

    if not deals:
        text += "❌ *Сделки не найдены.*\n"
    else:
        for deal in deals[:10]:  # максимум 10 результатов
            status_icon = "✅" if deal[4] == "COMPLETED" else ("⏳" if deal[4] == "PAID" else "📦")
            text += f"• `{deal[0]}` — {deal[2]} {deal[3]} {status_icon}\n"

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu"))

    await edit_user_menu(user_id, text, builder.as_markup(), parse_mode="Markdown")

@router.message(Command("deal"))
async def get_deal_info(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: `/deal DEAL_ID`", parse_mode="Markdown")
        return

    deal = await get_deal(args[1])
    if not deal:
        await message.answer("❌ Сделка не найдена")
        return

    status_emoji = {
        "WAITING_PAYMENT": "⏳",
        "PAID": "✅",
        "GIFT_SENT": "📦",
        "COMPLETED": "🎉",
        "DISPUTE": "⚠️",
        "CANCELLED": "❌"
    }

    text = f"📄 *Информация о сделке*\n\n"
    text += f"🆔 `{args[1]}`\n"
    text += f"👤 Покупатель: `{deal[0]}`\n"
    text += f"👤 Продавец: `{deal[1]}`\n"
    text += f"🎁 {deal[2]}\n"
    text += f"💰 {deal[3]} {deal[4]}\n"
    text += f"📊 Комиссия: {deal[5]} {deal[4]}\n"
    text += f"📌 Статус: {status_emoji.get(deal[6], deal[6])}"

    await message.answer(text, parse_mode="Markdown")


# ====================================================
# ADMIN PANEL
# ====================================================

async def admin_panel_menu(user_id):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📦 Активные сделки", callback_data="admin_active_deals"),
        InlineKeyboardButton(text="💸 Заявки на вывод", callback_data="admin_withdraws")
    )
    builder.row(
        InlineKeyboardButton(text="➕ Накрутить баланс", callback_data="admin_give"),
        InlineKeyboardButton(text="✅ Завершить сделку", callback_data="admin_complete")
    )
    builder.row(
        InlineKeyboardButton(text="💸 Возврат", callback_data="admin_refund"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
    )
    builder.row(
        InlineKeyboardButton(text="👑 Список админов", callback_data="admin_list"),
        InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")
    )
    builder.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu"))
    return builder.as_markup()

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔ Доступ запрещён")
        return

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            users = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM deals") as cursor:
            deals = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM withdraws WHERE status='pending'") as cursor:
            pending_withdraws = (await cursor.fetchone())[0]

    text = f"⚙️ *Панель администратора*\n\n👥 Пользователей: {users}\n📦 Сделок: {deals}\n💸 Заявок на вывод: {pending_withdraws}"

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📦 Активные сделки", callback_data="admin_active_deals"),
        InlineKeyboardButton(text="💸 Заявки на вывод", callback_data="admin_withdraws")
    )
    builder.row(
        InlineKeyboardButton(text="➕ Накрутить баланс", callback_data="admin_give"),
        InlineKeyboardButton(text="✅ Завершить сделку", callback_data="admin_complete")
    )
    builder.row(
        InlineKeyboardButton(text="💸 Возврат", callback_data="admin_refund"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
    )
    builder.row(
        InlineKeyboardButton(text="👑 Список админов", callback_data="admin_list"),
        InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")
    )
    builder.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu"))

    await edit_user_menu(user_id, text, builder.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data == "admin_active_deals")
async def admin_active_deals(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT deal_id, description, amount, currency, status FROM deals WHERE status NOT IN ('COMPLETED', 'CANCELLED')") as cursor:
            deals = await cursor.fetchall()
    if not deals:
        await callback.message.answer("📭 Активных сделок нет.")
        return
    text = "📦 *Активные сделки*\n\n"
    for deal in deals:
        text += f"🆔 `{deal[0]}` — {deal[1]} — {deal[2]} {deal[3]} — {deal[4]}\n"
    await callback.message.answer(text, parse_mode="Markdown")


@router.callback_query(F.data == "admin_withdraws")
async def admin_withdraws(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT id, user_id, currency, amount, details FROM withdraws WHERE status='pending'") as cursor:
            withdraws = await cursor.fetchall()
    if not withdraws:
        await callback.message.answer("📭 Нет активных заявок на вывод.")
        return
    for w in withdraws:
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_withdraw_{w[0]}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_withdraw_{w[0]}")
        )
        await callback.message.answer(f"💸 *Заявка #{w[0]}*\n\n👤 ID: `{w[1]}`\n💰 {w[3]} {w[2]}\n📝 {w[4]}",
                                      parse_mode="Markdown", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("approve_withdraw_"))
async def approve_withdraw(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    withdraw_id = int(callback.data.replace("approve_withdraw_", ""))
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, currency, amount FROM withdraws WHERE id=?", (withdraw_id,)) as cursor:
            w = await cursor.fetchone()
        if not w:
            await callback.answer("Заявка не найдена")
            return
        await db.execute("UPDATE withdraws SET status='approved' WHERE id=?", (withdraw_id,))
        await db.commit()
    await remove_balance(w[0], w[1], w[2])
    await bot.send_message(w[0],
                           f"✅ *Ваша заявка на вывод {w[2]} {w[1]} одобрена!*\n\nСредства отправлены на указанные реквизиты.",
                           parse_mode="Markdown")
    await callback.message.edit_text(f"✅ Заявка #{withdraw_id} одобрена")


@router.callback_query(F.data.startswith("decline_withdraw_"))
async def decline_withdraw(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    withdraw_id = int(callback.data.replace("decline_withdraw_", ""))
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, currency, amount FROM withdraws WHERE id=?", (withdraw_id,)) as cursor:
            w = await cursor.fetchone()
        await db.execute("UPDATE withdraws SET status='declined' WHERE id=?", (withdraw_id,))
        await db.commit()
    await bot.send_message(w[0], f"❌ *Ваша заявка на вывод {w[2]} {w[1]} отклонена.*\n\nСредства не были списаны.",
                           parse_mode="Markdown")
    await callback.message.edit_text(f"❌ Заявка #{withdraw_id} отклонена")


@router.callback_query(F.data == "admin_give")
async def admin_give_start(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещён", show_alert=True)
        return

    await state.update_data(user_id=callback.from_user.id)

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⭐ STARS", callback_data="give_currency_STARS"),
        InlineKeyboardButton(text="🇷🇺 RUB", callback_data="give_currency_RUB"),
        InlineKeyboardButton(text="🇺🇦 UAH", callback_data="give_currency_UAH")
    )
    builder.row(InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_give"))

    text = "💳 *Выберите валюту для начисления:*"
    await edit_user_menu(callback.from_user.id, text, builder.as_markup(), parse_mode="Markdown")
    await state.set_state(AdminGiveState.wait_currency)
    await callback.answer()


@router.callback_query(AdminGiveState.wait_currency, F.data.startswith("give_currency_"))
async def admin_give_currency(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    currency = callback.data.replace("give_currency_", "")
    await state.update_data(currency=currency)

    text = f"💰 *Введите сумму для начисления в {currency}:*\n\nМинимальная сумма: 1 {currency}"
    await edit_user_menu(callback.from_user.id, text, await back_button(callback.from_user.id), parse_mode="Markdown")
    await state.set_state(AdminGiveState.wait_amount)
    await callback.answer()


@router.message(AdminGiveState.wait_amount)
async def admin_give_amount(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        amount = float(message.text.strip())
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше нуля.")
            return
    except:
        await message.answer("❌ Введите число.\nПример: `100`", parse_mode="Markdown")
        return

    data = await state.get_data()
    user_id = data["user_id"]
    currency = data["currency"]

    # Начисляем баланс
    await add_balance(user_id, currency, amount)
    await state.clear()

    # Отправляем подтверждение
    await message.answer(
        f"✅ *Баланс успешно начислен!*\n\n"
        f"💰 Сумма: `{amount}` `{currency}`\n"
        f"👤 Пользователь: `{user_id}`",
        parse_mode="Markdown"
    )

    # Возвращаемся в админ-панель (редактируем видео)
    lang = await get_user_lang(user_id)

    # Получаем статистику для админ-панели
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            users = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM deals") as cursor:
            deals = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM withdraws WHERE status='pending'") as cursor:
            pending_withdraws = (await cursor.fetchone())[0]

    admin_text = f"⚙️ *Панель администратора*\n\n👥 Пользователей: {users}\n📦 Сделок: {deals}\n💸 Заявок на вывод: {pending_withdraws}"

    if user_id in user_video_messages:
        try:
            await bot.edit_message_caption(
                chat_id=user_id,
                message_id=user_video_messages[user_id],
                caption=admin_text,
                parse_mode="Markdown",
                reply_markup=await admin_panel_menu(user_id)
            )
        except Exception as e:
            await bot.send_message(
                chat_id=user_id,
                text=admin_text,
                parse_mode="Markdown",
                reply_markup=await admin_panel_menu(user_id)
            )
    else:
        await bot.send_message(
            chat_id=user_id,
            text=admin_text,
            parse_mode="Markdown",
            reply_markup=await admin_panel_menu(user_id)
        )

@router.callback_query(F.data == "cancel_give")
async def cancel_give(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    welcome_text = TEXTS[lang]['welcome']
    await edit_user_menu(user_id, welcome_text, await main_menu(user_id), parse_mode="HTML")
    await callback.answer()

@router.message(AdminGiveState.wait_user_id)
async def admin_give_user_id(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        user_id = int(message.text.strip())
    except:
        await message.answer("❌ *Ошибка!* Введите числовой ID пользователя.\nПример: `7727853285`",
                             parse_mode="Markdown")
        return

    await state.update_data(user_id=user_id)

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⭐ STARS", callback_data="give_currency_STARS"),
        InlineKeyboardButton(text="🇷🇺 RUB", callback_data="give_currency_RUB"),
        InlineKeyboardButton(text="🇺🇦 UAH", callback_data="give_currency_UAH")
    )
    builder.row(InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_give"))

    await message.answer("💳 *Выберите валюту:*", parse_mode="Markdown", reply_markup=builder.as_markup())
    await state.set_state(AdminGiveState.wait_currency)


@router.callback_query(AdminGiveState.wait_currency, F.data.startswith("give_currency_"))
async def admin_give_currency(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    currency = callback.data.replace("give_currency_", "")
    await state.update_data(currency=currency)

    await callback.message.edit_text(
        f"💰 *Введите сумму для начисления в {currency}:*\n\nМинимальная сумма: 1 {currency}", parse_mode="Markdown")
    await state.set_state(AdminGiveState.wait_amount)
    await callback.answer()


@router.message(AdminGiveState.wait_amount)
async def admin_give_amount(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        amount = float(message.text.strip())
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше нуля.")
            return
    except:
        await message.answer("❌ Введите число.\nПример: `100`", parse_mode="Markdown")
        return

    data = await state.get_data()
    user_id = data["user_id"]
    currency = data["currency"]

    await add_balance(user_id, currency, amount)
    await state.clear()

    await message.answer(
        f"✅ *Баланс успешно начислен!*\n\n"
        f"👤 Пользователь: `{user_id}`\n"
        f"💰 Сумма: `{amount}` `{currency}`",
        parse_mode="Markdown"
    )

    try:
        await bot.send_message(
            user_id,
            f"💰 *Вам начислено {amount} {currency}*",
            parse_mode="Markdown"
        )
    except:
        pass


@router.callback_query(F.data == "cancel_give")
async def cancel_give(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Операция отменена.")
    await callback.answer()


@router.callback_query(F.data == "admin_complete")
async def admin_complete(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.answer("📝 *Отправьте команду:*\n`/complete DEAL_ID`", parse_mode="Markdown")


@router.callback_query(F.data == "admin_refund")
async def admin_refund(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.answer("📝 *Отправьте команду:*\n`/refund DEAL_ID`", parse_mode="Markdown")


@router.message(Command("complete"))
async def complete_deal_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: `/complete DEAL_ID`", parse_mode="Markdown")
        return
    await release_money(args[1])
    await message.answer(f"✅ Сделка {args[1]} завершена")


@router.message(Command("refund"))
async def refund_deal_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: `/refund DEAL_ID`", parse_mode="Markdown")
        return
    deal = await get_deal(args[1])
    if not deal:
        await message.answer("❌ Сделка не найдена")
        return
    if deal[6] == "COMPLETED":
        await message.answer("❌ Сделка уже завершена")
        return
    await add_balance(deal[0], deal[4], deal[3])
    await update_deal_status(args[1], "CANCELLED")
    await message.answer(f"💸 Возврат выполнен. Покупатель {deal[0]} получил {deal[3]} {deal[4]}")


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            users = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM deals") as cursor:
            deals = (await cursor.fetchone())[0]
        async with db.execute("SELECT SUM(amount) FROM deals WHERE status='COMPLETED'") as cursor:
            total_volume = (await cursor.fetchone())[0] or 0
    await callback.message.answer(
        f"📊 *Статистика бота*\n\n👥 Пользователей: {users}\n📦 Сделок: {deals}\n💰 Оборот: {total_volume:.2f}",
        parse_mode="Markdown")


@router.callback_query(F.data == "admin_list")
async def admin_list(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    text = "👑 *Список администраторов*\n\n"
    for admin in ADMINS:
        text += f"• `{admin}`\n"
    await callback.message.answer(text, parse_mode="Markdown")


@router.callback_query(F.data == "admin_users")
async def admin_users_list(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, username FROM users LIMIT 50") as cursor:
            users = await cursor.fetchall()
    text = "👥 *Последние 50 пользователей*\n\n"
    for user in users:
        text += f"• `{user[0]}` — {user[1]}\n"
    await callback.message.answer(text, parse_mode="Markdown")


# ====================================================
# ADDITIONAL COMMANDS
# ====================================================

@router.message(Command("stats"))
async def stats_command(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            users = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM deals") as cursor:
            deals = (await cursor.fetchone())[0]
    await message.answer(f"📊 Пользователей: {users}\n📦 Сделок: {deals}")


@router.message(Command("top"))
async def top_command(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT username, completed_deals FROM users ORDER BY completed_deals DESC LIMIT 10") as cursor:
            top = await cursor.fetchall()
    text = f"{await get_text(user_id, 'top_title')}\n\n"
    for i, row in enumerate(top, 1):
        text += f"{i}. {row[0]} — {row[1]} {await get_text(user_id, 'deals_count')}\n"
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("ping"))
async def ping(message: types.Message):
    await message.answer("🏓 Pong!")


@router.message(Command("info"))
async def info(message: types.Message):
    user_id = message.from_user.id
    text = await get_text(user_id, 'info_text', COMMISSION_PERCENT, REFERRAL_PERCENT, MANAGER_USERNAME)
    await message.answer(text, parse_mode="Markdown")


# ====================================================
# REVIEW SYSTEM
# ====================================================

@router.callback_query(F.data.startswith("rate_seller_"))
async def rate_seller_start(callback: types.CallbackQuery, state: FSMContext):
    deal_id = callback.data.replace("rate_seller_", "")
    deal = await get_deal(deal_id)

    if not deal:
        await callback.answer("❌ Сделка не найдена")
        return

    if callback.from_user.id != deal[0]:
        await callback.answer("❌ Только покупатель может оставить отзыв", show_alert=True)
        return

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT id FROM reviews WHERE deal_id=? AND from_user_id=? AND to_user_id=?",
                (deal_id, callback.from_user.id, deal[1])
        ) as cursor:
            if await cursor.fetchone():
                await callback.answer("❌ Вы уже оставили отзыв на эту сделку", show_alert=True)
                return

    await state.update_data(deal_id=deal_id, to_user_id=deal[1])

    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.row(InlineKeyboardButton(text=f"⭐ {i}", callback_data=f"review_rating_{i}"))
    builder.row(InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_review"))

    await callback.message.edit_text(
        "⭐ *Оцените продавца:*\n\nВыберите количество звёзд от 1 до 5.",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )
    await state.set_state(ReviewState.wait_rating)
    await callback.answer()


@router.callback_query(F.data.startswith("rate_buyer_"))
async def rate_buyer_start(callback: types.CallbackQuery, state: FSMContext):
    deal_id = callback.data.replace("rate_buyer_", "")
    deal = await get_deal(deal_id)

    if not deal:
        await callback.answer("❌ Сделка не найдена")
        return

    if callback.from_user.id != deal[1]:
        await callback.answer("❌ Только продавец может оценить покупателя", show_alert=True)
        return

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT id FROM reviews WHERE deal_id=? AND from_user_id=? AND to_user_id=?",
                (deal_id, callback.from_user.id, deal[0])
        ) as cursor:
            if await cursor.fetchone():
                await callback.answer("❌ Вы уже оставили отзыв на эту сделку", show_alert=True)
                return

    await state.update_data(deal_id=deal_id, to_user_id=deal[0])

    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.row(InlineKeyboardButton(text=f"⭐ {i}", callback_data=f"review_rating_{i}"))
    builder.row(InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_review"))

    await callback.message.edit_text(
        "⭐ *Оцените покупателя:*\n\nВыберите количество звёзд от 1 до 5.",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )
    await state.set_state(ReviewState.wait_rating)
    await callback.answer()


@router.callback_query(ReviewState.wait_rating, F.data.startswith("review_rating_"))
async def review_rating(callback: types.CallbackQuery, state: FSMContext):
    rating = int(callback.data.replace("review_rating_", ""))
    await state.update_data(rating=rating)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⏩ Пропустить", callback_data="review_skip"))

    await callback.message.edit_text(
        f"✍️ *Напишите отзыв (необязательно)*\n\n"
        f"⭐ Оценка: {rating}/5",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )
    await state.set_state(ReviewState.wait_text)
    await callback.answer()


@router.callback_query(F.data == "review_skip")
async def review_skip(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(text="")
    await save_review_from_state(callback, state)
    await callback.answer()


@router.message(ReviewState.wait_text)
async def review_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await save_review_from_state(message, state)


async def save_review_from_state(event, state: FSMContext):
    data = await state.get_data()
    deal_id = data["deal_id"]
    to_user_id = data["to_user_id"]  # теперь универсально (и продавец, и покупатель)
    rating = data["rating"]
    text = data.get("text", "")

    from_user_id = event.from_user.id

    await save_review(deal_id, from_user_id, to_user_id, rating, text)

    thank_text = (
        f"🙏 *Спасибо за ваш отзыв!*\n\n"
        f"Мы ценим ваше мнение и благодарим за то, что выбрали наш сервис. 💎\n\n"
        f"Возвращайтесь к нам снова! 🚀"
    )

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(thank_text, parse_mode="Markdown")
    else:
        await event.answer(thank_text, parse_mode="Markdown")

    await state.clear()


@router.callback_query(F.data == "cancel_review")
async def cancel_review(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Отзыв отменён.")
    await callback.answer()


# ====================================================
# MAIN
# ====================================================

async def main():
    await init_db()
    dp.include_router(router)

    print("🤖 Diamond Gift бот запущен!")
    print(f"👥 Админы: {ADMINS}")
    print(f"💰 Комиссия: {COMMISSION_PERCENT}%")
    print(f"🎁 Реферальная программа: {REFERRAL_PERCENT}% от комиссии")
    print(f"📞 Поддержка: @{MANAGER_USERNAME}")
    print("🌐 Поддерживаются языки: Русский, English")
    print("✨ Премиум эмодзи: в приветствии, цитате и кнопках")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
