from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import get_main_menu, get_customers_menu, get_orders_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Добро пожаловать в RetailCRM Bot\n\n"
        "Выберите раздел:",
        reply_markup=get_main_menu()
    )


@router.message(F.text == "Клиенты")
async def customers_section(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Раздел: Клиенты\n\n"
        "Выберите действие:",
        reply_markup=get_customers_menu()
    )


@router.message(F.text == "Заказы")
async def orders_section(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Раздел: Заказы\n\n"
        "Выберите действие:",
        reply_markup=get_orders_menu()
    )


@router.message(F.text == "Помощь")
async def help_command(message: Message):
    help_text = (
        "Доступные разделы:\n\n"
        "Клиенты:\n"
        "- Просмотр списка клиентов\n"
        "- Поиск клиентов по параметрам\n"
        "- Создание нового клиента\n\n"
        "Заказы:\n"
        "- Просмотр заказов клиента\n"
        "- Создание нового заказа\n"
        "- Добавление платежа к заказу\n"
    )
    await message.answer(help_text)


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Главное меню\n\n"
        "Выберите раздел:"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Действие отменено")
    await callback.answer()


@router.callback_query(F.data == "page_info")
async def page_info(callback: CallbackQuery):
    await callback.answer()