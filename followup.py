import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot

import database as db
from generator import followup_10min, followup_1hr, followup_6hr
from keyboards import kb_whatsapp

logger = logging.getLogger(__name__)

_INTERVALS = {
    "sent_10min": timedelta(minutes=10),
    "sent_1hr": timedelta(hours=1),
    "sent_6hr": timedelta(hours=6),
}


async def _send_followup(bot: Bot, user_id: int, text: str) -> None:
    try:
        await bot.send_message(
            user_id,
            text,
            reply_markup=kb_whatsapp("📲 Book Now on WhatsApp"),
            parse_mode="Markdown",
        )
    except Exception as exc:
        logger.warning("Could not send followup to %s: %s", user_id, exc)


async def _process_user_followups(bot: Bot, user_id: int, first_name: str) -> None:
    row = db.get_followup_row(user_id)
    if not row:
        return
    if row["stopped"]:
        return

    user_row = next(
        (u for u in db.get_all_users() if u["user_id"] == user_id), None
    )
    if user_row and user_row["clicked_wa"]:
        db.mark_followup_sent(user_id, "stopped")
        return

    started_at = datetime.fromisoformat(row["started_at"])
    now = datetime.utcnow()
    elapsed = now - started_at

    if not row["sent_10min"] and elapsed >= _INTERVALS["sent_10min"]:
        await _send_followup(bot, user_id, followup_10min(first_name))
        db.mark_followup_sent(user_id, "sent_10min")

    elif not row["sent_1hr"] and elapsed >= _INTERVALS["sent_1hr"]:
        await _send_followup(bot, user_id, followup_1hr(first_name))
        db.mark_followup_sent(user_id, "sent_1hr")

    elif not row["sent_6hr"] and elapsed >= _INTERVALS["sent_6hr"]:
        await _send_followup(bot, user_id, followup_6hr(first_name))
        db.mark_followup_sent(user_id, "sent_6hr")


async def followup_loop(bot: Bot) -> None:
    logger.info("Follow-up loop started.")
    while True:
        try:
            users = db.get_all_users()
            for user in users:
                user_id = user["user_id"]
                first_name = user["first_name"] or ""
                await _process_user_followups(bot, user_id, first_name)
        except Exception as exc:
            logger.error("followup_loop error: %s", exc)
        await asyncio.sleep(60)
