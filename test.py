from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton




bot = Bot(token='KEY')
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


inline_kb = InlineKeyboardMarkup(row_width=2)
inline_btn_calories = InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories')
inline_btn_formulas = InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
inline_kb.add(inline_btn_calories, inline_btn_formulas)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    main_menu_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu_kb.add(types.KeyboardButton('Рассчитать'))
    main_menu_kb.add(types.KeyboardButton('Информация'))
    main_menu_kb.add(types.KeyboardButton('Купить'))
    await message.reply("Добро пожаловать! Выберите опцию:", reply_markup=main_menu_kb)



buy_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="КУПИТЬ", url="get_buying_list")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_catalog")]
    ]
)



@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    await message.reply("Выберите опцию:", reply_markup=inline_kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_text = ("Формула Миффлина-Сан Жеора:\n"
                    "Для мужчин:  10 * вес + 6.25 * рост - 5 * возраст + 5\n"
                    "Для женщин:  10 * вес + 6.25 * рост - 5 * возраст - 161")
    await call.message.reply(formula_text)


@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await call.message.reply("Введите свой возраст:")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Введите свой рост:")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.reply("Введите свой вес:")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    calories = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.reply(f"Ваша норма калорий: {calories} ккал в день.")
    await state.finish()


product_inline_kb = InlineKeyboardMarkup(row_width=4)
product_inline_kb.add(InlineKeyboardButton("ВитаминA", callback_data='product_buying'))
product_inline_kb.add(InlineKeyboardButton("ВитаминC", callback_data='product_buying'))
product_inline_kb.add(InlineKeyboardButton("ВитаминD", callback_data='product_buying'))
product_inline_kb.add(InlineKeyboardButton("ВитаминE", callback_data='product_buying'))


@dp.message_handler(text='Купить')
async def get_buying_list(message: types.Message):
    products = [
        {"title": "ВитаминA", "description": "Качество №1.", "price": 100,
         "image_url": "https://avatars.mds.yandex.net/i?id=fc5f93906c5f437a41af5f6f63b2a8c8_l-4557823-images-thumbs&n=13"},
        {"title": "ВитаминC", "description": "Импортная.", "price": 200,
         "image_url": "https://avatars.mds.yandex.net/i?id=b4e0443925eb63d098dd7b5af03be7a3f3805c78-5827319-images-thumbs&n=13"},
        {"title": "ВитаминD", "description": " БАД", "price": 300,
         "image_url": "https://avatars.mds.yandex.net/i?id=9a0beb2c167418ed2573e3d6402add21e3071217-9065826-images-thumbs&n=13"},
        {"title": "ВитаминE", "description": " *НОВИНКА*.", "price": 400,
         "image_url": "https://avatars.mds.yandex.net/i?id=134429f8e133375f47a92b6efeeaf2e6de884bee-5086932-images-thumbs&n=13"}
    ]

    for product in products:
        await message.reply(
            f"Название: {product['title']} | Описание: {product['description']} | Цена: {product['price']}")
        await message.reply_photo(product['image_url'])

    await message.reply("**********", reply_markup=product_inline_kb)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.reply("Вы успешно приобрели продукт!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
