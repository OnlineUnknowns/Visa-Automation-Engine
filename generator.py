import random
from datetime import datetime, timedelta, date
from typing import Optional

# ---------------------------------------------------------------------------
# Date engine
# ---------------------------------------------------------------------------
_date_state: dict = {"base": date(2026, 4, 14), "cycle": 0}


def _next_weekday(d: date) -> date:
    """Return d if weekday, else next Monday."""
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def _rolling_dates(n: int = 3) -> list[str]:
    results = []
    base = _next_weekday(_date_state["base"])
    current = base
    while len(results) < n:
        current = _next_weekday(current)
        results.append(current.strftime("%B %d, %Y"))
        current += timedelta(days=1)
    return results


def _advance_dates() -> None:
    _date_state["cycle"] += 1
    new_base = _date_state["base"] + timedelta(days=7)
    # Reset after August 2026
    if new_base > date(2026, 8, 31):
        new_base = date(2026, 4, 14)
    _date_state["base"] = new_base


# ---------------------------------------------------------------------------
# Content pools
# ---------------------------------------------------------------------------
HEADLINES_MORNING = [
    "🌅 Good morning! Your visa slot could be just one step away.",
    "☀️ Rise and book — fresh appointment slots just released.",
    "🌄 Start your day right — confirm your visa appointment today.",
    "🌞 Morning update: New dates available for your visa application.",
    "📋 Your visa journey begins here — check today's openings.",
]

HEADLINES_AFTERNOON = [
    "⚡ Act NOW — slots are filling up faster than expected!",
    "🔥 Don't wait until tomorrow. Book your visa appointment TODAY.",
    "🚨 Afternoon alert: Limited slots remaining — secure yours immediately.",
    "⏰ Time is ticking! Visa slots for next month are nearly full.",
    "💥 Urgent: High demand detected. Don't lose your spot!",
]

HEADLINES_NIGHT = [
    "🌙 LAST CHANCE tonight — slots almost GONE. Book NOW.",
    "🔴 CRITICAL: Only a handful of slots remain. Don't sleep on this.",
    "😱 Others are booking RIGHT NOW while you read this. Act fast!",
    "⛔ Slots disappearing by the hour — this is your final warning.",
    "🚫 Tomorrow may be too late. Secure your appointment RIGHT NOW.",
]

AVAILABILITY_PHRASES = [
    "⚠️ Only {n} slots left this week",
    "🔴 Just {n} appointments available",
    "📉 Demand is HIGH — {n} slots remain",
    "🚨 {n} openings left before we close bookings",
    "⚡ Flash availability: {n} spots only",
]

SCARCITY_LINES = [
    "Hundreds of applicants are competing for the same dates.",
    "Our agents confirm this window closes within 48 hours.",
    "Last batch sold out in under 3 hours.",
    "Embassy quotas are strictly enforced — no exceptions.",
    "We cannot guarantee availability after tonight.",
    "Demand has tripled since last week — move fast.",
]

TRUST_LINES = [
    "✅ Verified by 1,000+ successful visa applicants.",
    "🏆 Trusted by families, students & professionals across the region.",
    "🔒 100% secure booking — your data is protected.",
    "💼 Professional agents with 7+ years of embassy experience.",
    "⭐ Rated 4.9/5 by our WhatsApp community.",
    "🌍 We handle VFS, TLS & BLS — all providers, one team.",
]

CTA_LINES = [
    "Tap below and speak to our agent in seconds. 👇",
    "One message = your appointment locked. Don't overthink it. 👇",
    "Message us NOW and we'll handle everything for you. 👇",
    "Stop scrolling. One tap secures your date. 👇",
    "Our agent is online. Tap the button and get started. 👇",
    "Your appointment is 60 seconds away. Tap below. 👇",
]

FOMO_LINES = [
    "🔔 3 people just booked in the last 10 minutes.",
    "👥 12 users are viewing this right now.",
    "📲 Our WhatsApp is active — agents standing by.",
    "⏳ This offer refreshes in a few hours — don't miss it.",
    "👀 Someone from your city just secured their slot.",
]

PROVIDER_EMOJIS = {
    "VFS Global": "🏢",
    "TLS Contact": "🔵",
    "BLS International": "🟠",
}

COUNTRY_FLAGS = {
    "Morocco": "🇲🇦",
    "Algeria": "🇩🇿",
    "Pakistan": "🇵🇰",
}

OPENING_EMOJIS = ["🗓️", "📅", "🗒️", "📆", "🔖"]


# ---------------------------------------------------------------------------
# Time detection
# ---------------------------------------------------------------------------
def _time_period() -> str:
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    else:
        return "night"


# ---------------------------------------------------------------------------
# Message builder
# ---------------------------------------------------------------------------
def generate_post() -> str:
    period = _time_period()

    if period == "morning":
        headline = random.choice(HEADLINES_MORNING)
    elif period == "afternoon":
        headline = random.choice(HEADLINES_AFTERNOON)
    else:
        headline = random.choice(HEADLINES_NIGHT)

    providers = random.sample(["VFS Global", "TLS Contact", "BLS International"], k=random.randint(2, 3))
    countries = random.sample(["Morocco", "Algeria", "Pakistan"], k=random.randint(2, 3))
    dates = _rolling_dates(3)

    avail = random.choice(AVAILABILITY_PHRASES).format(n=random.randint(2, 8))
    scarcity = random.choice(SCARCITY_LINES)
    trust = random.choice(TRUST_LINES)
    cta = random.choice(CTA_LINES)
    fomo = random.choice(FOMO_LINES)

    opening_emoji = random.choice(OPENING_EMOJIS)

    provider_lines = "\n".join(
        f"  {PROVIDER_EMOJIS.get(p, '🔹')} {p}" for p in providers
    )
    country_lines = "\n".join(
        f"  {COUNTRY_FLAGS.get(c, '🌍')} {c}" for c in countries
    )
    date_lines = "\n".join(f"  📌 {d}" for d in dates)

    separator = "━" * 28

    msg = (
        f"{headline}\n\n"
        f"{separator}\n\n"
        f"{opening_emoji} **Available Providers:**\n{provider_lines}\n\n"
        f"🌍 **Countries Covered:**\n{country_lines}\n\n"
        f"📅 **Next Available Slots:**\n{date_lines}\n\n"
        f"{separator}\n\n"
        f"{avail}\n"
        f"🔸 {scarcity}\n"
        f"{fomo}\n\n"
        f"{trust}\n\n"
        f"💬 {cta}"
    )

    # Advance dates every 5 posts (cycle)
    _date_state["cycle"] += 1
    if _date_state["cycle"] % 5 == 0:
        _advance_dates()

    return msg


# ---------------------------------------------------------------------------
# Follow-up messages
# ---------------------------------------------------------------------------
def followup_10min(first_name: str) -> str:
    names = [first_name or "there", "friend", ""]
    greeting = random.choice(names)
    prefix = f"Hey {greeting}! 👋" if greeting else "Hey! 👋"
    options = [
        f"{prefix}\n\nJust checking in — did you get a chance to secure your visa appointment?\n\n"
        f"⚠️ Slots are still available but moving fast. One quick message on WhatsApp and we'll lock in your date.",
        f"{prefix}\n\nWe noticed you haven't completed your booking yet. That's okay!\n\n"
        f"Our agents are standing by to help you right now. It takes less than 2 minutes. 📲",
        f"{prefix}\n\nYour appointment is still waiting for you! 🗓️\n\n"
        f"Don't let the slot disappear — reach us on WhatsApp and we'll handle everything.",
    ]
    return random.choice(options)


def followup_1hr(first_name: str) -> str:
    name = first_name or "there"
    options = [
        f"⏰ An hour has passed, {name}.\n\n"
        f"🔴 We've had multiple bookings come in since you visited us. Your slot may no longer be available tomorrow.\n\n"
        f"Don't risk the delay — book your visa appointment NOW on WhatsApp.",
        f"🚨 {name}, this is urgent.\n\n"
        f"Appointment windows are closing faster than expected. Several of today's slots have already been taken.\n\n"
        f"Tap below to speak to our agent before it's too late.",
        f"😬 Still here, {name}?\n\n"
        f"We get it — life gets busy. But your visa appointment won't wait.\n\n"
        f"⚡ Reach our agent on WhatsApp now. This is your best chance this week.",
    ]
    return random.choice(options)


def followup_6hr(first_name: str) -> str:
    options = [
        "🌙 Final reminder before we close for the night.\n\n"
        "We've been holding a potential slot for you — but we can't guarantee it much longer.\n\n"
        "📲 Send us ONE message on WhatsApp right now. No forms, no complications. Just a quick message and you're set.",
        "⛔ This is your LAST reminder from us.\n\n"
        "If you don't book tonight, you may have to wait weeks for the next available slot.\n\n"
        "Our agent is still online. Tap below — it's now or never.",
        "🔴 FINAL NOTICE — Appointment availability resets tonight.\n\n"
        "Whatever slot was being held for you may be released to other applicants within the hour.\n\n"
        "Act NOW. One tap on WhatsApp. We'll take care of the rest.",
    ]
    return random.choice(options)
