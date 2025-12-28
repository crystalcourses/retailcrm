from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import aiohttp

from bot.config import config
from bot.states import CustomerStates, CustomerFilterStates
from bot.keyboards import get_pagination_keyboard, get_skip_button, get_cancel_button, get_customers_menu

router = Router()


@router.callback_query(F.data == "customers_list")
async def customers_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_customers_page(callback.message, 1, state)


async def show_customers_page(message: Message, page: int, state: FSMContext, filters: dict = None):
    async with aiohttp.ClientSession() as session:
        params = {"page": page, "limit": 20}
        
        if filters:
            if filters.get("first_name"):
                params["first_name"] = filters["first_name"]
            if filters.get("last_name"):
                params["last_name"] = filters["last_name"]
            if filters.get("email"):
                params["email"] = filters["email"]
        
        url = f"{config.api_url}/customers"
        headers = {
            "Accept": "application/json",
            "User-Agent": "RetailCRM-Bot/1.0"
        }
        
        print(f"DEBUG BOT: Requesting URL: {url}")
        print(f"DEBUG BOT: Params: {params}")
        
        try:
            async with session.get(url, params=params, headers=headers) as resp:
                print(f"DEBUG BOT: Response status: {resp.status}")
                response_text = await resp.text()
                print(f"DEBUG BOT: Response text: {response_text[:500]}")
                
                if resp.status == 200:
                    customers = await resp.json()
                    
                    if not customers:
                        await message.edit_text("Клиенты не найдены")
                        return
                    
                    text = f"Список клиентов (страница {page}):\n\n"
                    
                    for customer in customers:
                        text += f"ID: {customer['id']}\n"
                        text += f"Имя: {customer.get('first_name', 'Не указано')}\n"
                        text += f"Фамилия: {customer.get('last_name', 'Не указано')}\n"
                        text += f"Email: {customer.get('email', 'Не указано')}\n"
                        text += f"Телефон: {customer.get('phone', 'Не указано')}\n"
                        text += f"Создан: {customer.get('created_at', 'Не указано')}\n"
                        text += "\n"
                    
                    total_pages = page + 1 if len(customers) == 10 else page
                    
                    await message.edit_text(
                        text,
                        reply_markup=get_pagination_keyboard(page, total_pages, "customers_list")
                    )
                else:
                    await message.edit_text(f"Ошибка при получении данных: {resp.status}\n{response_text[:200]}")
        except Exception as e:
            import traceback
            print(f"DEBUG BOT: Exception: {str(e)}")
            print(f"DEBUG BOT: Traceback: {traceback.format_exc()}")
            await message.edit_text(f"Ошибка: {str(e)}")


@router.callback_query(F.data.startswith("customers_list_page_"))
async def customers_page_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    page = int(callback.data.split("_")[-1])
    
    data = await state.get_data()
    filters = data.get("filters")
    
    await show_customers_page(callback.message, page, state, filters)


@router.callback_query(F.data == "customers_filter")
async def customers_filter_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CustomerFilterStates.waiting_first_name)
    await callback.message.edit_text(
        "Введите имя для поиска:",
        reply_markup=get_skip_button("skip_first_name")
    )


@router.callback_query(F.data == "skip_first_name")
async def skip_first_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(first_name=None)
    await state.set_state(CustomerFilterStates.waiting_last_name)
    await callback.message.edit_text(
        "Введите фамилию для поиска:",
        reply_markup=get_skip_button("skip_last_name")
    )


@router.message(CustomerFilterStates.waiting_first_name)
async def process_filter_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(CustomerFilterStates.waiting_last_name)
    await message.answer(
        "Введите фамилию для поиска:",
        reply_markup=get_skip_button("skip_last_name")
    )


@router.callback_query(F.data == "skip_last_name")
async def skip_last_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(last_name=None)
    await state.set_state(CustomerFilterStates.waiting_email)
    await callback.message.edit_text(
        "Введите email для поиска:",
        reply_markup=get_skip_button("skip_email")
    )


@router.message(CustomerFilterStates.waiting_last_name)
async def process_filter_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(CustomerFilterStates.waiting_email)
    await message.answer(
        "Введите email для поиска:",
        reply_markup=get_skip_button("skip_email")
    )


@router.callback_query(F.data == "skip_email")
async def skip_email(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    filters = {
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "email": None
    }
    await state.update_data(filters=filters)
    await state.clear()
    
    msg = await callback.message.edit_text("Поиск клиентов...")
    await show_customers_page(msg, 1, state, filters)


@router.message(CustomerFilterStates.waiting_email)
async def process_filter_email(message: Message, state: FSMContext):
    data = await state.get_data()
    filters = {
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "email": message.text
    }
    await state.update_data(filters=filters)
    await state.clear()
    
    msg = await message.answer("Поиск клиентов...")
    await show_customers_page(msg, 1, state, filters)


@router.callback_query(F.data == "customers_create")
async def customers_create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CustomerStates.waiting_first_name)
    await callback.message.edit_text(
        "Создание нового клиента\n\n"
        "Введите имя:",
        reply_markup=get_cancel_button()
    )


@router.message(CustomerStates.waiting_first_name)
async def process_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(CustomerStates.waiting_last_name)
    await message.answer(
        "Введите фамилию:",
        reply_markup=get_skip_button("skip_last_name_create")
    )


@router.callback_query(F.data == "skip_last_name_create")
async def skip_last_name_create(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(last_name=None)
    await state.set_state(CustomerStates.waiting_email)
    await callback.message.edit_text(
        "Введите email:",
        reply_markup=get_skip_button("skip_email_create")
    )


@router.message(CustomerStates.waiting_last_name)
async def process_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(CustomerStates.waiting_email)
    await message.answer(
        "Введите email:",
        reply_markup=get_skip_button("skip_email_create")
    )


@router.callback_query(F.data == "skip_email_create")
async def skip_email_create(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(email=None)
    await state.set_state(CustomerStates.waiting_phone)
    await callback.message.edit_text(
        "Введите телефон:",
        reply_markup=get_skip_button("skip_phone_create")
    )


@router.message(CustomerStates.waiting_email)
async def process_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await state.set_state(CustomerStates.waiting_phone)
    await message.answer(
        "Введите телефон:",
        reply_markup=get_skip_button("skip_phone_create")
    )


@router.callback_query(F.data == "skip_phone_create")
async def skip_phone_create(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await create_customer_request(callback.message, state, phone=None)


@router.message(CustomerStates.waiting_phone)
async def process_phone(message: Message, state: FSMContext):
    await create_customer_request(message, state, phone=message.text)


async def create_customer_request(message: Message, state: FSMContext, phone: str = None):
    data = await state.get_data()
    
    customer_data = {
        "first_name": data["first_name"]
    }
    
    if data.get("last_name"):
        customer_data["last_name"] = data["last_name"]
    if data.get("email"):
        customer_data["email"] = data["email"]
    if phone:
        customer_data["phone"] = phone
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{config.api_url}/customers", json=customer_data) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    await state.clear()
                    await message.answer(
                        f"Клиент успешно создан\n"
                        f"ID: {result.get('id')}\n\n"
                        "Возвращайтесь в главное меню",
                        reply_markup=get_customers_menu()
                    )
                else:
                    await message.answer(
                        f"Ошибка при создании клиента:\n{result.get('detail', 'Неизвестная ошибка')}"
                    )
        except Exception as e:
            await message.answer(f"Ошибка: {str(e)}")