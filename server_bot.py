
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    LabeledPrice,
    Location,
)
import sqlite3, re, traceback, requests, os, time, telebot, math
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import googlemaps
from geopy.distance import geodesic


# AIzaSyDIbzNUYOu2QRbxP45wk2YfLHndauvwOh0
payme_provider_token = "371317599:TEST:1728755041870"
click_provider_token = "398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065"
bot = telebot.TeleBot("7484059552:AAFJVOKnQyIZhX_g68WxUAHif2G59ybyvH0")
emoji_mapping = {str(i): f"{i}️⃣" for i in range(10)}


def convert_to_emoji(number):
    return "".join(emoji_mapping[digit] for digit in str(number))


GOOGLE_MAPS_API_KEY = "AIzaSyDIbzNUYOu2QRbxP45wk2YfLHndauvwOh0"
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
geolocator = Nominatim(user_agent="myPizzaBot/1.0")

Instagram = "[Instagram](https://www.instagram.com/wadd_jaloloff/)"
Facebook = "[Facebook](http://fb.me/oqtepalavash.official)"
Sayt = "[Sayt](https://www.pizzabot.com/)"
joylashuvi = None
tsoni = 1
adminlar = [8093652182, 7274836900, 6565325969]
ism = ""
kopinchadata = None
locations = {
    "Samarqand": (39.65417, 66.95972),
    "Toshkent": (41.2995, 69.2401),
    "Buxoro": (39.77472, 64.42861),
    "Uzo": (41.162371, 69.235349),
}
group_id = -4537441210


def createuserdatabase():
    con = sqlite3.connect('Architect.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS MAHSULOTLAR (
                    ProductId INTEGER PRIMARY KEY AUTOINCREMENT,
                    name text,
                    about text,
                    category text,
                    active INTEGER DEFAULT 1,
                    joylashuv TEXT
    )"""
    )

    cur.close()
    con.close()


    con = sqlite3.connect('Architect.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS users(
                	id integer,
                    name text,
                    phone_number integer
    )"""
    )
    cur.close()
    con.close()





createuserdatabase()
product_data = {}



def yangi(message):
    global product_data
    product_data = {}
    id = message.from_user.id
    if id in adminlar:
        chat_id = message.chat.id
        product_data[chat_id] = {}
        bot.send_message(
            chat_id, "Mahsulot nomini kiriting:\n\nBekor qilish uchun: /cancel", reply_markup=ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, get_product_name)

user_last_message = {}





@bot.message_handler(commands=["start"])
def send_welcome(message):
    if message.chat.type == "private":
        try:
            con = sqlite3.connect('Architect.db', check_same_thread=False)
            cur = con.cursor()
            user_id = message.from_user.id
            user_name = message.from_user.first_name
            print(user_id)

            row = cur.execute("SELECT name, phone_number FROM users WHERE id=?", (user_id,)).fetchone()
            if row:
                name, phone_number = row
            else:
                cur.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
                con.commit()
                name, phone_number = None, None

        finally:
            cur.close()
            con.close()

        # Telefon raqamni so'rash yoki bosh menyuga o'tish
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if not name:
            markup.add(KeyboardButton(user_name))
            bot.send_message(message.from_user.id, "Ismingizni kiriting!", reply_markup=markup)
            bot.register_next_step_handler(message, save_name)
        elif not phone_number:
            markup.add(KeyboardButton("📞 Telefon raqamni jonatish", request_contact=True))
            bot.send_message(
                user_id,
                "Telefon raqamingizni yuboring\nMasalan: +998 55 111 22 11",
                reply_markup=markup,
            )
            bot.register_next_step_handler(message, Update)
        else:
            bosh_menu(message)



def save_name(message):
    user_id = message.from_user.id
    name = message.text.strip()

    # Baza bloklanishining oldini olish uchun timeout qo‘shamiz
    con = sqlite3.connect("Architect.db", timeout=5)
    cur = con.cursor()

    try:
        if cur.rowcount == 0:  # Agar foydalanuvchi yo‘q bo‘lsa, yangi qo‘shish
            cur.execute("INSERT INTO users (id, name) VALUES (?, ?)", (user_id, name))
            con.commit()
        cur.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
        con.commit()
        bot.send_message(message.chat.id, "✅ Ismingiz saqlandi!")
        send_welcome(message)
    except sqlite3.OperationalError as e:
        bot.send_message(message.chat.id, f"❌ Ma'lumot saqlanmadi! Xato: {e}")
    finally:
        cur.close()
        con.close()



def bosh_menu(message):
    chat_id = message.chat.id
    if user_last_message.get(chat_id) == str(message.id):
        return
    user_last_message[chat_id] = str(message.id)
    bot.send_message(chat_id, "Asosiy Menu", reply_markup=asosiy_buttons(message.from_user.id))
    bot.register_next_step_handler(message, asosiydan)

def asosiy_buttons(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("👨🏻‍💻 Admin Panel")
    btn2 = KeyboardButton("📋 Loyihalarimiz")
    btn3 = KeyboardButton("ℹ Biz haqimizda")
    btn4 = KeyboardButton("⚙️ Sozlamalar")
    btn5 = KeyboardButton("✍ Fikr va Xabar")
    if user_id in adminlar:
        markup.add(btn1)
        markup.row(btn2, btn3)
        markup.add(btn4)
    else:
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


    elif message.text == "👨🏻‍💻 Admin Panel" and user_id in adminlar:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row(KeyboardButton("➕ Yangi mahsulot"), KeyboardButton("📋 E'lon yuborish"))
        markup.add(KeyboardButton("⬅️Orqaga"))
        bot.send_message(chat_id=message.from_user.id, text="Kerakli vazifani tanlang!", reply_markup=markup)
        bot.register_next_step_handler(message, admin_panel)


    elif message.text == "✍ Fikr va Xabar" and user_id not in adminlar:
        bot.send_message(chat_id=message.from_user.id, text="Izoh qoldiring. Sizning fikringiz biz uchun muhim !\nBekor qilish: /cancel", reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, fikrniYuborish)

    elif message.text == "⚙️ Sozlamalar":
        print("Nooodir ketitti moshin")
        con = sqlite3.connect('Architect.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id=?", (message.from_user.id,))
        row = cur.fetchone()
        cur.close()
        con.close()
        markup = InlineKeyboardMarkup(row_width=2)

        if row:
            id, name, phone = row[0], row[1], row[2]

            message_text = ""
            buttons = []
            if name:
                message_text += f"Ism:  <b>{name}</b>"
                buttons.append(InlineKeyboardButton("✏️ Ism", callback_data="ism"))

            if phone:
                message_text += f"\nTelefon:  <b>+{phone}</b>"
                buttons.append(InlineKeyboardButton("✏️ Telefon", callback_data="telefon"))

            message_text += "\nMuloqot tili:  <b>🇺🇿 O'zbekcha</b>\n\nQuyidagilardan birini tanlang!"

            # Add buttons to markup while ensuring there are no None values
            for i in range(0, len(buttons), 2):
                row_buttons = [buttons[i]]
                if i + 1 < len(buttons):
                    row_buttons.append(buttons[i + 1])
                markup.row(*row_buttons)

            markup.add(InlineKeyboardButton("⬅️Asosiy menuga", callback_data="Asosiy"))
            # Foydalanuvchiga habar yuborish
            bot.send_message(message.chat.id, message_text, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "Ma'lumotlar topilmadi")
        bot.register_next_step_handler(message, asosiydan)

    elif message.text == "ℹ Biz haqimizda":
        Instagram = "[Instagram](https://www.instagram.com//)"
        Facebook = "[Facebook](http://fb.me/)"
        Sayt = "[Sayt](https://www.Google.com/)"

        text = (
            "*Biz haqimizda\\!*  \n\n"
            "Lorem ipsum dolor sit, amet consectetur adipisicing elit"
            "Iure quo suscipit inventore necessitatibus dolorum qui aut quisquam,"
            "dolor quibusdam consectetur eius ad minima rem numquam nesciunt"
            "saepe eligendi officia quaerat\\!  \n\n"
            "*Ha aytgancha\\!*  "
            "Lorem ipsum dolor sit, amet consectetur adipisicing elit\\."
            "Iure quo suscipit inventore necessitatibus dolorum qui aut quisquam\\.  \n\n"
            "Murojaat uchun: \\+998 91 009 70 30  \n"
            f"{Sayt} \\| {Facebook} \\| {Instagram}"
        )

        bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2", disable_web_page_preview=True)
        bot.register_next_step_handler(message, asosiydan)




    elif message.text.lower() == "/start":
        send_welcome(message)
    else:
        bot.register_next_step_handler(message, asosiydan)


def admin_panel(message):
    if user_last_message.get(message.chat.id) == message.id:
        bot.register_next_step_handler(message, lambda msg: product(msg, message.from_user.id))
        return

    user_last_message[message.chat.id] = message.text

    if message.text == "➕ Yangi mahsulot":
        yangi(message)

    elif message.text == "📋 E'lon yuborish":
        handle_send(message)

    elif message.text == "⬅️Orqaga":
        bosh_menu(message)


def fikrniYuborish(message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "Bekor qilindi!")
        bosh_menu(message)
        return
    else:
        if not adminlar:
            print(1)
            bot.send_message(message.chat.id, "❌ Ichki tizim hatoligi!")
            send_welcome(message)
            return

        muvaffaqiyatli_yuborildi = False
        try:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(
                                "🔁 Javob berish",
                                callback_data=f"FikrgaJavobQaytarish{message.from_user.id}"))
            for admin_id in adminlar:
                bot.send_message(admin_id, f"📨 Yangi xabar bor!\n\n{message.text}", reply_markup=markup)
                muvaffaqiyatli_yuborildi = True  # Agar hech bo‘lmaganda bitta xabar yuborilsa, True bo‘ladi
        except Exception as e:
            print(f"Xatolik: {e}")  # Konsolga xatolikni chiqarish (faqat debugging uchun)

        if muvaffaqiyatli_yuborildi:
            bot.send_message(message.chat.id, "<b>✅ Murojaatingiz administratsiyaga yuborildi!\nTez orada sizga javob qaytaramiz!</b>", parse_mode="HTML")
            bosh_menu(message)
        else:
            bot.send_message(message.chat.id, "❌ Ichki tizim hatoligi!")
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


def handle_send(message):
    if message.from_user.id in adminlar:
        try:
            bot.send_message(message.chat.id, "Habarni yuborishingiz mumkin!\n\nBekor qilish uchun: /cancel")
            bot.register_next_step_handler(message, handle_send2)
        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")

def handle_send2(message):
    a = 0
    try:
        con = sqlite3.connect('Architect.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute('SELECT id FROM users')
        users = cur.fetchall()
        cur.close()
        con.close()

        if message.photo:
            file_id = message.photo[-1].file_id
            caption = message.caption or ''
            reply_markup = message.reply_markup

            for user in users:
                try:
                    bot.send_photo(user[0], photo=file_id, caption=caption, reply_markup=reply_markup or None)
                    a += 1
                except Exception as e:
                    print(f"Xatolik yuz berdi {user[0]} ga rasm yuborishda: {e}")
        else:
            if message.text.lower() == "/cancel":
                message.text = "👨🏻‍💻 Admin Panel"
                asosiydan(message)
                return
            print("ish bermadi")
            for user in users:
                try:
                    bot.send_message(user[0], message.text)
                    a += 1
                except Exception as e:
                    print(f"Xatolik yuz berdi {user[0]} ga xabarni forward qilishda: {e}")

        bot.reply_to(message, f"Habarlarni yuborish yakunlandi.\n{a} ta foydalanuvchilarga yuborildi.")
        message.text = "👨🏻‍💻 Admin Panel"
        asosiydan(message)
    except Exception as e:
        print(f"Umumiy xatolik: {e}")


def MahsulotQoshish(message):
    chat_id = message.chat.id
    if user_last_message.get(chat_id) == message.text:
        bot.register_next_step_handler(message, MahsulotQoshish)
        return
    user_last_message[chat_id] = message.text

    if message.text == "➕Mahsulot qo'shish":
        menu(message)
    else:
        bot.register_next_step_handler(message, MahsulotQoshish)






def menu(input_data):
    # Agar `input_data` CallbackQuery bo'lsa, `message`ni olish
    if hasattr(input_data, 'message'):
        message = input_data.message
    else:
        message = input_data  # Aks holda bu oddiy Message obyekti
    chat_id = message.chat.id

    print(f"wassup {user_last_message.get(chat_id)}")

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    # Ma'lumotlar bazasidan ma'lumot olish
    with sqlite3.connect('Architect.db') as con:
        cur = con.cursor()
        if message.from_user.id in adminlar:
            cur.execute("SELECT category, COUNT(*) FROM MAHSULOTLAR GROUP BY category")
        else:
            cur.execute("SELECT category, COUNT(*) FROM MAHSULOTLAR WHERE active=1 GROUP BY category")

        categories = cur.fetchall()
        cur.close()
    buttons = [
        KeyboardButton(f"{category} ({count})") for category, count in categories
    ]
    last_btn = KeyboardButton("🔙 Orqaga qaytish")
    if buttons:
        if len(buttons) > 2:
            markup.add(buttons[0])
            for i in range(1, len(buttons), 2):
                row = buttons[i:i + 2]
                markup.add(*row)
            markup.add(last_btn)
        elif len(buttons) == 2:
            markup.row(buttons[0], buttons[1])
            markup.add(last_btn)
        else:
            markup.row(buttons[0], last_btn)
    else:
        # buttons bo'sh bo'lsa, faqat "🔙 Orqaga qaytish" tugmasini qo'shamiz
        markup.add(last_btn)

    bot.send_message(chat_id=message.chat.id, text="Tanlashingiz mumkin:", reply_markup=markup)
    print(f"Tanlashingiz mumkin: {user_last_message.get(chat_id)}")
    bot.register_next_step_handler(message, menudan)


def menudan(message):
    user_id = message.from_user.id
    print(f"menudan {message.text}")

    chat_id = message.chat.id
    print("last step", user_last_message.get(chat_id))

    if user_last_message.get(chat_id) == message.text:
        bot.register_next_step_handler(message, menudan)
        return
    user_last_message[chat_id] = message.text
    print("heyyey2")

    con = sqlite3.connect('Architect.db', check_same_thread=False)
    cur = con.cursor()
    if user_id in adminlar:
        cur.execute("SELECT category FROM MAHSULOTLAR GROUP BY category")
    else:
        cur.execute("SELECT category FROM MAHSULOTLAR WHERE active = 1 GROUP BY category")
    categories = [row[0] for row in cur.fetchall()]
    cur.close()
    con.close()

    if message.text == "/start":
        send_welcome(message)
        return

    elif any(re.fullmatch(rf"{category} \((\d+)\)", message.text) for category in categories):
        print("ishal")
        category(message, user_id)


    elif message.text == "🔙 Orqaga qaytish":
        bosh_menu(message)

    elif message.text.lower() == "/start":
        send_welcome(message)

    elif message.text.lower() == "/send":
        handle_send(message)

    else:
        bot.register_next_step_handler(message, menudan)

def category(message, user_id, orqagaQaytish=False):
    print("def category")
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    con = sqlite3.connect('Architect.db', check_same_thread=False)
    cur = con.cursor()
    print(f"messagemiz {message.text}")
    category = message.text.rsplit(" (", 1)[0]  # Oxirgi so'zni olib tashlash
    print(f"ProductCategory {category}")
    cur.execute("SELECT * FROM MAHSULOTLAR WHERE category=?", (category,))
    barcha = cur.fetchall()
    cur.close()
    con.close()

    buttons, all_btn = [], []
    dict_1 = {}

    for i in barcha:
        if i[4] == 1:
            dict_1[i[1]] = i[0]
            buttons.append(KeyboardButton(i[1]))
            all_btn.append(KeyboardButton(i[1]))
        else:
            dict_1[f"❗️{i[1]}"] = i[0]
            all_btn.append(KeyboardButton(f"❗️{i[1]}"))
    tanlovlar = []
    if user_id in adminlar:
        for i in range(0, len(all_btn), 2):
            row = all_btn[i : i + 2]
            markup.add(*row)
            tanlovlar = all_btn
    else:
        for i in range(0, len(buttons), 2):
            row = buttons[i : i + 2]
            markup.add(*row)
            tanlovlar = buttons

    btn_back = KeyboardButton("🔙 Menuga qaytish")  # Orqaga tugmasi


    markup.add(btn_back)

    if len(tanlovlar) == 1 and orqagaQaytish == False:
        print("Hatosiz ishladiyu barbr")
        message.text = tanlovlar[0].text
        bot.send_message(message.chat.id, f"{category}da faqat 1ta mahsulot mavjud! <b>{message.text}</b>", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        product(message, dict_1)
        return

    else:
        category_photo_path = os.path.join("photo", category, "1.jpg")

        try:
            with open(category_photo_path, "rb") as file:
                bot.send_photo(message.chat.id, file, caption=category, reply_markup=markup)
        except FileNotFoundError:
            bot.send_message(message.chat.id, f"{category} uchun rasm topilmadi!")
        except Exception as e:
            print(f"Xatolik: {e}")
            bot.send_message(message.chat.id, category)

        bot.register_next_step_handler(message, lambda msg: product(msg, dict_1))


def product(message, dict_1 = None):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.text.lower() == "/start":
        send_welcome(message)
        return

    if user_last_message.get(chat_id) == message.text:
        bot.register_next_step_handler(message, lambda msg: product(msg, dict_1))
        return
    user_last_message[chat_id] = message.text

    if message.text.strip() in dict_1:
        ProductId = dict_1[message.text.strip()]

        user_id = message.from_user.id
        markup = InlineKeyboardMarkup()
        con = sqlite3.connect('Architect.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM MAHSULOTLAR WHERE ProductId=?", (ProductId,))
        ProductData = cur.fetchone()
        cur.close()
        con.close()
        markup = productTugma(ProductId, user_id)

        file_path = "" + os.path.join(ProductData[5].split("\\")[-1])
        print(f"file_path: {file_path}")
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                caption = ProductData[1]
                bot.send_photo(
                    message.chat.id,
                    photo=file,
                    caption=f"<b>{caption.title()}</b>\n\nTavsif: {ProductData[2]}",
                    reply_markup=markup,
                    parse_mode="HTML",
                )
        else:
            caption = ProductData[1]
            bot.send_message(message.chat.id,
            f"Fayl topilmadi!\n\n<b>{caption.title()}</b>\n\nTavsif: {ProductData[2]}",
                    reply_markup=markup,
                    parse_mode="HTML",)

        bot.register_next_step_handler(
            message, lambda msg: product(msg, dict_1)
        )


    elif message.text == "🔙 Menuga qaytish":
        message.text = "📋 Loyihalarimiz"
        print("keldi manga")
        menu(message)
        return

    else:
        bot.register_next_step_handler(message, lambda msg: product(msg, dict_1))



product_data = {}
# MAHSULOTLAR jadvalidan active mahsulotlarni olish
def get_active_products(category):
    con = sqlite3.connect('Architect.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("SELECT name, joylashuv FROM MAHSULOTLAR WHERE active = 1 AND category = ?", (category,),)
    active_products = [(row[0], row[1]) for row in cur.fetchall()]
    cur.close()
    con.close()
    return active_products


# Nomi ichidan maxsus belgilarni tozalash
def clean_name(name):
    return re.sub(r"[^\w\s]", "", name)


# Grid shaklida rasm yaratish funksiyasi
# def create_image_grid(image_paths, output_path, image_size=200):
#     def process_image(image_path):
#         with Image.open(image_path) as img:
#             min_side = min(img.size)
#             left = (img.width - min_side) / 2
#             top = (img.height - min_side) / 2
#             right = (img.width + min_side) / 2
#             bottom = (img.height + min_side) / 2
#             img = img.crop((left, top, right, bottom))
#             return img.resize((image_size, image_size), Image.LANCZOS)

#     images = []
#     for name, location in image_paths:
#         cleaned_name = clean_name(name)
#         image_path = os.path.join("./", location)
#         images.append((cleaned_name, process_image(image_path)))

#     total_images = len(images)
#     rows = math.ceil(math.sqrt(total_images))
#     cols = rows if rows * (rows - 1) < total_images else rows - 1

#     grid_width = cols * image_size
#     grid_height = rows * (image_size + 30)

#     grid_image = Image.new("RGB", (grid_width, grid_height), color=(255, 255, 255))
#     draw = ImageDraw.Draw(grid_image)
#     font = ImageFont.truetype("arial.ttf", 21)

#     for index, (name, image) in enumerate(images):
#         x = (index % cols) * image_size
#         y = (index // cols) * (image_size + 30)

#         grid_image.paste(image, (x, y))

#         # Rasm tagiga mahsulot nomini qo'shish
#         text_bbox = draw.textbbox((0, 0), name, font=font)
#         text_width = text_bbox[2] - text_bbox[0]
#         text_position = (x + (image_size - text_width) / 2, y + image_size + 5)
#         draw.text(text_position, name, fill="black", font=font)

#     grid_image.save(output_path, quality=95)


# Mahsulot ma'lumotlarini qayta ishlash qismi
def get_product_name(message):
    chat_id = message.chat.id
    if message.text.lower() == "/cancel":
        bot.send_message(chat_id, "Bekor qilindi!")
        message.text = "👨🏻‍💻 Admin Panel"
        asosiydan(message)
        return
    product_name = message.text
    product_data[chat_id] = {"name": product_name}
    bot.send_message(chat_id, "Mahsulot haqida ma'lumot kiriting:\n\nBekor qilish uchun: /cancel")
    bot.register_next_step_handler(message, get_product_about)


def get_product_about(message):
    chat_id = message.chat.id
    if message.text.lower() == "/cancel":
        bot.send_message(chat_id, "Bekor qilindi!")
        message.text = "👨🏻‍💻 Admin Panel"
        asosiydan(message)
        return
    try:
        product_data[chat_id]["about"] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        con = sqlite3.connect('Architect.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT DISTINCT category FROM MAHSULOTLAR")
        categories = cur.fetchall()
        cur.close()
        con.close()

        row = []
        for index, category in enumerate(categories):
            row.append(KeyboardButton(category[0]))
            if (index + 1) % 2 == 0:
                markup.add(*row)
                row = []
        if row:
            markup.add(*row)

        bot.send_message(
            chat_id,
            "Kategoriyalardan birini tanlang yoki yangi kategoriya yarating:\n\nBekor qilish uchun: /cancel",
            reply_markup=markup,
        )
        bot.register_next_step_handler(message, get_product_category)

    except:
        bot.send_message(chat_id, "Iltimos, ma'lumotni qaytadan kiriting!\n\nBekor qilish uchun: /cancel")
        bot.register_next_step_handler(message, get_product_about)


def get_product_category(message):
    chat_id = message.chat.id
    if message.text.lower() == "/cancel":
        message.text = "👨🏻‍💻 Admin Panel"
        asosiydan(message)
        return

    if user_last_message.get(chat_id) == message.text:
        return  # Javob qaytarmay chiqib ketadi

    user_last_message[chat_id] = message.text
    category = message.text
    product_data[chat_id]["category"] = category
    print(product_data[chat_id]["category"])
    bot.send_message(
        chat_id, "Mahsulotning rasmni yuboring:\n\nBekor qilish uchun: /cancel", reply_markup=ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(message, get_product_photo, category)


def get_product_photo(message, category):
    chat_id = message.chat.id
    if message.content_type == "photo":
        file_info = bot.get_file(message.photo[-1].file_id)
        photo_name = f"{file_info.file_id}.jpg"
        category = category.strip().replace("\\", "/")  # Kategoriya noto‘g‘ri formatda bo‘lsa to‘g‘rilaymiz
        category_path = os.path.join("photo", category)

        photo_location = os.path.join(category_path, photo_name)

        downloaded_file = bot.download_file(file_info.file_path)

        os.makedirs(category_path, exist_ok=True)
        with open(photo_location, "wb") as photo_file:
            photo_file.write(downloaded_file)
        print("photo_location",photo_location)
        product_data[chat_id]["photo"] = photo_location


        # Agar kategoriya rasmi mavjud bo‘lmasa, uni so‘raymiz
        category_photo_path = os.path.join(category_path, "1.jpg")
        if not os.path.exists(category_photo_path):
            bot.send_message(
                chat_id, "Kategoriya uchun rasm yuboring:",
                reply_markup=ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, get_category_photo, category)
        else:
            # Kategoriya rasmi bor, mahsulotni saqlashga o'tamiz
            add_product_to_db(chat_id)
            bot.send_message(chat_id, "Mahsulot muvaffaqiyatli saqlandi!")
            bosh_menu(message)
            return



    else:
        if message.text.lower() == "/cancel":
            message.text = "👨🏻‍💻 Admin Panel"
            asosiydan(message)
            return
        bot.send_message(chat_id, "Iltimos, mahsulot rasmini tog'ri formatda yuboring!\n\nBekor qilish uchun: /cancel")
        bot.register_next_step_handler(message, get_product_photo, category)



def get_category_photo(message, category):
    chat_id = message.chat.id
    if message.content_type == "photo":
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        category = category.strip().replace("\\", "/")  # Noto‘g‘ri ajratgichlarni to‘g‘rilash
        category_path = os.path.join("photo", category)
        category_photo_path = os.path.join(category_path, "1.jpg")

        print("category_path:", category_path)  # Tekshirish uchun
        print("category_photo_path:", category_photo_path)

        os.makedirs(category_path, exist_ok=True)
        with open(category_photo_path, "wb") as photo_file:
            photo_file.write(downloaded_file)

        # Endi mahsulotni bazaga saqlaymiz
        add_product_to_db(chat_id)
        bot.send_message(chat_id, "Mahsulot muvaffaqiyatli saqlandi!\nQayta boshlash uchun: /start")


    else:
        if message.text.lower() == "/cancel":
            message.text = "👨🏻‍💻 Admin Panel"
            asosiydan(message)
            return
        bot.send_message(chat_id, "Iltimos, mahsulot rasmini tog'ri formatda yuboring!\n\nBekor qilish uchun: /cancel")
        bot.register_next_step_handler(message, get_category_photo, category)



def add_product_to_db(chat_id):
    name = product_data[chat_id]["name"]
    about = product_data[chat_id]["about"]
    category = product_data[chat_id]["category"]
    photo = product_data[chat_id].get("photo", "")

    con = sqlite3.connect('Architect.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("INSERT INTO MAHSULOTLAR (name, about, category, joylashuv) VALUES (?, ?, ?, ?)", (name, about, category, photo),)
    con.commit()
    product_data.pop(chat_id, None)


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
        markup = productTugma(ProductId, user_id)
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

    elif callback.data.startswith("berkitish_"):
        id = callback.data.split("_", 1)[1]
        con = sqlite3.connect('Architect.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("UPDATE MAHSULOTLAR SET active=? WHERE ProductId =?", (0, id))
        con.commit()
        cur.close()
        con.close()

        con = sqlite3.connect('Architect.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM MAHSULOTLAR WHERE ProductId=?", (id,))
        ProductData = cur.fetchone()
        cur.close()
        con.close()

        bot.answer_callback_query(callback.id, "😶‍🌫️ Mahsulot berkitildi !")
        markup = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton("⬅️ Orqaga", callback_data=f"category_{ProductData[3]}")
        btn2 = InlineKeyboardButton("👀 Qaytarish", callback_data=f"korsatish_{ProductData[0]}")
        markup.row(btn1, btn2)
        chat_id = callback.message.chat.id
        message_id = callback.message.message_id
        bot.edit_message_reply_markup(
            chat_id=chat_id, message_id=message_id, reply_markup=markup
        )

    elif callback.data.startswith("korsatish_"):
        bot.answer_callback_query(callback.id, "⏳ Mahsulot menuga qo'shildi")
        ProductId = callback.data.split("_", 1)[1]
        user_id = callback.from_user.id

        con = sqlite3.connect('Architect.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("UPDATE MAHSULOTLAR SET active=? WHERE ProductId =?", (1, ProductId))
        con.commit()
        cur.execute("SELECT * FROM MAHSULOTLAR WHERE ProductId=?", (ProductId,))
        ProductData = cur.fetchone()
        cur.close()
        con.close()
        markup = productTugma(ProductId, user_id)
        try:
            chat_id = callback.message.chat.id
            message_id = callback.message.message_id
            bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=f"<b>{ProductData[1].title()}</b>\n\nTavsif: {ProductData[2]}",
                reply_markup=markup,
                parse_mode="HTML"
            )
        except Exception as e:
            bot.answer_callback_query(callback.id, "❌ Xatolik: " + str(e))

    elif callback.data.startswith("Admin"):
        ProductId = callback.data.split("Admin")[1]
        print(ProductId)
        markup = InlineKeyboardMarkup(row_width=2)
        btn1 = InlineKeyboardButton(
            "👀 Berkitish", callback_data=f"berkitish_{ProductId}"
        )
        btn3 = InlineKeyboardButton(
            "✏️ Tahrirlash", callback_data=f"tahrirlash_{ProductId}"
        )
        btn5 = InlineKeyboardButton("⬅️Orqaga", callback_data=f"Product{ProductId}")
        markup.add(btn1, btn3, btn5)
        bot.edit_message_reply_markup(
            callback.message.chat.id, callback.message.message_id, reply_markup=markup
        )

    elif callback.data.startswith("tahrirlash_"):
        ProductId = callback.data.split("_")[1]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn1 = KeyboardButton("Nomini tahrirlash")
        btn2 = KeyboardButton("Tavsifni tahrirlash")
        btn3 = KeyboardButton("🔙 Orqaga")
        btn4 = KeyboardButton("Rasmini tahrirlash")
        markup.row(btn1, btn2)
        markup.row(btn3, btn4)
        bot.send_message(
            callback.message.chat.id, "Mahsulotning ma'lumotini yangilash:", reply_markup=markup
        )
        bot.register_next_step_handler(callback.message, tahrirlashnuvchiMalumotniTanlash, ProductId)



    elif callback.data == "telefon":
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("📞 Telefon raqamni kiritish", request_contact=True))
        markup.add(KeyboardButton("⬅️Orqaga"))
        bot.send_message(
            callback.message.chat.id,
            "Telefon raqamingizni yuboring!",
            reply_markup=markup,
        )
        bot.register_next_step_handler(callback.message, Update)

    elif callback.data == "ism":
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, "Ismingizni kiriting: ", reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(callback.message, saveNewName)


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

def tahrirlashnuvchiMalumotniTanlash(message, ProductId):
        if message.text == "Nomini tahrirlash":
            message.text = "ism"
            ProductniYangiMalumotniSorash(message, ProductId)
        elif message.text == "Tavsifni tahrirlash":
            message.text = "tavsif"
            ProductniYangiMalumotniSorash(message, ProductId)
        elif message.text == "Rasmini tahrirlash":
            bot.send_message(message.from_user.id, "Yangilangan rasmni yuboring!")
            bot.register_next_step_handler(message, ProductRasminiYangilash, ProductId)

        elif message.text ==  "🔙 Loyihalarga":
            bosh_menu()
            return
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            btn1 = KeyboardButton("Nomini tahrirlash")
            btn2 = KeyboardButton("Tavsifni tahrirlash")
            btn3 = KeyboardButton("🔙 Orqaga")
            btn4 = KeyboardButton("Rasmini tahrirlash")
            markup.row(btn1, btn2)
            markup.row(btn3, btn4)
            bot.send_message(message.from_user.id, "Tahrirlanishi kerak bo'lgan qismni tanlng!", reply_markup=markup)
            bot.register_next_step_handler(message, tahrirlashnuvchiMalumotniTanlash, ProductId)

def ProductRasminiYangilash(message, ProductId):
    try:
        if message.content_type == "photo":
            # 1. Eng katta rasm versiyasining file_id ni olish
            file_id = message.photo[-1].file_id

            con = sqlite3.connect("Architect.db")
            cur = con.cursor()
            cur.execute("SELECT joylashuv FROM MAHSULOTLAR WHERE ProductId = ?", (ProductId,))
            result = cur.fetchone()
            cur.close()
            con.close()

            if result is None or result[0] is None:
                bot.send_message(message.chat.id, "❌ Rasm joylashuvi topilmadi!")
                return

            # 2. Baza ichidagi rasm nomi (papka bilan birga)
            image_path = result[0]

            # 3. Telegramdan rasmni olish
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # 4. Rasmni papkaga saqlash
            os.makedirs(os.path.dirname(image_path), exist_ok=True)  # Papkani yaratish (agar mavjud bo'lmasa)

            with open(image_path, "wb") as new_file:
                new_file.write(downloaded_file)

            bot.send_message(message.chat.id, f"✅ Rasm yangilandi!")
            message.text == "📋 Loyihalarimiz"
            menu(message)
        else:
            bot.send_message(message.from_user.id, "Rasmni tog'ri formatda yuboring!")
            bot.register_next_step_handler(message, tahrirlashnuvchiMalumotniTanlash, ProductId)



    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Xatolik: {str(e)}")


def ProductniYangiMalumotniSorash(message, ProductId):
    if message.text == "ism":
        bot.send_message(message.from_user.id, "Yangilangan nomni kiriting:")
    else:
        bot.send_message(message.chat.id, "Yangilangan tavsifni kiriting:")
    bot.register_next_step_handler(message, saveNewInfo, [message.text, ProductId])

def saveNewInfo(message, box):
    try:
        if len(box) < 2:
            bot.send_message(message.from_user.id, "❌ Ma'lumot yetarli emas!")
            message.text == "📋 Loyihalarimiz"
            menu(message)
            return

        turi, ProductId = box[0], box[1]
        column = "name" if turi == "ism" else "about"

        con = sqlite3.connect("Architect.db")
        cur = con.cursor()
        cur.execute(f"UPDATE MAHSULOTLAR SET {column} = ? WHERE ProductId = ?", (message.text, ProductId))
        con.commit()
        cur.close()
        con.close()

        bot.send_message(message.from_user.id, f"{'Nomi' if turi == 'ism' else 'Tavsif'} muvaffaqiyatli yangilandi!\nQayta boshlash: /start")

    except Exception as e:
        bot.send_message(message.from_user.id, f"❌ Ichki tizim hatoligi: {str(e)}")


def saveNewName(message):
    con = sqlite3.connect('Architect.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET name = ? WHERE id = ?", (message.text, message.from_user.id))
    con.commit()
    cur.close()
    con.close()
    message.text = "⚙️ Sozlamalar"
    asosiydan(message)

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
            bot.send_message(message.chat.id, "✅ Javob muvaffaqiyatli guruhga yuborildi!")

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


def yangi_narx(message, ProductId, message_id):
    try:
        value = float(message.text)
        con = sqlite3.connect('Architect.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("UPDATE MAHSULOTLAR SET narxi = ? WHERE ProductId = ?", (int(value), ProductId))
        con.commit()
        cur.close()
        con.close()

        con = sqlite3.connect('Architect.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM MAHSULOTLAR WHERE ProductId = ?", (ProductId,))
        ProductData = cur.fetchone()
        cur.close()
        con.close()

        markup = InlineKeyboardMarkup(row_width=2)
        btn1 = InlineKeyboardButton(
            "👀 Berkitish", callback_data=f"berkitish_{ProductId}"
        )
        btn3 = InlineKeyboardButton(
            "✏️ Narxini tahrirlash", callback_data=f"narxi_{ProductId}"
        )
        btn5 = InlineKeyboardButton("⬅️ Orqaga", callback_data=f"::{ProductData[3]}")
        markup.add(btn1, btn3, btn5)

        bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message_id,
            caption=f"<b>{ProductData[1].title()}</b>\n\nTavsif: {ProductData[2]}",
            reply_markup=markup,
            parse_mode="HTML",
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ Menuga", callback_data="Orqaga"))
        bot.send_message(message.chat.id, "✅ Narx yangilandi !", reply_markup=markup)
    except ValueError:
        bot.send_message(
            message.chat.id, "Iltimos, Narxini raqam ko'rinishida kiriting:"
        )
        bot.register_next_step_handler(message, lambda m: yangi_narx(m, ProductId, message_id))


def Update(message):
    try:
        phone_number = None
        if message.contact and message.contact.phone_number:
            phone_number = message.contact.phone_number
        elif message.text:
            phone_number = message.text.replace(" ", "")
            if phone_number.startswith("+998") and len(phone_number[4:]) == 9:
                pass
            else:
                bot.send_message(
                    message.chat.id,
                    "❗️Raqamni tog'ri formatda kiriting!\nMasalan: +998 55 111 22 11",
                )
                bot.register_next_step_handler(message, Update)
                return

        if phone_number is not None:
            user_id = message.from_user.id
            con = sqlite3.connect('Architect.db', check_same_thread=False)
            cur = con.cursor()
            cur.execute("UPDATE users SET phone_number= ? WHERE id= ?;", (phone_number, user_id))
            con.commit()
            cur.close()
            con.close()

            bot.send_message(message.chat.id, "✅ Raqamingiz ham saqlandi!")
            send_welcome(message)

    except Exception as e:
        print(f"Xato yuz berdi: {str(e)}")
        bot.send_message(
            message.chat.id,
            "Raqamni tog'ri formatda kiriting!\nMasalan: +998 55 111 22 11",
        )
        bot.register_next_step_handler(message, Update)

def productTugma(ProductId, user_id):
    try:
        con = sqlite3.connect('Architect.db', check_same_thread=False)
        cur = con.cursor()
        # cur.execute("UPDATE MAHSULOTLAR SET active=? WHERE ProductId =?", (1, ProductId))
        # con.commit()
        cur.execute("SELECT * FROM MAHSULOTLAR WHERE ProductId=?", (ProductId,))
        markup = InlineKeyboardMarkup()
        ProductData  = cur.fetchone()
        cur.close()
        con.close()

        btn6 = InlineKeyboardButton(f"🔙 {ProductData[3]}", callback_data=f"category_{ProductData[3]}")
        if ProductData[4] == 1:
            btn5 = InlineKeyboardButton(
                "👤 Admin", callback_data=f"Admin{ProductId}"
            )
        else:
            if user_id in adminlar:
                btn5 = InlineKeyboardButton(
                    "👀 Qaytarish", callback_data=f"korsatish_{ProductId}"
                )

        if user_id in adminlar:
                markup.row(btn6, btn5)
        else:
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