import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import random
import aiohttp
from telegram import InputFile
from io import BytesIO


BAD_WORDS = ['آشغال', 'عوضی', 'بی ناموس', 'جاکش', "کسکش", "خارکسده", "کونی", "کونده", "کسده", "جنده", "مادر جنده", "مادر خراب", "دیوث", "گوزو", "ریدی", "گاییدی", "گایید", "فاحشه", "فاهشه", "جنده پولی", "کس کش", "جا کش", "کو نی", "مادر سگ", "تخم سگ"]
warning_texts = ["ای بابا، ادب رو رعایت کن", "عه ، بی ادبی نکنید", "لطفا به هم دیگه احترام بزارین", "لطفا احترام یکدیگر رو رعایت کنید", "اوه! ، مودب باشین"]
    

JOKES= [
    "جفررر ﺍﻭﻣﺪ ﺍﺯ ﻫﻮﺍﭘﯿﻤﺎ ﭘﯿﺎﺩﻩ ﺷﻪ یهو ﺷﻠﻮﺍﺭﺵ ﺍﻓﺘﺎﺩ \nﺩﺍﺩ ﺯﺩ : \nﺣﺎﻻ ﺍﻭﻥ  گلﺧﺎﻧﻮﻣﯽ ﮐﻪ ﮔﻔﺖ\nﮐﻤﺮﺑﻨﺪﺍ ﺭﻭ ﺑﺎﺯ ﮐﻨﯿﺪ ﺑﯿﺎﺩ ﺟﻮﺍﺏ ﺑﺪﻩ ",
    "nیارو داخل هواپیما میره داخل کابین خلبان با تهدید میگه برو فرانکفورت.\nخلبان یه نگاهش بهش میکنه میگه پس اسلحه ات کو؟؟\nیارو میگه رفاقتی برو دیگه حتما باید زور بالا سرتون باشه",
    "جعفر تو اتوبوس یه کشیده گذاشت تو گوش بغل دستیش 🤛\n\nیارو ميگه:چرا میزنی من که چیزی نگفتم\n\nجعفر ميگه: مسیرطولانیه گفتم یه موقع گوه زیادی نخورى!",
    "با شلوارک میری تو آسانسور عکس میگیری لوکیشن میزنی دبی\n\nپشت سرتو نگاه کن نوشته استیل البرز 😐\n\nدر آسانسور بزنه تو کمرت ملعون",
    "هر وقت احساس تنهایی کردی ...\nپاشو يه فيلم ترسناک بزار نگاه کن !!!\nبعد فکر ميکني يکي تو اتاقه، يکی تو آشپز خونه هست، چند نفر هم تو حياطن !!!\nخلاصه از تنهایی در ميای 😂",
    "داروها وقتی میخوان حال یکی رو خوب کنن ، همیشه به شیاف میگن: ما محاصره‌اش میکنیم تو از در پشت وارد شو",
    "دیشب به نامزدم میگم سرم گیج میره همه چیو دو تا می بینم\nمیگه منم دوتا میبینی ؟ \nمیگم اره !\nمیگه خب کدوممون خوشگلتریم ؟",
    "از نظر راننده ها عابراى پياده يه مشت گوسفندن\n\n\nاز نظر عابراى پياده راننده ها يه مشت گاون خلاصه خيابون نيست كه دامداريه",
    "دختره عکسشو با سگش گذاشت اینستا 🐩😍\nپسره با خنده میگه کدومی؟ 😂\nدختره گفت اونی که تورو بغل کرده 😁\nو برای اولین بار پسری در دنیای مجازی، دختری را بلاک کرد\n\nو برای اولین بار پسری در دنیای مجازی، دختری را بلاک کرد",
    "این پیرمردای بالای صدسال که صداسیما میره باهاشون مصاحبه میکنه و میپرسه راز سلامتیتون چیه و اونام میگن پیاده روی و مصرف لبنیات.\nدروغ میگن همشون تریاک میکشن.",
    "حیف نون میره مراسم ختم زن دوستش...\nمیخواد با دوستش اظهار همدردی کنه... نمیدونه چی بگه\nمیگه:\nخدا بیامرزدش، زن تو نبود! زن هممون بود!",
    "مدرسه غلط کرده...\nچیست؟!!!!\nپاسخ منطقی والدین به دانش آموزان در مواجه با تقاضای پول برای مدرسه\nدهه شصتی ها میدونن چی میگم",
    "وقتی پسر و دختر باهم بیرون میرن:\n-این دختره که رد شد خوشگلتر بود یا من؟\n+اون (باختی!پاسخ اشتباه)\n+تو (باختی!پاسخ اشتباه)\n+کدوم دختره؟؟من که ندیدمش(پاسخ صحیح)",
    "یعنی شما بری عطاری بگی دوست پسر ندارم\nهم باز یه گیاهی بهت میده میگه اینو دم کن بخور....\nحل میشه",
    "جَمیله : عزیزم دکتر بهم گفت واسه اینکه حالم خوب بشه باید بریم به سفر خارج به یه ساحل آفتابی\nحالا منو کجا میبری؟\nحیف نون: یه دکتر دیگه!",
    "بادوست دخترم تصویری صحبت ميكردم گف ميخوام باهات چيزيو تجربه كنم كه با هيشكی تجربه نكردم\nگوشيو گذاشت تو يخچال گفت درو ميبندم\nبگو واقعا چراغ خاموش ميشه يانه",
    "دخترا :\nامروز یه نفر بهم دایرکت داد گفت روت کراش دارم \nدوستش : از بس دلبری دیگه\nپسرا :\nممد امروز یه دختر بهم دایرکت داد گفت روت کراش دارم\nممد : من بودم",
    "طرف از یه چایی کیسه ای ۷ تا چایی میگیره\nبعد اومده میگه چجوری میری تو آف لباس میخری\nهرچیزی بنجوله رو دستشون میمونه آف میزنن‌\nنکشیمون  اورجینال",
    "با یه دختر آشنا شدم\nهمش میگفت از پسرهای ورزشکار خیلی خوشم میاد\nدفعه اول با  دوبنده کُشتی  رفتم\nسر قرار منو که دید در رفت\nفکر‌ کنم فوتبالی بود 🤔",
    "حیف نون گردن یکی از مسئولین  اختلاس گر رو بوسید ...\nمسئولِ گفت : همه دست مارو می بوسند تو چرا گردن مارو می بوسی ؟\nحیف نون گفت : جای شمشیر امام زمانو میبوسم",
    "داشتن مدرک تحصیلی تو ایران عین شُرت میمونه …\nداشتنش هنر نیست ولی نبودنش عیبه",
    "غضنفر رفت دستشویی\nیکی داد زد اب داره قطع میشه\nغضنفر هول شد اول کـونشو شست بعد ریــد",
    "دخترای خارج با نگاه، نشون میدن که عاشقت شدن\nولی دخترای ایران چنان نگات میکنن و در گوش هم پچ پچ میکنن\nکه نمیفهمی،خوشکلی ،خوشتیپی ، خشتکت پارس، زیپت بازه یا عاشقت شدن...!",
    "مامان بابام دیشب قهر کردن، بابام صبح اومد آشتی کنه گفت: \nخانوم یه صبحونه به ما نمیدی؟ \nمامانم گفت: \nمگه من نوکرتم؟ \nدوباره یه دعوا شروع شد",
    "رفتیم خواستگاری پدر دختره گفت: از وضعیت مالیت بگو\n\nگفتم برام اصلا پول مهم نیست\n\nبا لباس سفید میام خونتون با لباس سفیدم میرم\nبا قمه افتادن دنبالم بیشورا",
    "فیلم سوپره دختره خواب بود طرف اومد سیر اینو کرد و تموم شد دختره هنوز بیدار نشده بود \nخب کصکش زنگ بزن اورژانس شاید مرده باشه",
    "مورد داشتیم دختره بلد نبوده در پورشه رو وا کنه بیاد بیرون!!!\nتو رودروایسی گیر کرده با پسره رفته شمال",
    "دست یه نابینارو گرفتم بردمش وسط خیابون دوباره برش گردوندم سرجاش\nعینکشو درآورد تو‌چشام نگاه کرد گفت: تو کصکش تری یا من؟",
    "صاب کارم گفته بود برا اینکه خوب بفروشیم \nتیکه کلامت خودم تست کردم، عالیه باشه. \nزنه اومد تو مغازه پرسید آقا اینا کیفیتش خوبه؟ ندید گفتم خودم تست کردم عالیه. \n\nسرمو بلند کردم دیدم نوار بهداشتی رو گرفته دستش",
    "قلمراد میره جبهه بعد از 2 روز برمی گرده. میگن چی شد اینقدر زود برگشتی؟\nمیگه: بابا اونجا به قصد کشت تفنگ بازی می کنن",
    "تو تاکسی زنه تلفنی با شوهرش دعواش شد،\nگوشیو که قطع کرد گفت مردا همه آشغالن، \nراننده زد بغل گفت از سطل آشغال من پیاده شو",
    "دختره ميخواست دوس پسرشو بوس کنه،\nپسره گفت قسم ميخوري که من اولين پسري ام که بوس ميکني! \nدختره ميگه آره بخدا چرا همتون اينو ميپرسين",
    "تو یه جمعی یکی بهم گفت یه کس بگو بخندیم.\nمنم گفتم کس ننت(: \nتا شعاعه 50 متری همه خندیدن غیر خودش \nکسکش فک کرده من دلقکم",
    "ﺩﮐﺘﺮ ﮔﻔﺖ ﭼﺮﺍ ﺳﯿﮕﺎﺭ ﻣﯿﮑﺸﯽ؟؟؟\n ﺩﺭﺩﻫﺎﯾﻢ ﺭﺍ ﮐﻪ ﺷﻨﯿﺪ ﺑﺎ ﮐﻤﯽ ﺗﺄﻣﻞ ﮔﻔﺖ ﺗﺮﯾﺎﮎ ﺑﮑﺶ بدبخت\n ریدم تو این زندگیت",
    "از داعشیه ميپرسن : چرا با ايرانیا نمی جنگید؟\nمیگه : اینا يه فهميده داشتن ... پرید زير تانک !\nواى به حال نفهماشون",
    "نوشته اگه دستت رو محکم گرفت یعنی دوستت داره\nپس چرا من اون سری مامور یگان دستمو محکم گرفته بود بهش گفتم منم دوستت دارم عشقم، اسپری فلفل زد تو صورتم",
    "خدا بیامرز بابابزرگم میگفت وقتی عیالوار بشی باید همه‌ش در بیاری بدی زن و بچه‌ت بخورن \nگفتم آقاجون زن حالا یه چیزی ولی بچه زشته ناموسا\n اونجا بود که سکته دوم رو زد"
]




async def generate_image_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.startswith('/پرامپت'):
        return

    prompt_text = text[len('/پرامپت'):].strip()
    if not prompt_text:
        await update.message.reply_text("لطفا بعد از /پرامپت موضوع عکس را وارد کنید.")
        return

    await update.message.reply_text("در حال ساخت تصویر... لطفا صبر کنید.")

    # نمونه URL فرضی API Polinations:
    api_url = f"https://image.pollinations.ai/prompt/{prompt_text}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    img_bytes = await resp.read()
                    bio = BytesIO(img_bytes)
                    bio.name = "image.png"
                    bio.seek(0)
                    await update.message.reply_photo(photo=InputFile(bio))
                else:
                    await update.message.reply_text("متأسفانه تصویر ساخته نشد. دوباره تلاش کنید.")
    except Exception as e:
        await update.message.reply_text(f"خطا در ساخت تصویر: {e}")




async def joke_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    triggers = [
        "یه جوک بگو",
        "جوک بگو",
        "جوک",
        "یه جوک",
        "جوک جدید",
        "یک جوک بگو",
        "جوک داری؟"
    ]
    if any(trigger == text for trigger in triggers):
        joke = random.choice(JOKES)
        await update.message.reply_text(joke)











async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    group_name = chat.title if chat.title else "گروه"
    for new_user in update.message.new_chat_members:
        name = new_user.first_name
        await update.message.reply_text(f"{name} \nبه {group_name} خوش اومدی! هر کاری داشتی بگو")


async def filter_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.lower() 

    for bad_word in BAD_WORDS:
        if bad_word in message_text:
            try:
                await update.message.delete()
                print(f"پیام حاوی کلمه نامناسب حذف شد: {bad_word}")

                # انتخاب پیام رندوم
                warning_msg_text = random.choice(warning_texts)
                
                warning_msg = await update.effective_chat.send_message(warning_msg_text)
                
                await asyncio.sleep(3)
                
                await warning_msg.delete()
            except Exception as e:
                print(f"خطا در حذف پیام یا ارسال تذکر: {e}")
            break


async def report_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "گزارش":
        await update.message.reply_text("✅ گزارش شما ثبت شد #گزارش")

async def send_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "لینک" in text:
        chat = update.effective_chat
        try:
            # گرفتن لینک گروه (ربات باید ادمین باشه و دسترسی داشته باشه)
            invite_link = await context.bot.export_chat_invite_link(chat.id)
            await update.message.reply_text(f"لینک گروه ✅\n{invite_link}")
        except Exception as e:
            await update.message.reply_text("متأسفانه نمی‌توانم لینک گروه را ارسال کنم. لطفاً مطمئن شوید ربات ادمین است.")
            print(f"خطا در گرفتن لینک گروه: {e}")

async def main():
    TOKEN = '7933239688:AAE88fA5gzZxj_wTK1_QQR0pxt4ODSQdPw8' 

    app = ApplicationBuilder().token(TOKEN).build()

    # هندلر عضو جدید
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(r'^/پرامپت'), generate_image_prompt))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & filters.Regex(r'^/پرامپت'), generate_image_prompt))

    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, fall_reply))



    # هندلر پاسخ به گزارش
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & filters.Regex(r'^گزارش$'), report_reply))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & filters.Regex(r'^یه جوک بگو$'), joke_reply))

    # هندلر ارسال لینک گروه (باید قبل از فیلتر کلمات باشه)
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & filters.Regex(r'^(لینک|لینک گروهو)$'), send_group_link))

    # هندلر فیلتر کلمات نامناسب
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, filter_bad_words))

    print("ربات در حال اجراست...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()

        loop.run_until_complete(main())
    except RuntimeError as e:
        print(f"خطا در اجرای ربات: {e}")
