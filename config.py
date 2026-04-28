import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "PUT_TOKEN_HERE")
GROUP_ID: int = int(os.getenv("GROUP_ID", "-1001234567890"))
WHATSAPP_NUMBER: str = os.getenv("WHATSAPP_NUMBER", "201286016083")

WHATSAPP_LINK: str = f"https://wa.me/{WHATSAPP_NUMBER}"

PROVIDERS = ["VFS Global", "TLS Contact", "BLS International"]
COUNTRIES = ["Morocco", "Algeria", "Pakistan"]

ADMIN_IDS: list[int] = []
