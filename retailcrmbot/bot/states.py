from aiogram.fsm.state import State, StatesGroup


class CustomerStates(StatesGroup):
    waiting_first_name = State()
    waiting_last_name = State()
    waiting_email = State()
    waiting_phone = State()


class CustomerFilterStates(StatesGroup):
    waiting_first_name = State()
    waiting_last_name = State()
    waiting_email = State()


class OrderStates(StatesGroup):
    waiting_customer_id = State()
    waiting_items = State()
    waiting_number = State()


class PaymentStates(StatesGroup):
    waiting_order_id = State()
    waiting_amount = State()
    waiting_type = State()