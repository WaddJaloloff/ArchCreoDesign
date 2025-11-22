import sys
import os

# STEP 1: Django settings path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archcreodesign.settings')

# STEP 2: Django init
import django
django.setup()

# STEP 3: Django model va boshqa importlar (shu yerda import qiling)
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InputMediaPhoto
)
from collections import defaultdict
import threading
import sqlite3, re, traceback, requests, os, time, telebot

# STEP 4: Django model importlari – django.setup() DAN KEYIN!
from app.models import Loyihalar, Kategoriyalar, telegram_user

# STEP 5: Bot ishga tushirish
bot = telebot.TeleBot("7484059552:AAGE2NqR-vwBEoxvnCzCP4v_c6ytMceNLbQ", parse_mode='HTML')




Instagram = "[Instagram](https://www.instagram.com/wadd_jaloloff/)"
Facebook = "[Facebook](http://fb.me/oqtepalavash.official)"
Sayt = "[Sayt](https://www.pizzabot.com/)"
joylashuvi = None
tsoni = 1
adminlar = [7274836900, 1393009, 6565325969]
group_id = -4537441210






user_last_message = {}





@bot.message_handler(commands=["start"])
def send_welcome(message):
    if message.chat.type == "private":
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        username = message.from_user.username

        # Foydalanuvchini bazadan olish yoki yaratish
        user, created = telegram_user.objects.get_or_create(user_id=user_id)

        if created:
            user.first_name = first_name
            user.username = username
            user.save()

        if not user.first_name:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(KeyboardButton(first_name))
            bot.send_message(message.chat.id, "Ismingizni kiriting!", reply_markup=markup)
            bot.register_next_step_handler(message, save_name)
        elif not user.telefon:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(KeyboardButton("📞 Telefon raqamni jonatish", request_contact=True))
            bot.send_message(
                message.chat.id,
                "Telefon raqamingizni yuboring\nMasalan: +998 55 111 22 11",
                reply_markup=markup,
            )
            bot.register_next_step_handler(message, update_phone)
        else:
            bosh_menu(message)

def save_name(message):
    user_id = str(message.from_user.id)
    name = message.text.strip()

    try:
        user = telegram_user.objects.get(user_id=user_id)
        user.first_name = name
        user.save()
        bot.send_message(message.chat.id, "✅ Ismingiz saqlandi!")
        send_welcome(message)
    except telegram_user.DoesNotExist:
        bot.send_message(message.chat.id, "❌ Foydalanuvchi topilmadi.")

def update_phone(message):
    try:
        phone_number = None
        if message.contact and message.contact.phone_number:
            phone_number = message.contact.phone_number
        elif message.text:
            phone_number = message.text.replace(" ", "")
            if not (phone_number.startswith("+998") and len(phone_number[4:]) == 9):
                bot.send_message(
                    message.chat.id,
                    "❗️Raqamni tog'ri formatda kiriting!\nMasalan: +998 55 111 22 11"
                )
                bot.register_next_step_handler(message, update_phone)
                return

        if phone_number:
            user_id = str(message.from_user.id)
            user = telegram_user.objects.get(user_id=user_id)
            user.telefon = phone_number
            user.save()

            bot.send_message(message.chat.id, "✅ Raqamingiz ham saqlandi!")
            send_welcome(message)

    except telegram_user.DoesNotExist:
        bot.send_message(message.chat.id, "❌ Foydalanuvchi topilmadi.")
    except Exception as e:
        print("Xatolik:", e)
        bot.send_message(message.chat.id, "Xatolik yuz berdi. Qaytadan urinib ko'ring.")
        bot.register_next_step_handler(message, update_phone)


def new_name_save(message):
    user_id = str(message.from_user.id)  # modelda user_id CharField bo'lgani uchun str qilamiz
    new_name = message.text.strip()

    if len(new_name) < 2:
        bot.send_message(message.chat.id, "Ism juda qisqa. Qaytadan kiriting:")
        bot.register_next_step_handler(message, new_name_save)
        return

    try:
        user = telegram_user.objects.get(user_id=user_id)
        user.first_name = new_name
        user.save()

        bot.send_message(
            message.chat.id,
            f"✅ Ismingiz muvaffaqiyatli yangilandi: <b>{new_name}</b>",
            parse_mode="HTML"
        )

        # Sozlamalar menyusiga qaytarish (agar kerak bo‘lsa)

        message.text = "⚙️ Sozlamalar"
        asosiydan(message)
    except telegram_user.DoesNotExist:
        bot.send_message(message.chat.id, "❌ Foydalanuvchi topilmadi.")
    except Exception as e:
        print("Ism saqlashda xatolik:", e)
        bot.send_message(message.chat.id, "❌ Ismingizni yangilashda xatolik yuz berdi. Qayta urinib ko‘ring.")
        

def bosh_menu(message):
    chat_id = message.chat.id
    if user_last_message.get(chat_id) == str(message.id):
        return
    user_last_message[chat_id] = str(message.id)
    bot.send_message(chat_id, "Asosiy Menu", reply_markup=asosiy_buttons(message.from_user.id))
    bot.register_next_step_handler(message, asosiydan)

def asosiy_buttons(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn2 = KeyboardButton("📋 Loyihalarimiz")
    btn3 = KeyboardButton("ℹ Biz haqimizda")
    btn4 = KeyboardButton("⚙️ Sozlamalar")
    btn5 = KeyboardButton("✍ Murojaat qilish")
    markup.add(btn2)
    markup.row(btn3, btn4)
    markup.add(btn5)

    return markup


def asosiydan(data):
    print("ishlavottimi1")
    # Tugma yoki xabar turini aniqlash
    if hasattr(data, "text"):  # Oddiy xabarlar
        message = data
        chat_id = message.chat.id
        message.text = message.text
    else:  # Callback tugmalar
        message = data.message
        chat_id = message.chat.id
        message.text = data.data
    user_id = message.from_user.id if hasattr(data, "text") else data.from_user.id
    turi = 0 if hasattr(data, "text") else 1
    chat_id = message.chat.id

    # Foydalanuvchi oxirgi xabarini tekshirish
    if "/start" != user_last_message.get(chat_id) == message.text:
        return  # Javob qaytarmay chiqib ketadi
    if message.text != "📥 Savat":
        user_last_message[chat_id] = message.text

    if message.text == "📋 Loyihalarimiz":
        menu(message)


    elif message.text == "✍ Murojaat qilish":
        bot.send_message(chat_id=message.from_user.id, text="Izoh qoldiring. Sizning fikringiz biz uchun muhim !\nBekor qilish: /cancel", reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, fikrniYuborish)

    elif message.text == "⚙️ Sozlamalar":    
        user_id = str(message.from_user.id)  # CharField bo‘lgani uchun str qilish muhim
        chat_id = message.chat.id

        try:
            user = telegram_user.objects.get(user_id=user_id)
        except telegram_user.DoesNotExist:
            bot.send_message(chat_id, "Ma'lumotlar topilmadi.")
            return

        # Inline tugmalar
        markup = InlineKeyboardMarkup(row_width=2)
        message_text = ""
        buttons = []

        if user.first_name:
            message_text += f"Ism:  <b>{user.first_name}</b>"
            buttons.append(InlineKeyboardButton("✏️ Ism", callback_data="ism"))

        if user.telefon:
            message_text += f"\nTelefon:  <b>+{user.telefon}</b>"
            buttons.append(InlineKeyboardButton("✏️ Telefon", callback_data="telefon"))

        message_text += "\nMuloqot tili:  <b>🇺🇿 O'zbekcha</b>\n\nQuyidagilardan birini tanlang!"

        for i in range(0, len(buttons), 2):
            row_buttons = [buttons[i]]
            if i + 1 < len(buttons):
                row_buttons.append(buttons[i + 1])
            markup.row(*row_buttons)

        markup.add(InlineKeyboardButton("⬅️ Asosiy menuga", callback_data="Asosiy"))

        # Habar yuborish
        bot.send_message(chat_id, message_text, reply_markup=markup, parse_mode="HTML")

        # Agar kerak bo‘lsa, asosiy menyuga qaytish uchun handlerni saqlang
        bot.register_next_step_handler(message, asosiydan)

    elif message.text == "ℹ Biz haqimizda":
        Instagram = '<a href="https://www.instagram.com/arch_creo_design/">Instagram</a>'
        Facebook = '<a href="http://fb.me/">Facebook</a>'
        Sayt = '<a href="https://www.google.com/">Sayt</a>'

        text = (
            "<b>🏛 ARCH CREO DESIGN haqida!</b>\n\n"
            "📌 16 yillik tajriba\n"
            "📌 Interyer | Eksteryer | Landshaft dizayni\n"
            "📌 Ko‘p qavatli va xususiy uy loyihalari\n"
            "📌 O‘zbekiston va qo‘shni davlatlardagi mijozlar uchun!\n\n"
            "<b>Har bir loyiha</b> — bu biz uchun san’at, tafakkur va mukammallik uyg‘unligi.\n"
            "“Bizni kimligimizni bilmoqchi bo‘lsangiz – biz qurgan imoratlarga qarang.”\n"
            "— Sohibqiron Amir Temur.\n\n"
            "🎯 Siz orzu qilgan loyihani biz haqiqatga aylantiramiz!\n"
            f"{Sayt} | {Facebook} | {Instagram}"
        )

        bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )


        bot.register_next_step_handler(message, asosiydan)

    elif message.text and message.text.lower() == "/start":
        send_welcome(message)
        
    else:
        bot.register_next_step_handler(message, asosiydan)



def fikrniYuborish(message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "Bekor qilindi!")
        bosh_menu(message)
        return
    else:
        if not adminlar:
            print(1)
            bot.send_message(message.chat.id, "❌ Ichki tizim hatoligi!1")
            send_welcome(message)
            return

        muvaffaqiyatli_yuborildi = False
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
                                "🔁 Javob berish",
                                callback_data=f"FikrgaJavobQaytarish{message.from_user.id}"))
        for admin_id in adminlar:
            try:
                bot.send_message(admin_id, f"📨 Yangi xabar bor!\n\n{message.text}", reply_markup=markup)
                muvaffaqiyatli_yuborildi = True  # Agar hech bo‘lmaganda bitta xabar yuborilsa, True bo‘ladi
                break
            except Exception as e:
                print(f"Xatolik: {e}")  # Konsolga xatolikni chiqarish (faqat debugging uchun)

        if muvaffaqiyatli_yuborildi:
            bot.send_message(message.chat.id, "<b>✅ Murojaatingiz administratsiyaga yuborildi!\nTez orada sizga javob qaytaramiz!</b>", parse_mode="HTML")
            bosh_menu(message)
        else:
            bot.send_message(message.chat.id, "❌ Ichki tizim hatoligi!2")
            print(0)
            send_welcome(message)
            return





def split_text(text, max_length=4096):
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]

def parse_coordinates(value):
    try:
        lat, lon = map(float, value.split(","))
        return lat, lon
    except ValueError:
        return None



from django.db import models
from django.db.models import Count

def menu(input_data):
    message = getattr(input_data, 'message', input_data)
    chat_id = message.chat.id

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    qs = (Loyihalar.objects.filter(Active=True)
          .values('Kategoriyasi__Nomi')
          .annotate(count=Count('id')))

    buttons = [KeyboardButton(f"{c['Kategoriyasi__Nomi']} ({c['count']})") for c in qs]

    if buttons:
        if len(buttons) > 2:
            markup.add(buttons[0])
            for i in range(1, len(buttons), 2):
                markup.add(*buttons[i:i+2])
        else:
            markup.row(*buttons)

    markup.add(KeyboardButton("🔙 Orqaga qaytish"))
    bot.send_message(chat_id, "Tanlashingiz mumkin:", reply_markup=markup)
    bot.register_next_step_handler(message, menudan)


def menudan(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if user_last_message.get(chat_id) == text:
        return bot.register_next_step_handler(message, menudan)
    
    user_last_message[chat_id] = text

    if text.lower() == "/start":
        return send_welcome(message)

    category_names = list(Kategoriyalar.objects.values_list('Nomi', flat=True))
    pattern = rf"({'|'.join(re.escape(n) for n in category_names)}) \(\d+\)"
    
    if re.fullmatch(pattern, text):
        return category(message, message.from_user.id)

    if text == "🔙 Orqaga qaytish":
        return bosh_menu(message)

    bot.register_next_step_handler(message, menudan)


def category(message, user_id, orqagaQaytish=False):
    chat_id = message.chat.id
    text = message.text.rsplit(" (", 1)[0]

    try:
        cat = Kategoriyalar.objects.get(Nomi=text)
    except Kategoriyalar.DoesNotExist:
        return bot.send_message(chat_id, "Bunday kategoriya topilmadi.")

    projects = Loyihalar.objects.filter(Kategoriyasi=cat).only("id", "Nomi", "Active")
    if not projects.exists():
        return bot.send_message(chat_id, "Bu kategoriyada loyiha mavjud emas.")

    dict_1, all_btns, act_btns = {}, [], []

    for p in projects:
        label = p.Nomi if p.Active else f"❗️{p.Nomi}"
        dict_1[label] = p.id
        btn = KeyboardButton(label)
        all_btns.append(btn)
        if p.Active:
            act_btns.append(btn)

    btns = act_btns if act_btns else all_btns

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for i in range(0, len(btns), 2):
        markup.add(*btns[i:i+2])
    markup.add(KeyboardButton("🔙 Menuga qaytish"))

    if len(btns) == 1 and not orqagaQaytish:
        single = btns[0]
        message.text = single.text
        bot.send_message(chat_id, f"{text} da faqat 1ta loyiha: <b>{single.text}</b>",
                         parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        return product(message, dict_1)

    try:
        if cat.rasmni and os.path.exists(cat.rasmni.path):
            with open(cat.rasmni.path, "rb") as img:
                bot.send_photo(chat_id, img, caption=text, reply_markup=markup)
        else:
            raise FileNotFoundError("Kategoriya rasmi topilmadi.")
    except Exception as e:
        print(f"[Xato] Kategoriya rasmi: {e}")
        bot.send_message(chat_id, text, reply_markup=markup)

    bot.register_next_step_handler(message, lambda msg: product(msg, dict_1))


def product(message, dict_1=None):
    chat_id = message.chat.id
    label = message.text.strip()

    if user_last_message.get(chat_id) == label:
        return bot.register_next_step_handler(message, lambda m: product(m, dict_1))
    
    user_last_message[chat_id] = label

    if label == "🔙 Menuga qaytish":
        message.text = "📋 Loyihalarimiz"
        return menu(message)

    proj_id = dict_1.get(label)
    if not proj_id:
        return bot.register_next_step_handler(message, lambda m: product(m, dict_1))

    try:
        p = Loyihalar.objects.get(pk=proj_id)
    except Loyihalar.DoesNotExist:
        return bot.send_message(chat_id, "Loyiha topilmadi.")

    media_group = []

    for fname in ('Rasm_1', 'Rasm_2', 'Rasm_3', 'Rasm_4', 'Rasm_5', 'Rasm_6'):
        img = getattr(p, fname)
        if img and hasattr(img, 'path') and os.path.exists(img.path):
            try:
                media_group.append(InputMediaPhoto(open(img.path, 'rb')))
            except Exception as e:
                print(f"[Xato] Rasm yuklash: {e}")

    if media_group:
        try:
            bot.send_media_group(chat_id, media_group)
        except Exception as e:
            print(f"[Xato] Media group yuborilmadi: {e}")

    bot.send_message(chat_id,
                     f"Nomi: <b>{p.Nomi}</b>\n\nTavsif: {p.Tavsifi}",
                     parse_mode="HTML",
                     reply_markup=productTugma(p.id))

    bot.register_next_step_handler(message, lambda m: product(m, dict_1))


@bot.callback_query_handler(func=lambda call: True)
def call(callback):
    print("Callback data: ", callback.data)

    if callback.data == "yopish":
        bot.delete_message(callback.message.chat.id, callback.message.message_id)


    elif callback.data == "Orqaga":
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        menu(callback.message)

    elif callback.data == "Asosiy":
        message = callback.message
        message.from_user.id = callback.from_user.id
        print(f"from_user_id: {message.from_user.id}")
        bot.delete_message(message.chat.id, message.message_id)
        bosh_menu(message)


    elif callback.data.startswith("Product"):
        user_id = callback.from_user.id
        ProductId = callback.data.split("Product")[1]
        markup = productTugma(ProductId)
        bot.edit_message_reply_markup(
            callback.message.chat.id, callback.message.message_id, reply_markup=markup
        )

    elif callback.data.startswith("category_"):
        bot.clear_step_handler(callback.message)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        data = callback.data.split("_")[1]
        print(f"data {data}")
        user_last_message[callback.message.chat.id] = "⬅️Orqaga"
        callback.message.text = data
        category(callback.message, callback.from_user.id, orqagaQaytish=True)





    elif callback.data == "telefon":
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("📞 Telefon raqamni kiritish", request_contact=True))
        markup.add(KeyboardButton("⬅️Orqaga"))
        bot.send_message(
            callback.message.chat.id,
            "Telefon raqamingizni yuboring!",
            reply_markup=markup,
        )
        bot.register_next_step_handler(callback.message, update_phone)

    elif callback.data == "ism":
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, "Ismingizni kiriting: ", reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(callback.message, new_name_save)


    elif callback.data.startswith("FikrgaJavobQaytarish"):
        try:
            CustomerId = callback.data.split("FikrgaJavobQaytarish", 1)[1]
            message_id = callback.message.message_id  # Asl xabar ID'si
            data = f"{CustomerId}//{message_id}"

            print(f"data {data}")  # Konsolda tekshirish uchun

            msg = bot.send_message(callback.message.chat.id, "Javobni shu yerga yozing!\nBekor qilish: /cancel", reply_markup=ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, FikrgaJavobniYuborish, data)

        except Exception as e:
            bot.send_message(callback.message.chat.id, "❌ Xatolik yuz berdi!")
            print(f"Xatolik: {e}")





def FikrgaJavobniYuborish(message, data):
    print("ket2")
    try:
        CustomerId, message_id = data.split("//")
        message_id = int(message_id)  # ID larni butun son ko‘rinishiga o‘tkazish

        if message.text == "/cancel":
            bot.send_message(message.chat.id, "Bekor qilindi!")
            return

        print("ket")
        try:
            # Javobni guruhga yuborish
            bot.send_message(CustomerId, f"<b>Administratsiya Javobi:</b>\n\n{message.text}", parse_mode="HTML")
            bot.send_message(message.chat.id, "✅ Javob muvaffaqiyatli yuborildi!")

        except Exception as e:
            bot.send_message(message.chat.id, "❌ Ichki tizim hatoligi!")
            print(f"Xatolik send_message: {e}")

        try:
            bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        except Exception as e:
            print(f"Xatolik delete_message: {e}")

        bosh_menu(message)

    except Exception as e:
        print(f"Xatolik FikrgaJavobniYuborish: {e}")




def productTugma(ProductId):
    try:
        p = Loyihalar.objects.get(id=ProductId)
        markup = InlineKeyboardMarkup()
        btn6 = InlineKeyboardButton(f"🔙 {p.Kategoriyasi.Nomi}", callback_data=f"category_{p.Kategoriyasi.Nomi}")
        markup.add(btn6)
        return markup
    except:
        pass



def Reasosiy():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("⬅️Asosiy menu"))
    return markup


def run_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except requests.exceptions.RequestException as e:
            print(f"Xatolik: {e}")
            time.sleep(5)
        except KeyboardInterrupt:
            print("Bot to'xtatilmoqda...")
            bot.stop_polling()  # Botni to'xtatish
            break  # while True siklidan chiqish
        except Exception as e:
            print(f"Xato: {e}")
            traceback.print_exc()  # Xato tafsilotlarini chiqarish
            time.sleep(5)

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("Bot to'xtatildi!")
        bot.stop_polling()
