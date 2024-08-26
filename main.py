# yasaman sadeghi
import speech_recognition as sr
# برای افزودن رنگ به متن در خروجی خط فرمان
from colorama import init, Fore
# تعیین  رنگ در خط فرمان
from termcolor import colored
from translate import Translator
# تبدیل متن به صدا
import pyttsx3
import pandas as pd
import vanna as vn
from vanna.remote import VannaDefault
from vanna.flask import VannaFlaskApp
import pypyodbc as pdc
# ایجاد یک نمونه از VannaDefault با مدل و کلید API
vanna = VannaDefault(model='thelook', api_key='7eff7e353bf64a61adbaefb3360fdacc')

# اطلاعات اتصال به پایگاه داده
SERVER_NAME = 'DESKTOP-ABI87P6\\NEWMSSQLSERVER'  # نام سرور SQL Server
DATABASE_NAME = 'BarDB'  # نام دیتابیس

connection_string = f"""
DRIVER=ODBC Driver 17 for SQL Server;
SERVER={SERVER_NAME};
DATABASE={DATABASE_NAME};
Trusted_Connection=YES;
"""
try:
    db_conn = pdc.connect(connection_string)
except pdc.Error as ex:
    sqlstate = ex.args[1]
    print(Fore.RED+f"Error establishing connection: {sqlstate}")
    exit()

# تعریف تابع run_sql


def run_sql(sql: str) -> pd.DataFrame:
    df = pd.read_sql_query(sql, db_conn)
    return df

# تنظیم تابع run_sql در vanna


vn.run_sql = run_sql
vn.run_sql_is_set = True

# تابع برای پرسش و جو از کاربر


def online_speech_to_text():
    recognizer = sr.Recognizer()
    engine1 = pyttsx3.init()
    # مجوز استفاده از رنگها در خط فرمان
    init(autoreset=True)

    with sr.Microphone() as source:
        print("Be silent...")
        # حذف نویزهای اطراف
        recognizer.adjust_for_ambient_noise(source)
        print("Now speak :")
        audio = recognizer.listen(source, timeout=5)

    try:
        # دریافت صدا
        text0 = recognizer.recognize_google(audio, language="fa-IR")

        # ترجمه صدای دریافتی از فارسی به انگلیسی
        def translate(text, source_language='fa-IR', target_language='en'):
            translator = Translator(from_lang=source_language, to_lang=target_language)
            translation = translator.translate(text)
            return translation

        persian_text = text0
        english_translate = translate(persian_text)

        # نمایش فاصله به کاربر
        print(colored(Fore.GREEN + f"You said: {text0} "))
        print(colored(Fore.BLUE + f"English translate: {english_translate}"))

        # اجرای کوئری SQL
        df_information_schema = vn.run_sql(f"""
        SELECT distance FROM CityDistances WHERE origin = '{english_translate}' AND destination = '{english_translate}'
        """)
        plan = vn.get_training_plan_generic(df_information_schema)
        vn.train(plan=plan)
        vn.get_training_data()

        # پرسش از مدل و دریافت پاسخ
        distance = vn.ask(question=english_translate)

        # تنظیم تابع اجرای کوئری در vanna
        app = VannaFlaskApp(vn)
        app.run()

        print(colored(Fore.YELLOW + f"Distance between cities: {distance}"))

        # تشخیص متن
        engine1.say(text0)
        engine1.runAndWait()

    except sr.UnknownValueError:
        print(colored(Fore.RED + "I did not understand, repeat again"))
    except sr.RequestError:
        print(colored(Fore.RED + "Detection error, check your internet connection"))

# فراخوانی تابع برای دریافت صدا


online_speech_to_text()
