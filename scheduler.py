import asyncio
import logging
import random

from aiogram import Bot

from config import GROUP_ID
from generator import generate_post
from keyboards import kb_post_whatsapp

logger = logging.getLogger(__name__)

MIN_INTERVAL = 14 * 60  # 14 minutes in seconds
MAX_INTERVAL = 18 * 60  # 18 minutes in seconds


async def group_post_loop(bot: Bot) -> None:
    logger.info("Group auto-post scheduler started.")
    while True:
        try:
            text = generate_post()
            await bot.send_message(
                GROUP_ID,
                text,
                reply_markup=kb_post_whatsapp(),
                parse_mode="Markdown",
            )
            logger.info("Auto-post sent to group %s", GROUP_ID)
        except Exception as exc:
            logger.error("group_post_loop error: %s", exc)

        sleep_seconds = random.randint(MIN_INTERVAL, MAX_INTERVAL)
        logger.debug("Next post in %d seconds.", sleep_seconds)
        await asyncio.sleep(sleep_seconds)
