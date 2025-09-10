from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from loader import dp, db, bot
from aiogram.filters import CommandStart
from keyboard_buttons.inline.menu import menu
from states.register import Register
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from keyboard_buttons.default.menu import location_keyboard
from aiogram.utils.markdown import hbold
import re




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
    except Exception as e:
        print(f"Xatolik: {e}")
        await message.answer(
            text=f"Assalomu alaykum {full_name}! 👋",
            reply_markup=menu
        )



@dp.callback_query(F.data == "apply")
async def apply_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Ariza shaklini to'ldirishni boshlaymiz.\n\nIltimos, ismingizni kiriting:")
    await state.set_state(Register.first_name)
    await callback.answer()



@dp.message(Register.first_name)
async def process_firstname(message: types.Message, state: FSMContext):
    if len(message.text.strip()) < 2:
        await message.answer("⚠️ Iltimos, to'g'ri ism kiriting (kamida 2 ta belgi)")
        return

    await state.update_data(first_name=message.text.strip())
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(Register.last_name)


@dp.message(Register.last_name)
async def process_lastname(message: types.Message, state: FSMContext):
    if len(message.text.strip()) < 2:
        await message.answer("⚠️ Iltimos, to'g'ri familiya kiriting (kamida 2 ta belgi)")
        return

    await state.update_data(last_name=message.text.strip())
    await message.answer("📱 Telefon raqamingizni kiriting (masalan: +998901234567):")
    await state.set_state(Register.phone_number)



def is_valid_phone(phone):
    pattern = r'^\+998\d{9}$'
    return re.match(pattern, phone) is not None


@dp.message(Register.phone_number)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if not is_valid_phone(phone):
        await message.answer("⚠️ Iltimos, to'g'ri telefon raqam kiriting (masalan: +998901234567)")
        return

    await state.update_data(phone=phone)
    await message.answer("📧 Email manzilingizni kiriting:")
    await state.set_state(Register.email)


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@dp.message(Register.email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()

    if not is_valid_email(email):
        await message.answer("⚠️ Iltimos, to'g'ri email manzil kiriting (masalan: ism@example.com)")
        return

    await state.update_data(email=email)
    await message.answer(
        "🏠 Iltimos, yashash joyingizni yuboring:",
        reply_markup=location_keyboard
    )
    await state.set_state(Register.location)


@dp.message(Register.location, F.location)
async def process_location(message: types.Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude

    await state.update_data(location=f"{latitude},{longitude}")

    await message.answer(
        "🎓 Endi ta'lim va kasbiy ma'lumotlaringizni yuboring (DOC/DOCX yoki matn):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Register.education)


@dp.message(Register.location)
async def process_location_text(message: types.Message, state: FSMContext):
    if len(message.text.strip()) < 5:
        await message.answer("⚠️ Iltimos, to'liqroq manzil kiriting")
        return

    await state.update_data(location=message.text.strip())
    await message.answer(
        "🎓 Endi ta'lim va kasbiy ma'lumotlaringizni yuboring (DOC/DOCX yoki matn):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Register.education)


@dp.message(Register.education)
async def process_education(message: types.Message, state: FSMContext):
    if message.document:  
        doc = message.document
        if not (doc.file_name.endswith(".doc") or doc.file_name.endswith(".docx")):
            await message.answer("⚠️ Ta'lim va kasbiy ma'lumotlarni faqat DOC/DOCX formatda yuboring yoki matn kiriting.")
            return
        new_file_name = f"documents/{message.from_user.id}_education_{doc.file_name}"
        file = await bot.get_file(doc.file_id)
        await bot.download_file(file.file_path, destination=new_file_name)
        await state.update_data(education=new_file_name)
    else:  
        if len(message.text.strip()) < 10:
            await message.answer("⚠️ Ta'lim haqida to'liqroq yozing yoki DOC/DOCX fayl yuboring.")
            return
        await state.update_data(education=message.text.strip())

    await message.answer("🗳 Endi siyosiy faoliyat tajribangizni yuboring (DOC/DOCX yoki matn):")
    await state.set_state(Register.political_exp)



@dp.message(Register.political_exp)
async def process_political(message: types.Message, state: FSMContext):
    if message.document:
        doc = message.document
        if not (doc.file_name.endswith(".doc") or doc.file_name.endswith(".docx")):
            await message.answer("⚠️ Siyosiy faoliyatni faqat DOC/DOCX formatda yuboring yoki matn kiriting.")
            return
        new_file_name = f"documents/{message.from_user.id}_political_{doc.file_name}"
        file = await bot.get_file(doc.file_id)
        await bot.download_file(file.file_path, destination=new_file_name)
        await state.update_data(political_exp=new_file_name)
    else:
        if len(message.text.strip()) < 5:
            await message.answer("⚠️ Tajribangizni to‘liqroq yozing yoki DOC/DOCX fayl yuboring.")
            return
        await state.update_data(political_exp=message.text.strip())

    await message.answer("✍️ Endi motivatsiya va maqsadingizni yuboring (DOC/DOCX yoki matn, kamida 150 so‘z):")
    await state.set_state(Register.motivation)


@dp.message(Register.motivation)
async def process_motivation(message: types.Message, state: FSMContext):
    if message.document:
        doc = message.document
        if not (doc.file_name.endswith(".doc") or doc.file_name.endswith(".docx")):
            await message.answer("⚠️ Motivatsiyani faqat DOC/DOCX formatda yuboring yoki matn kiriting.")
            return
        new_file_name = f"documents/{message.from_user.id}_motivation_{doc.file_name}"
        file = await bot.get_file(doc.file_id)
        await bot.download_file(file.file_path, destination=new_file_name)
        await state.update_data(motivation=new_file_name)
    else:
        text = message.text.strip()
        words = text.split()
        if len(words) < 150:
            await message.answer(f"⚠️ Matnda kamida 150 ta so‘z bo‘lishi kerak. Siz {len(words)} ta so‘z kiritdingiz.")
            return
        await state.update_data(motivation=text)

    await message.answer("📂 Endi CV faylingizni yuboring (faqat PDF formatda):")
    await state.set_state(Register.documents)


@dp.message(Register.documents, F.document)
async def process_cv(message: types.Message, state: FSMContext):
    doc = message.document
    if not doc.file_name.endswith(".pdf"):
        await message.answer("⚠️ CV faqat PDF formatda yuborilishi kerak.")
        return

    new_file_name = f"documents/{message.from_user.id}_CV_{doc.file_name}"
    file = await bot.get_file(doc.file_id)
    await bot.download_file(file.file_path, destination=new_file_name)

    await state.update_data(documents=new_file_name)

    await save_application_data(message, state)



@dp.message(Register.documents)
async def wrong_cv(message: types.Message):
    await message.answer("⚠️ CV faqat PDF fayl sifatida yuborilishi kerak.")


async def save_application_data(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        db.add_application(
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data["phone"],
            email=data["email"],
            address=data["location"],
            education=data["education"],      
            political_exp=data["political_exp"], 
            motivation=data["motivation"],   
            documents=data.get("documents"),  
            telegram_id=message.from_user.id
        )

        application_text = f"""
✅ Arizangiz muvaffaqiyatli qabul qilindi!

{hbold('Ma\'lumotlaringiz:')}
📌 Ism: {data['first_name']}
📌 Familiya: {data['last_name']}
📞 Telefon: {data['phone']}
📧 Email: {data['email']}
🏠 Manzil: {data['location']}
🎓 Ta'lim: {"Fayl" if str(data['education']).startswith("documents/") else data['education'][:50]}
🗳 Siyosiy tajriba: {"Fayl" if str(data['political_exp']).startswith("documents/") else data['political_exp'][:50]}
✍️ Motivatsiya: {"Fayl" if str(data['motivation']).startswith("documents/") else data['motivation'][:50]}
📎 CV: {"Yuklandi" if data.get('documents') else "Yo'q"}Tez orada siz bilan bog'lanamiz. Rahmat!
        """

        await message.answer(application_text)

    except Exception as e:
        print(f"Ma'lumotlarni saqlashda xatolik: {e}")
        await message.answer("⚠️ Arizangizni saqlashda xatolik yuz berdi. Iltimos, qayta urining.")
    finally:
        await state.clear()
