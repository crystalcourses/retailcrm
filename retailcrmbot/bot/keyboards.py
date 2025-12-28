from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Клиенты"), KeyboardButton(text="Заказы")],
            [KeyboardButton(text="Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_customers_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Список клиентов", callback_data="customers_list")],
            [InlineKeyboardButton(text="Найти клиента", callback_data="customers_filter")],
            [InlineKeyboardButton(text="Создать клиента", callback_data="customers_create")],
            [InlineKeyboardButton(text="Назад", callback_data="back_main")]
        ]
    )
    return keyboard


def get_orders_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Заказы клиента", callback_data="orders_by_customer")],
            [InlineKeyboardButton(text="Создать заказ", callback_data="orders_create")],
            [InlineKeyboardButton(text="Добавить платеж", callback_data="payment_create")],
            [InlineKeyboardButton(text="Назад", callback_data="back_main")]
        ]
    )
    return keyboard


def get_pagination_keyboard(current_page: int, total_pages: int, callback_prefix: str):
    buttons = []
    
    if current_page > 1:
        buttons.append(InlineKeyboardButton(
            text="Назад",
            callback_data=f"{callback_prefix}_page_{current_page - 1}"
        ))
    
    buttons.append(InlineKeyboardButton(
        text=f"{current_page}/{total_pages}",
        callback_data="page_info"
    ))
    
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton(
            text="Вперед",
            callback_data=f"{callback_prefix}_page_{current_page + 1}"
        ))
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_main")]
    ])
    
    return keyboard


def get_skip_button(callback_data: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data=callback_data)]
        ]
    )
    return keyboard


def get_cancel_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ]
    )
    return keyboard