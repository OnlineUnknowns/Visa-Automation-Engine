from aiogram.fsm.state import State, StatesGroup


class BookingFSM(StatesGroup):
    choosing_provider = State()
    choosing_country = State()
    confirming = State()


class BroadcastFSM(StatesGroup):
    waiting_message = State()
