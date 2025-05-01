import asyncio
import logging
import sys
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import add_user_to_database

TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class UserForm(StatesGroup):
    ism = State()
    fam = State()
    tel_nomer = State()

async def send_help_message(message: types.Message, state_name: str):
    helps = {
        "ism": "Ismingizni kiriting (faqat harflardan iborat bo'lsin): Masalan: Muhammad Yusuf",
        "fam": "Familiyangizni kiriting (faqat harflardan iborat bo'lsin): Masalan: G'aybullayev",
        "tel_nomer": "Telefon raqamingizni kiriting: Masalan: +998998071134"
    }
    await message.answer(helps.get(state_name, "Yordam: Ma'lumotni to'g'ri kiriting!"))

def is_valid_name(name: str) -> bool:
    return bool(re.match(r"^[a-zA-Zа-яА-ЯёЁ\s'-]{3,}$", name.strip()))

def is_valid_surname(surname: str) -> bool:
    return bool(re.match(r"^[a-zA-Zа-яА-ЯёЁ\s'-]{3,}$", surname.strip()))

def is_valid_phone(phone: str) -> bool:
    return bool(re.match(r"^\+998[0-9]{9}$", phone))

@dp.message(StateFilter(UserForm.ism), Command("help"))
@dp.message(StateFilter(UserForm.ism), lambda m: m.text.lower() == "help")
async def help_ism(message: types.Message):
    await send_help_message(message, "ism")

@dp.message(StateFilter(UserForm.fam), Command("help"))
@dp.message(StateFilter(UserForm.fam), lambda m: m.text.lower() == "help")
async def help_fam(message: types.Message):
    await send_help_message(message, "fam")

@dp.message(StateFilter(UserForm.tel_nomer), Command("help"))
@dp.message(StateFilter(UserForm.tel_nomer), lambda m: m.text.lower() == "help")
async def help_tel(message: types.Message):
    await send_help_message(message, "tel_nomer")

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("👋 Salom! 👤Ismingizni kiriting:")
    await state.set_state(UserForm.ism)

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Jarayon bekor qilindi. Qayta boshlash uchun /start ni bosing.")

@dp.message(StateFilter(UserForm.ism))
async def process_ism(message: types.Message, state: FSMContext):
    if not is_valid_name(message.text):
        await send_help_message(message, "ism")
        return
    await state.update_data(ism=message.text.strip())
    await message.answer("👤Familiyangizni kiriting:")
    await state.set_state(UserForm.fam)

@dp.message(StateFilter(UserForm.fam))
async def process_fam(message: types.Message, state: FSMContext):
    if not is_valid_surname(message.text):
        await send_help_message(message, "fam")
        return
    await state.update_data(fam=message.text.strip())
    await message.answer("📞Telefon raqamingizni kiriting:")
    await state.set_state(UserForm.tel_nomer)

@dp.message(StateFilter(UserForm.tel_nomer))
async def process_tel(message: types.Message, state: FSMContext):
    if not is_valid_phone(message.text):
        await send_help_message(message, "tel_nomer")
        return
    await state.update_data(tel_nomer=message.text.strip())
    data = await state.get_data()

    add_user_to_database(data)  

    await message.answer(
        "✅ Ma'lumotlaringiz saqlandi!\n"
        f"👤 Ism: {data['ism']}\n"
        f"👤 Familiya: {data['fam']}\n"
        f"📞 Telefon: {data['tel_nomer']}\n\n"
        "🔄 Qayta ro'yxatdan o'tish uchun /start ni bosing."
    )
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())