import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import database as db
from config import BOT_TOKEN, GROUP_ID, WHATSAPP_LINK, PROVIDERS, COUNTRIES
from generator import generate_post
from keyboards import kb_providers, kb_countries, kb_confirm, kb_whatsapp, kb_post_whatsapp
from scheduler import group_post_loop
from followup import followup_loop
from states import BookingFSM, BroadcastFSM
from tracking import track_click

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher(storage=MemoryStorage())


# ---------------------------------------------------------------------------
# /start
# ---------------------------------------------------------------------------
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    try:
        user = message.from_user
        db.upsert_user(user.id, user.username, user.first_name)
        db.init_followup(user.id)

        await state.clear()
        await message.answer(
            f"👋 Welcome, *{user.first_name or 'there'}*!\n\n"
            "We help you book visa appointments with **VFS Global**, **TLS Contact**, and **BLS International** — fast, easy, and hassle-free.\n\n"
            "🗓️ *Let's get started!* Please choose your visa provider below:",
            reply_markup=kb_providers(),
        )
        await state.set_state(BookingFSM.choosing_provider)
    except Exception as exc:
        logger.error("cmd_start error: %s", exc)


# ---------------------------------------------------------------------------
# Provider selection
# ---------------------------------------------------------------------------
@dp.callback_query(BookingFSM.choosing_provider, F.data.startswith("provider:"))
async def cb_provider(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        provider = callback.data.split(":", 1)[1]
        await state.update_data(provider=provider)
        await callback.message.edit_text(
            f"✅ Provider selected: *{provider}*\n\n"
            "🌍 Now choose your *destination country*:",
            reply_markup=kb_countries(),
        )
        await state.set_state(BookingFSM.choosing_country)
        await callback.answer()
    except Exception as exc:
        logger.error("cb_provider error: %s", exc)
        await callback.answer("Something went wrong. Please try /start again.")


# ---------------------------------------------------------------------------
# Country selection
# ---------------------------------------------------------------------------
@dp.callback_query(BookingFSM.choosing_country, F.data.startswith("country:"))
async def cb_country(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        country = callback.data.split(":", 1)[1]
        data = await state.get_data()
        provider = data.get("provider", "Unknown")
        await state.update_data(country=country)
        await callback.message.edit_text(
            f"📋 *Booking Summary*\n\n"
            f"🏢 Provider: *{provider}*\n"
            f"🌍 Country: *{country}*\n\n"
            f"⚡ Ready to confirm? Tap below to finalise your booking on WhatsApp — our agent will assist you within minutes.",
            reply_markup=kb_confirm(provider, country),
        )
        await state.set_state(BookingFSM.confirming)
        await callback.answer()
    except Exception as exc:
        logger.error("cb_country error: %s", exc)
        await callback.answer("Something went wrong. Please try /start again.")


# ---------------------------------------------------------------------------
# Confirmation → WhatsApp redirect
# ---------------------------------------------------------------------------
@dp.callback_query(BookingFSM.confirming, F.data.startswith("confirm:"))
async def cb_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        parts = callback.data.split(":", 2)
        provider = parts[1] if len(parts) > 1 else "Unknown"
        country = parts[2] if len(parts) > 2 else "Unknown"
        user = callback.from_user

        track_click(user.id, user.username, source="booking_confirm")

        await callback.message.edit_text(
            f"🎉 *Excellent choice!*\n\n"
            f"Your request for *{provider}* in *{country}* has been noted.\n\n"
            f"📲 Tap the button below to open WhatsApp and speak to our agent right now. We'll confirm your appointment within minutes!\n\n"
            f"_Average response time: under 3 minutes_ ⚡",
            reply_markup=kb_whatsapp("📲 Open WhatsApp Now"),
        )
        await state.clear()
        await callback.answer("Redirecting you to WhatsApp! ✅")
    except Exception as exc:
        logger.error("cb_confirm error: %s", exc)
        await callback.answer("Something went wrong. Please try /start again.")


# ---------------------------------------------------------------------------
# Restart
# ---------------------------------------------------------------------------
@dp.callback_query(F.data == "restart")
async def cb_restart(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await state.clear()
        await callback.message.edit_text(
            "🔄 Let's start over! Please choose your visa provider:",
            reply_markup=kb_providers(),
        )
        await state.set_state(BookingFSM.choosing_provider)
        await callback.answer()
    except Exception as exc:
        logger.error("cb_restart error: %s", exc)


# ---------------------------------------------------------------------------
# /stats — Admin
# ---------------------------------------------------------------------------
@dp.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    try:
        stats = db.get_stats()
        top = stats.get("top_users", [])
        top_text = "\n".join(
            f"  {'@' + u['username'] if u['username'] else u['first_name'] or 'Unknown'} — {u['click_count']} clicks"
            for u in top
        ) or "  No data yet."
        text = (
            "📊 *Analytics Dashboard*\n\n"
            f"👤 Total Users: *{stats.get('total_users', 0)}*\n"
            f"📲 Total WA Clicks: *{stats.get('total_clicks', 0)}*\n"
            f"✅ Converted Users: *{stats.get('converted', 0)}*\n"
            f"📈 Conversion Rate: *{stats.get('conversion_rate', 0)}%*\n\n"
            f"🏆 *Top Active Users:*\n{top_text}"
        )
        await message.answer(text)
    except Exception as exc:
        logger.error("cmd_stats error: %s", exc)


# ---------------------------------------------------------------------------
# /broadcast — Admin
# ---------------------------------------------------------------------------
@dp.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext) -> None:
    try:
        await message.answer(
            "📢 *Broadcast Mode*\n\nSend your message now. It will be forwarded to all users and the group.\n\n"
            "You can include text. Type /cancel to abort."
        )
        await state.set_state(BroadcastFSM.waiting_message)
    except Exception as exc:
        logger.error("cmd_broadcast error: %s", exc)


@dp.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Cancelled.")


@dp.message(BroadcastFSM.waiting_message)
async def do_broadcast(message: Message, state: FSMContext) -> None:
    try:
        await state.clear()
        users = db.get_all_users()
        text = message.text or message.caption or ""
        keyboard = kb_whatsapp("📲 Book on WhatsApp")

        sent = 0
        failed = 0
        for user in users:
            try:
                await bot.send_message(
                    user["user_id"],
                    text,
                    reply_markup=keyboard,
                    parse_mode="Markdown",
                )
                sent += 1
            except Exception:
                failed += 1

        try:
            await bot.send_message(
                GROUP_ID,
                text,
                reply_markup=kb_post_whatsapp(),
                parse_mode="Markdown",
            )
        except Exception as exc:
            logger.warning("Broadcast to group failed: %s", exc)

        await message.answer(
            f"✅ *Broadcast complete.*\n\nSent: {sent}\nFailed: {failed}"
        )
    except Exception as exc:
        logger.error("do_broadcast error: %s", exc)


# ---------------------------------------------------------------------------
# Startup / Main
# ---------------------------------------------------------------------------
async def on_startup(bot: Bot) -> None:
    db.init_db()
    logger.info("Bot started. Launching background tasks.")
    asyncio.create_task(group_post_loop(bot))
    asyncio.create_task(followup_loop(bot))


async def main() -> None:
    dp.startup.register(on_startup)
    logger.info("Starting polling…")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
