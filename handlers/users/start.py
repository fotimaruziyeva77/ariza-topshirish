from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from loader import dp, db
from aiogram.filters import CommandStart
from keyboard_buttons.inline.menu import menu  
from states.register import Register
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from keyboard_buttons.default.menu import location_keyboard


# /start komandasi
@dp.message(CommandStart())
async def start_command(message: Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name, telegram_id=telegram_id)  
        await message.answer(
            text=f"""Assalomu alaykum, {full_name}! 👋  

Siz tanlov dasturiga xush kelibsiz.  
Quyidagi tugmalardan birini tanlang:""",
            reply_markup=menu
        )
    except:
        await message.answer(
            text="Assalomu alaykum 👋",
            reply_markup=menu
        )


# 🔹 Ariza boshlash
@dp.callback_query(F.data == "apply")
async def apply_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Ariza shaklini to‘ldirishni boshlaymiz.\n\nIltimos, ismingizni kiriting:")
    await state.set_state(Register.first_name)
    await callback.answer()


# 🔹 Ism
@dp.message(Register.first_name)
async def process_firstname(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(Register.last_name)


# 🔹 Familiya
@dp.message(Register.last_name)
async def process_lastname(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("📱 Telefon raqamingizni kiriting:")
    await state.set_state(Register.phone_number)


# 🔹 Telefon
@dp.message(Register.phone_number)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("📧 Email manzilingizni kiriting:")
    await state.set_state(Register.email)


# 🔹 Email
@dp.message(Register.email)
async def process_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer(
        "🏠 Iltimos, yashash joyingizni yuboring:",
        reply_markup=location_keyboard
    )
    await state.set_state(Register.location)


# 🔹 Manzil (location tugma orqali)
@dp.message(Register.location, F.location)
async def process_location(message: types.Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude

    await state.update_data(location=f"{latitude},{longitude}")

    await message.answer(
        "🎓 Endi ta’lim va kasbiy ma’lumotlaringizni kiriting:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Register.education)


# 🔹 Ta’lim
@dp.message(Register.education)
async def process_education(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)
    await message.answer("🗳 Siyosiy faoliyat tajribangiz haqida yozing:")
    await state.set_state(Register.political_exp)


# 🔹 Siyosiy faoliyat
@dp.message(Register.political_exp)
async def process_political(message: types.Message, state: FSMContext):
    await state.update_data(political_exp=message.text)
    await message.answer("✍️ Motivatsiya va maqsadingizni yozing (kamida 150 so‘z):")
    await state.set_state(Register.motivation)


# 🔹 Motivatsiya (150 so‘zdan kam bo‘lmasligi kerak)
@dp.message(Register.motivation)
async def process_motivation(message: types.Message, state: FSMContext):
    words = message.text.split()
    if len(words) < 150:
        await message.answer("⚠️ Matnda kamida 150 ta so‘z bo‘lishi kerak. Iltimos, yana to‘liqroq yozing.")
        return
    await state.update_data(motivation=message.text)
    await message.answer("📂 Hujjatlaringizni yuboring (CV, tavsiyanoma PDF yoki DOC formatida):")
    await state.set_state(Register.documents)


# 🔹 Hujjat
@dp.message(Register.documents, F.document)
async def process_documents(message: types.Message, state: FSMContext):
    file_id = message.document.file_id
    await state.update_data(documents=file_id)

    data = await state.get_data()

    # 🔑 Full name yig‘ib olish
    full_name = f"{data['first_name']} {data['last_name']}"

    # 📌 Bazaga yozish
    db.add_application(
        full_name=full_name,
        phone=data["phone"],
        email=data["email"],
        address=data["location"],   
        education=data["education"],
        political_exp=data["political_exp"],
        motivation=data["motivation"],
        documents=data["documents"],
        telegram_id=message.from_user.id
    )

    await message.answer("✅ Arizangiz muvaffaqiyatli qabul qilindi!\nRahmat!")
    await state.clear()
