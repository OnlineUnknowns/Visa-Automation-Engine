import logging
from database import record_wa_click, upsert_user

logger = logging.getLogger(__name__)


def track_click(user_id: int, username: str | None, source: str = "button") -> None:
    try:
        record_wa_click(user_id, username, source)
        logger.info("WA click tracked: user_id=%s source=%s", user_id, source)
    except Exception as exc:
        logger.error("track_click error: %s", exc)
