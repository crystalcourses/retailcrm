from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import aiohttp

from bot.config import config
from bot.states import OrderStates, PaymentStates
from bot.keyboards import get_pagination_keyboard, get_skip_button, get_cancel_button, get_orders_menu

router = Router()


@router.callback_query(F.data == "orders_by_customer")
async def orders_by_customer_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(OrderStates.waiting_customer_id)
    await callback.message.edit_text(
        "Введите ID клиента для просмотра заказов:",
        reply_markup=get_cancel_button()
    )


@router.message(OrderStates.waiting_customer_id)
async def process_customer_id_for_orders(message: Message, state: FSMContext):
    try:
        customer_id = int(message.text)
        await state.update_data(customer_id=customer_id)
        await state.clear()
        
        msg = await message.answer("Загрузка заказов...")
        await show_orders_page(msg, customer_id, 1, state)
    except ValueError:
        await message.answer("ID клиента должен быть числом. Попробуйте снова:")


async def show_orders_page(message: Message, customer_id: int, page: int, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        params = {"page": page, "limit": 20}
        
        try:
            async with session.get(f"{config.api_url}/customers/{customer_id}/orders", params=params) as resp:
                if resp.status == 200:
                    orders = await resp.json()
                    
                    if not orders:
                        await message.edit_text("Заказы не найдены")
                        return
                    
                    text = f"Заказы клиента {customer_id} (страница {page}):\n\n"
                    
                    for order in orders:
                        text += f"ID: {order['id']}\n"
                        text += f"Номер: {order.get('number', 'Не указан')}\n"
                        text += f"Статус: {order.get('status', 'Не указан')}\n"
                        text += f"Сумма: {order.get('total_sum', 0)}\n"
                        text += f"Создан: {order.get('created_at', 'Не указано')}\n"
                        text += "\n"
                    
                    total_pages = page + 1 if len(orders) == 10 else page
                    
                    await state.update_data(orders_customer_id=customer_id)
                    
                    await message.edit_text(
                        text,
                        reply_markup=get_pagination_keyboard(page, total_pages, "orders_list")
                    )
                else:
                    error_data = await resp.json()
                    await message.edit_text(f"Ошибка при получении данных: {error_data.get('detail', resp.status)}")
        except Exception as e:
            await message.edit_text(f"Ошибка: {str(e)}")


@router.callback_query(F.data.startswith("orders_list_page_"))
async def orders_page_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    page = int(callback.data.split("_")[-1])
    
    data = await state.get_data()
    customer_id = data.get("orders_customer_id")
    
    if customer_id:
        await show_orders_page(callback.message, customer_id, page, state)


@router.callback_query(F.data == "orders_create")
async def orders_create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(OrderStates.waiting_customer_id)
    await callback.message.edit_text(
        "Создание нового заказа\n\n"
        "Введите ID клиента:",
        reply_markup=get_cancel_button()
    )


@router.message(OrderStates.waiting_customer_id)
async def process_customer_id_for_create(message: Message, state: FSMContext):
    try:
        customer_id = int(message.text)
        await state.update_data(customer_id=customer_id)
        await state.set_state(OrderStates.waiting_number)
        await message.answer(
            "Введите номер заказа:",
            reply_markup=get_skip_button("skip_order_number")
        )
    except ValueError:
        await message.answer("ID клиента должен быть числом. Попробуйте снова:")


@router.callback_query(F.data == "skip_order_number")
async def skip_order_number(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(number=None)
    await state.set_state(OrderStates.waiting_items)
    await callback.message.edit_text(
        "Введите товары в формате:\n"
        "название|количество|цена\n\n"
        "Для нескольких товаров каждый с новой строки.\n\n"
        "Пример:\n"
        "Товар 1|2|1500\n"
        "Товар 2|1|3000",
        reply_markup=get_cancel_button()
    )


@router.message(OrderStates.waiting_number)
async def process_order_number(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    await state.set_state(OrderStates.waiting_items)
    await message.answer(
        "Введите товары в формате:\n"
        "название|количество|цена\n\n"
        "Для нескольких товаров каждый с новой строки.\n\n"
        "Пример:\n"
        "Товар 1|2|1500\n"
        "Товар 2|1|3000",
        reply_markup=get_cancel_button()
    )


@router.message(OrderStates.waiting_items)
async def process_order_items(message: Message, state: FSMContext):
    try:
        lines = message.text.strip().split('\n')
        items = []
        
        for line in lines:
            parts = line.split('|')
            if len(parts) != 3:
                await message.answer(
                    "Неверный формат. Используйте:\n"
                    "название|количество|цена\n\n"
                    "Попробуйте снова:"
                )
                return
            
            product_name = parts[0].strip()
            quantity = int(parts[1].strip())
            price = float(parts[2].strip())
            
            items.append({
                "product_name": product_name,
                "quantity": quantity,
                "price": price
            })
        
        data = await state.get_data()
        
        order_data = {
            "customer_id": data["customer_id"],
            "items": items
        }
        
        if data.get("number"):
            order_data["number"] = data["number"]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{config.api_url}/orders", json=order_data) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    await state.clear()
                    await message.answer(
                        f"Заказ успешно создан\n"
                        f"ID: {result.get('id')}\n\n"
                        "Возвращайтесь в главное меню",
                        reply_markup=get_orders_menu()
                    )
                else:
                    await message.answer(
                        f"Ошибка при создании заказа:\n{result.get('detail', 'Неизвестная ошибка')}"
                    )
    except ValueError:
        await message.answer(
            "Ошибка в данных. Проверьте что количество и цена - числа.\n"
            "Попробуйте снова:"
        )
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")


@router.callback_query(F.data == "payment_create")
async def payment_create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(PaymentStates.waiting_order_id)
    await callback.message.edit_text(
        "Добавление платежа\n\n"
        "Введите ID заказа:",
        reply_markup=get_cancel_button()
    )


@router.message(PaymentStates.waiting_order_id)
async def process_order_id_for_payment(message: Message, state: FSMContext):
    try:
        order_id = int(message.text)
        await state.update_data(order_id=order_id)
        await state.set_state(PaymentStates.waiting_amount)
        await message.answer(
            "Введите сумму платежа:",
            reply_markup=get_cancel_button()
        )
    except ValueError:
        await message.answer("ID заказа должен быть числом. Попробуйте снова:")


@router.message(PaymentStates.waiting_amount)
async def process_payment_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await state.set_state(PaymentStates.waiting_type)
        await message.answer(
            "Введите тип платежа (cash, card, online):",
            reply_markup=get_skip_button("skip_payment_type")
        )
    except ValueError:
        await message.answer("Сумма должна быть числом. Попробуйте снова:")


@router.callback_query(F.data == "skip_payment_type")
async def skip_payment_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await create_payment_request(callback.message, state, payment_type="cash")


@router.message(PaymentStates.waiting_type)
async def process_payment_type(message: Message, state: FSMContext):
    await create_payment_request(message, state, payment_type=message.text)


async def create_payment_request(message: Message, state: FSMContext, payment_type: str):
    data = await state.get_data()
    
    payment_data = {
        "amount": data["amount"],
        "type": payment_type,
        "status": "paid"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{config.api_url}/orders/{data['order_id']}/payment",
                json=payment_data
            ) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    await state.clear()
                    await message.answer(
                        f"Платеж успешно создан\n"
                        f"ID: {result.get('id')}\n\n"
                        "Возвращайтесь в главное меню",
                        reply_markup=get_orders_menu()
                    )
                else:
                    await message.answer(
                        f"Ошибка при создании платежа:\n{result.get('detail', 'Неизвестная ошибка')}"
                    )
        except Exception as e:
            await message.answer(f"Ошибка: {str(e)}")