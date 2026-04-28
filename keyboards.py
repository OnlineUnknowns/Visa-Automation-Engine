from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PROVIDERS, COUNTRIES, WHATSAPP_LINK


def kb_providers() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=p, callback_data=f"provider:{p}")]
        for p in PROVIDERS
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def kb_countries() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=c, callback_data=f"country:{c}")]
        for c in COUNTRIES
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def kb_confirm(provider: str, country: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm & Book on WhatsApp", callback_data=f"confirm:{provider}:{country}"),
            ],
            [
                InlineKeyboardButton(text="🔄 Start Over", callback_data="restart"),
            ],
        ]
    )


def kb_whatsapp(label: str = "📲 Book on WhatsApp") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, url=WHATSAPP_LINK)],
        ]
    )


def kb_post_whatsapp() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📲 Book on WhatsApp", url=WHATSAPP_LINK)],
            [InlineKeyboardButton(text="🤖 Open Bot", url="https://t.me/me")],
        ]
    )
