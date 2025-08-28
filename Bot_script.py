import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from config import API_TOKEN


API_TOKEN = "8429987254:AAFMrTQ-gZQs7_8OP9_bvQXdC61xK82B3ZQ"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- СТАНИ калькулятора ---
class CalcStates(StatesGroup):
    waiting_for_num1 = State()
    waiting_for_num2 = State()
    waiting_for_action = State()

# --- Головне меню кнопок ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Привіт 👋")],
        [KeyboardButton(text="Смайлик 😎")],
        [KeyboardButton(text="Калькулятор")],
        [KeyboardButton(text="Допомога ❓")]
    ],
    resize_keyboard=True
)

# --- Налаштування команд ---
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="help", description="Список команд"),
        BotCommand(command="echo", description="Повторю твої слова"),
        BotCommand(command="count", description="Порахую символи"),
        BotCommand(command="smile", description="Надішлю смайлик"),
        BotCommand(command="calculator", description="Калькулятор"),
    ]
    await bot.set_my_commands(commands)

# /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт 👋!\n"
        "Я тестовий бот 🤖\n\n"
        "Вибери дію з меню нижче ⬇️",
        reply_markup=main_menu
    )

# /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Доступні команди:\n"
        "/start – привітання\n"
        "/help – список команд\n"
        "/echo – повторю твої слова\n"
        "/count – порахую символи\n"
        "/smile – відправлю смайлик\n"
        "/calculator – калькулятор"
    )

# /echo
@dp.message(Command("echo"))
async def echo_command(message: types.Message):
    await message.answer("Введи будь-що, і я повторю!")

# /count
@dp.message(Command("count"))
async def count_command(message: types.Message):
    text = message.text.replace("/count", "").strip()
    if text:
        await message.answer(f"У твоєму тексті {len(text)} символів 📊")
    else:
        await message.answer("Напиши так: /count твій_текст")

# /smile
@dp.message(Command("smile"))
async def smile_command(message: types.Message):
    await message.answer("😎🔥✨")

# --- Калькулятор ---
@dp.message(Command("calculator"))
async def calculator_start(message: types.Message, state: FSMContext):
    await message.answer("Введи перше число:")
    await state.set_state(CalcStates.waiting_for_num1)

@dp.message(CalcStates.waiting_for_num1)
async def calculator_num1(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введи число ❗")
        return
    await state.update_data(num1=int(message.text))
    await message.answer("Добре ✅ Тепер введи друге число:")
    await state.set_state(CalcStates.waiting_for_num2)

@dp.message(CalcStates.waiting_for_num2)
async def calculator_num2(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введи число ❗")
        return
    await state.update_data(num2=int(message.text))
    await message.answer("Яку дію виконати? (+, -, *, /, %)")
    await state.set_state(CalcStates.waiting_for_action)

@dp.message(CalcStates.waiting_for_action)
async def calculator_action(message: types.Message, state: FSMContext):
    data = await state.get_data()
    num1 = data["num1"]
    num2 = data["num2"]
    action = message.text.strip()

    if action == "+":
        result = num1 + num2
    elif action == "-":
        result = num1 - num2
    elif action == "*":
        result = num1 * num2
    elif action == "/":
        if num2 == 0:
            await message.answer("❌ На нуль ділити не можна")
            await state.clear()
            return
        result = num1 / num2
    elif action == "%":
        result = num1 % num2
    else:
        await message.answer("Дозволені тільки дії: +, -, *, /, %")
        return

    await message.answer(f"📊 Результат: {num1} {action} {num2} = {result}")
    await state.clear()

# --- Обробка кнопок з меню ---
@dp.message()
async def handle_text(message: types.Message):
    if message.text == "Привіт 👋":
        await message.answer("Привіт, радий тебе бачити! 😊")
    elif message.text == "Смайлик 😎":
        await message.answer("🔥✨💯")
    elif message.text == "Калькулятор":
        await calculator_start(message, dp.fsm.get_context(bot, message.chat.id, message.from_user.id))
    elif message.text == "Допомога ❓":
        await cmd_help(message)
    else:
        await message.answer(f"Ти написав: {message.text}")

# запуск
async def main():
    await set_commands(bot)  # <<< ВАЖЛИВО! Додаємо команди в меню
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
