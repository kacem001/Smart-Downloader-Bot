import os
import re
import yt_dlp
import logging
import requests
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InputMediaPhoto,
    InputMediaVideo,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

with open("bot_token.txt", "r") as f:
    TELEGRAM_BOT_TOKEN = f.read().strip()

DOWNLOAD_DIR = "downloads"

LANGUAGES = {
    "العربية": "ar",
    "English": "en",
    "Indonesia": "id",
    "Русский": "ru",
    "日本語": "ja"
}

PLATFORMS = [
    "Facebook", "TikTok", "Instagram", "YouTube", "Pinterest", "Snapchat"
]

ADMINS = [6413712599]
USER_IDS = set()
ADMIN_BROADCAST_MEDIA = {}

MESSAGES = {
    "en": {
        "welcome": "👋 Welcome!\nPress 'Home' to start downloading from social media, or open 'Settings' for more options.",
        "home": "🏠 Home",
        "settings": "⚙️ Settings",
        "share_bot": "🔗 Share Bot",
        "report_problem": "🚩 Report a Problem",
        "choose_platform": "🎯 Select a social media platform:",
        "choose_language": "🌐 Change language:",
        "send_link": "📩 Please send the link to the post or video from {platform}.",
        "invalid_link": "⚠️ The link is invalid or not supported. Please try again.",
        "choose_type": "Please select the file type you want to download:",
        "choose_mp3_mp4": "🎵 Audio (MP3) or 🎬 Video (MP4)?",
        "downloading_now": "⏳ Downloading your file, please wait...",
        "download_failed": "❌ Download failed. Please check the link or try again later.",
        "help": "ℹ️ Send a link from Facebook, TikTok, Instagram, YouTube, Pinterest, or Snapchat.",
        "back": "⬅️ Back",
        "change_language": "🌐 Change language",
        "feature_soon": "✨ More features coming soon!",
        "send_message": "📢 Broadcast",
        "cancel": "❌ Cancel",
        "enter_broadcast": "✏️ Send the message or media you want to broadcast, or press Cancel.",
        "broadcast_sent": "✅ The broadcast has been sent to all users.",
        "broadcast_cancelled": "❎ The broadcast was cancelled.",
        "send_problem": "✏️ Please describe the problem and send it.",
        "problem_received": "✅ Your report has been received. Thank you!",
        "share_text": "Share this bot with your friends 👇",
    },
    "ar": {
        "welcome": "👋 مرحبًا بك!\nاضغط على 'الصفحة الرئيسية' للتحميل من وسائل التواصل، أو افتح 'الإعدادات' للمزيد من الخيارات.",
        "home": "🏠 الصفحة الرئيسية",
        "settings": "⚙️ الإعدادات",
        "share_bot": "🔗 مشاركة البوت",
        "report_problem": "🚩 الإبلاغ عن مشكلة",
        "choose_platform": "🎯 اختر منصة التواصل الاجتماعي:",
        "choose_language": "🌐 تغيير اللغة:",
        "send_link": "📩 يرجى إرسال رابط المنشور أو الفيديو من {platform}.",
        "invalid_link": "⚠️ الرابط غير صالح أو غير مدعوم. يرجى المحاولة مرة أخرى.",
        "choose_type": "يرجى اختيار نوع الملف الذي تريد تحميله:",
        "choose_mp3_mp4": "🎵 صوت (MP3) أو 🎬 فيديو (MP4)؟",
        "downloading_now": "⏳ جاري تحميل الملف، يرجى الانتظار...",
        "download_failed": "❌ فشل التحميل. تحقق من الرابط أو حاول لاحقًا.",
        "help": "ℹ️ أرسل رابطًا من فيسبوك أو تيك توك أو إنستجرام أو يوتيوب أو بنترست أو سناب شات.",
        "back": "⬅️ رجوع",
        "change_language": "🌐 تغيير اللغة",
        "feature_soon": "✨ المزيد من الميزات قريبًا!",
        "send_message": "📢 بث إعلان",
        "cancel": "❌ إلغاء",
        "enter_broadcast": "✏️ أرسل الرسالة أو الوسائط للإعلان، أو اضغط إلغاء.",
        "broadcast_sent": "✅ تم إرسال الإعلان إلى جميع المستخدمين.",
        "broadcast_cancelled": "❎ تم إلغاء البث.",
        "send_problem": "✏️ يرجى وصف المشكلة وإرسالها.",
        "problem_received": "✅ تم استلام بلاغك. شكرًا لك!",
        "share_text": "شارك هذا البوت مع أصدقائك 👇",
    },
    "id": {
        "welcome": "👋 Selamat datang!\nTekan 'Beranda' untuk mulai mengunduh dari media sosial, atau buka 'Pengaturan' untuk opsi lainnya.",
        "home": "🏠 Beranda",
        "settings": "⚙️ Pengaturan",
        "share_bot": "🔗 Bagikan Bot",
        "report_problem": "🚩 Laporkan Masalah",
        "choose_platform": "🎯 Pilih platform media sosial:",
        "choose_language": "🌐 Ganti bahasa:",
        "send_link": "📩 Silakan kirim tautan ke postingan atau video dari {platform}.",
        "invalid_link": "⚠️ Tautan tidak valid atau tidak didukung. Silakan coba lagi.",
        "choose_type": "Silakan pilih jenis file yang ingin Anda unduh:",
        "choose_mp3_mp4": "🎵 Audio (MP3) atau 🎬 Video (MP4)?",
        "downloading_now": "⏳ Mengunduh file Anda, mohon tunggu...",
        "download_failed": "❌ Gagal mengunduh. Periksa tautan atau coba lagi nanti.",
        "help": "ℹ️ Kirim tautan dari Facebook, TikTok, Instagram, YouTube, Pinterest, atau Snapchat.",
        "back": "⬅️ Kembali",
        "change_language": "🌐 Ganti bahasa",
        "feature_soon": "✨ Fitur lain segera hadir!",
        "send_message": "📢 Siarkan Pesan",
        "cancel": "❌ Batal",
        "enter_broadcast": "✏️ Kirim pesan atau media untuk disiarkan, atau tekan Batal.",
        "broadcast_sent": "✅ Pesan telah dikirim ke semua pengguna.",
        "broadcast_cancelled": "❎ Siaran dibatalkan.",
        "send_problem": "✏️ Silakan jelaskan masalah dan kirimkan.",
        "problem_received": "✅ Laporan Anda telah diterima. Terima kasih!",
        "share_text": "Bagikan bot ini dengan teman-teman Anda 👇",
    },
    "ru": {
        "welcome": "👋 Добро пожаловать!\nНажмите 'Главная', чтобы начать скачивание из соцсетей, или откройте 'Настройки' для других опций.",
        "home": "🏠 Главная",
        "settings": "⚙️ Настройки",
        "share_bot": "🔗 Поделиться ботом",
        "report_problem": "🚩 Сообщить о проблеме",
        "choose_platform": "🎯 Выберите социальную платформу:",
        "choose_language": "🌐 Изменить язык:",
        "send_link": "📩 Пожалуйста, отправьте ссылку на пост или видео из {platform}.",
        "invalid_link": "⚠️ Ссылка недействительна или не поддерживается. Попробуйте снова.",
        "choose_type": "Пожалуйста, выберите тип файла для скачивания:",
        "choose_mp3_mp4": "🎵 Аудио (MP3) или 🎬 Видео (MP4)?",
        "downloading_now": "⏳ Скачивание файла, пожалуйста, подождите...",
        "download_failed": "❌ Не удалось скачать. Проверьте ссылку или попробуйте позже.",
        "help": "ℹ️ Отправьте ссылку с Facebook, TikTok, Instagram, YouTube, Pinterest или Snapchat.",
        "back": "⬅️ Назад",
        "change_language": "🌐 Изменить язык",
        "feature_soon": "✨ Больше функций скоро появится!",
        "send_message": "📢 Рассылка",
        "cancel": "❌ Отмена",
        "enter_broadcast": "✏️ Отправьте сообщение или медиа для рассылки или нажмите Отмена.",
        "broadcast_sent": "✅ Рассылка отправлена всем пользователям.",
        "broadcast_cancelled": "❎ Рассылка отменена.",
        "send_problem": "✏️ Пожалуйста, опишите проблему и отправьте.",
        "problem_received": "✅ Ваш отчет получен. Спасибо!",
        "share_text": "Поделитесь этим ботом с друзьями 👇",
    },
    "ja": {
        "welcome": "👋 ようこそ！\n「ホーム」を押してSNSからダウンロードを開始するか、「設定」を開いて詳細オプションを確認してください。",
        "home": "🏠 ホーム",
        "settings": "⚙️ 設定",
        "share_bot": "🔗 ボットを共有",
        "report_problem": "🚩 問題を報告",
        "choose_platform": "🎯 ソーシャルメディアプラットフォームを選択してください：",
        "choose_language": "🌐 言語を変更：",
        "send_link": "📩 {platform}の投稿または動画のリンクを送信してください。",
        "invalid_link": "⚠️ リンクが無効または未対応です。もう一度お試しください。",
        "choose_type": "ダウンロードしたいファイルの種類を選んでください：",
        "choose_mp3_mp4": "🎵 オーディオ (MP3) または 🎬 ビデオ (MP4)?",
        "downloading_now": "⏳ ファイルをダウンロードしています。お待ちください...",
        "download_failed": "❌ ダウンロードに失敗しました。リンクを確認するか、後で再試行してください。",
        "help": "ℹ️ Facebook、TikTok،Instagram،YouTube、Pinterest、またはSnapchatのリンクを送信してください。",
        "back": "⬅️ 戻る",
        "change_language": "🌐 言語を変更",
        "feature_soon": "✨ さらなる機能がまもなく追加されます！",
        "send_message": "📢 ブロードキャスト",
        "cancel": "❌ キャンセル",
        "enter_broadcast": "✏️ ブロードキャストするメッセージまたはメディアを送信するか、キャンセルを押してください。",
        "broadcast_sent": "✅ ブロードキャストが全ユーザーに送信されました。",
        "broadcast_cancelled": "❎ ブロードキャストはキャンセルされました。",
        "send_problem": "✏️ 問題を説明して送信してください。",
        "problem_received": "✅ ご報告を受け取りました。ありがとうございます！",
        "share_text": "このボットを友達とシェアしましょう 👇",
    }
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_user(user_id):
    USER_IDS.add(user_id)

def get_message(lang, key, **kwargs):
    lang = lang if lang in MESSAGES else "en"
    msg = MESSAGES[lang].get(key, "")
    return msg.format(**kwargs)

def detect_platform(url: str):
    patterns = {
        "Facebook": r"(facebook\.com|fb\.watch|fb\.me)",
        "TikTok": r"(tiktok\.com)",
        "Instagram": r"(instagram\.com)",
        "YouTube": r"(youtube\.com|youtu\.be)",
        "Pinterest": r"(pinterest\.com|pin\.it)",
        "Snapchat": r"(snapchat\.com)"
    }
    for name, pat in patterns.items():
        if re.search(pat, url, re.IGNORECASE):
            return name
    return None

def main_menu_keyboard(lang):
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(get_message(lang, "home"))],
            [
                KeyboardButton(get_message(lang, "settings")),
                KeyboardButton(get_message(lang, "share_bot")),
                KeyboardButton(get_message(lang, "report_problem")),
            ]
        ],
        resize_keyboard=True
    )

def home_platform_keyboard(lang):
    kb = []
    for p in PLATFORMS:
        if p == "Instagram":
            label = "~Instagram~" if lang == "en" else "~إنستجرام~"
            kb.append([KeyboardButton(label)])
        else:
            kb.append([KeyboardButton(p)])
    kb.append([KeyboardButton(get_message(lang, "back"))])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def settings_keyboard(lang, is_admin=False):
    kb = [
        [KeyboardButton(get_message(lang, "change_language"))],
        [KeyboardButton(get_message(lang, "share_bot")), KeyboardButton(get_message(lang, "report_problem"))]
    ]
    if is_admin:
        kb.append([KeyboardButton(get_message(lang, "send_message"))])
    kb.append([KeyboardButton(get_message(lang, "back"))])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def language_keyboard():
    kb = [[KeyboardButton(lang)] for lang in LANGUAGES]
    kb.append([KeyboardButton("⬅️ Back")])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def back_keyboard(lang):
    return ReplyKeyboardMarkup(
        [[KeyboardButton(get_message(lang, "back"))]],
        resize_keyboard=True
    )

def remove_keyboard():
    return ReplyKeyboardRemove()

def resolve_pinterest_shortlink(url):
    try:
        session = requests.Session()
        resp = session.head(url, allow_redirects=True, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        return resp.url
    except Exception:
        return url

def resolve_facebook_share_link(url):
    try:
        session = requests.Session()
        resp = session.get(url, allow_redirects=True, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        return resp.url
    except Exception:
        return url

def download_pinterest_content(pin_url, dest_dir):
    user_agent = "Mozilla/5.0 (compatible; PinterestBot/1.0; +http://www.pinterest.com/bot.html)"
    html = ""
    try:
        resp = requests.get(pin_url, headers={"User-Agent": user_agent}, timeout=20)
        if resp.status_code == 200:
            html = resp.text
        else:
            if "pin.it" in pin_url or resp.is_redirect:
                try:
                    redirect_url = resp.headers.get("Location") or resp.url
                    resp2 = requests.get(redirect_url, headers={"User-Agent": user_agent}, timeout=20)
                    if resp2.status_code == 200:
                        html = resp2.text
                except Exception:
                    pass
    except Exception:
        pass
    candidates = []
    for patt in [
        r'"url":"(https://i\.pinimg\.com[^"]+)"',
        r'<meta property="og:image" content="([^"]+)"',
        r'<meta property="og:video" content="([^"]+)"',
        r'"contentUrl":"(https://[^"]+)"'
    ]:
        for m in re.finditer(patt, html):
            url = m.group(1).replace('\\u002F', '/').replace('\\', '')
            candidates.append(url)
    candidates = list(dict.fromkeys(candidates))
    files = []
    for idx, url in enumerate(candidates):
        ext = os.path.splitext(url)[-1].split("?")[0]
        if not ext or len(ext) > 6:
            ext = ".jpg"
        file_path = os.path.join(dest_dir, f"pinterest_{idx}{ext}")
        try:
            data = requests.get(url, headers={"User-Agent": user_agent}, timeout=20).content
            with open(file_path, "wb") as f:
                f.write(data)
            files.append(file_path)
        except Exception:
            continue
    return files if files else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    lang = "ar"
    context.user_data["lang"] = lang
    add_user(update.effective_user.id)
    await update.message.reply_text(
        get_message(lang, "welcome"),
        reply_markup=main_menu_keyboard(lang)
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ar")
    txt = update.message.text.strip()
    user_id = update.effective_user.id
    add_user(user_id)
    is_admin = user_id in ADMINS

    if txt == get_message(lang, "home"):
        await update.message.reply_text(
            get_message(lang, "choose_platform"),
            reply_markup=home_platform_keyboard(lang)
        )
        return
    if txt == get_message(lang, "settings"):
        await update.message.reply_text(
            get_message(lang, "settings"),
            reply_markup=settings_keyboard(lang, is_admin)
        )
        return
    if txt == get_message(lang, "share_bot"):
        bot_link = f"https://t.me/{(await context.bot.get_me()).username}"
        await update.message.reply_text(
            f"{get_message(lang, 'share_text')}\n\n{bot_link}",
            reply_markup=main_menu_keyboard(lang)
        )
        return
    if txt == get_message(lang, "report_problem"):
        context.user_data["report_mode"] = True
        await update.message.reply_text(
            get_message(lang, "send_problem"),
            reply_markup=ReplyKeyboardMarkup([[get_message(lang, "cancel")]], resize_keyboard=True)
        )
        return
    if txt == get_message(lang, "change_language"):
        await update.message.reply_text(
            get_message(lang, "choose_language"),
            reply_markup=language_keyboard()
        )
        return
    if txt in LANGUAGES:
        lang_code = LANGUAGES[txt]
        context.user_data["lang"] = lang_code
        await update.message.reply_text(
            get_message(lang_code, "welcome"),
            reply_markup=main_menu_keyboard(lang_code)
        )
        return
    if txt == "⬅️ Back":
        await update.message.reply_text(
            get_message(lang, "settings"),
            reply_markup=settings_keyboard(lang, is_admin)
        )
        return
    if txt == get_message(lang, "back"):
        await update.message.reply_text(
            get_message(lang, "welcome"),
            reply_markup=main_menu_keyboard(lang)
        )
        return
    if txt in PLATFORMS or txt in ["~Instagram~", "~إنستجرام~"]:
        context.user_data["platform"] = "Instagram" if "انستجرام" in txt or "Instagram" in txt else txt
        await update.message.reply_text(
            get_message(lang, "send_link", platform=context.user_data["platform"]),
            reply_markup=back_keyboard(lang)
        )
        return
    if is_admin and txt == get_message(lang, "send_message"):
        context.user_data["broadcast_mode"] = True
        ADMIN_BROADCAST_MEDIA[user_id] = []
        await update.message.reply_text(
            get_message(lang, "enter_broadcast"),
            reply_markup=ReplyKeyboardMarkup(
                [[get_message(lang, "cancel")]],
                resize_keyboard=True
            )
        )
        return
    await handle_text(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ar")
    text = update.message.text.strip()
    user_id = update.effective_user.id
    add_user(user_id)

    if "facebook.com/share/p/" in text:
        text = resolve_facebook_share_link(text)
    if "pin.it" in text:
        text = resolve_pinterest_shortlink(text)

    if context.user_data.get("report_mode"):
        context.user_data["report_mode"] = False
        for admin_id in ADMINS:
            await context.bot.send_message(admin_id, f"[REPORT]\nFrom: {user_id}\n\n{text}")
        await update.message.reply_text(
            get_message(lang, "problem_received"),
            reply_markup=main_menu_keyboard(lang)
        )
        return

    if context.user_data.get("broadcast_mode"):
        if text == get_message(lang, "cancel") or text == get_message(lang, "back"):
            context.user_data["broadcast_mode"] = False
            ADMIN_BROADCAST_MEDIA[user_id] = []
            await update.message.reply_text(
                get_message(lang, "broadcast_cancelled"),
                reply_markup=settings_keyboard(lang, user_id in ADMINS)
            )
            return
        ADMIN_BROADCAST_MEDIA[user_id].append(("text", text))
        await broadcast(admin_id=user_id, context=context, lang=lang)
        context.user_data["broadcast_mode"] = False
        ADMIN_BROADCAST_MEDIA[user_id] = []
        await update.message.reply_text(
            get_message(lang, "broadcast_sent"),
            reply_markup=settings_keyboard(lang, user_id in ADMINS)
        )
        return

    if text == get_message(lang, "back"):
        await update.message.reply_text(
            get_message(lang, "choose_platform"),
            reply_markup=home_platform_keyboard(lang)
        )
        return
    url = text
    platform = detect_platform(url)
    if not platform:
        await update.message.reply_text(get_message(lang, "invalid_link"), reply_markup=home_platform_keyboard(lang))
        return
    context.user_data["last_url"] = url
    context.user_data["last_platform"] = platform

    if platform == "Pinterest":
        await download_and_send_pinterest(update, context, url, lang)
    else:
        await update.message.reply_text(
            get_message(lang, "choose_mp3_mp4"),
            reply_markup=ReplyKeyboardMarkup([["🎬 MP4", "🎵 MP3"], [get_message(lang, "back")]], resize_keyboard=True)
        )

async def handle_reply_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ar")
    txt = update.message.text.strip()
    user_id = update.effective_user.id
    add_user(user_id)

    if txt in ["🎬 MP4", "🎵 MP3"]:
        url = context.user_data.get("last_url", "")
        platform = context.user_data.get("last_platform", "")
        as_audio = txt == "🎵 MP3"
        await download_and_send(update, context, url, lang, platform, as_audio=as_audio)
        return
    await handle_menu(update, context)

async def download_and_send_pinterest(update, context, url, lang):
    await update.message.reply_text(get_message(lang, "downloading_now"), reply_markup=remove_keyboard())
    user_id = update.effective_user.id
    user_dir = os.path.join(DOWNLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    files = download_pinterest_content(url, user_dir)
    if files:
        media = []
        for file_path in files:
            ext = os.path.splitext(file_path)[-1].lower()
            if ext in (".mp4", ".mkv", ".webm"):
                media.append(InputMediaVideo(open(file_path, "rb")))
            elif ext in (".jpg", ".png", ".jpeg", ".gif"):
                media.append(InputMediaPhoto(open(file_path, "rb")))
            else:
                media.append(InputMediaPhoto(open(file_path, "rb")))
        # تقسيم الميديا إلى مجموعات (10 أو أقل)
        while media:
            batch = media[:10]
            media = media[10:]
            if len(batch) == 1:
                if isinstance(batch[0], InputMediaVideo):
                    await update.message.reply_video(video=batch[0].media)
                else:
                    await update.message.reply_photo(photo=batch[0].media)
            else:
                await update.message.reply_media_group(batch)
        await update.message.reply_text(get_message(lang, "feature_soon"), reply_markup=home_platform_keyboard(lang))
        for file_path in files:
            try:
                os.remove(file_path)
            except Exception:
                pass
        return
    await update.message.reply_text(get_message(lang, "download_failed"), reply_markup=home_platform_keyboard(lang))

async def download_and_send(update, context, url, lang, platform=None, as_audio=False):
    await update.message.reply_text(get_message(lang, "downloading_now"), reply_markup=remove_keyboard())
    user_id = update.effective_user.id
    user_dir = os.path.join(DOWNLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    file_path = None
    success = False

    ydl_opts = {
        "outtmpl": f"{user_dir}/%(title).40s.%(ext)s",
        "format": "bestaudio/best" if as_audio else "bestvideo+bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "nocheckcertificate": True,
    }
    if as_audio:
        ydl_opts["extract_audio"] = True
        ydl_opts["audio_format"] = "mp3"
        ydl_opts["audio_quality"] = "192K"
        ydl_opts["merge_output_format"] = "mp3"
    else:
        ydl_opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if "entries" in info:
                info = info["entries"][0]
            file_path = ydl.prepare_filename(info)
            base, _ = os.path.splitext(file_path)
            if as_audio:
                for ext in ["mp3", "m4a"]:
                    candidate = f"{base}.{ext}"
                    if os.path.exists(candidate):
                        file_path = candidate
                        break
            else:
                for ext in ["mp4", "mkv", "webm"]:
                    candidate = f"{base}.{ext}"
                    if os.path.exists(candidate):
                        file_path = candidate
                        break
            if os.path.exists(file_path):
                success = True
    except Exception as e:
        logger.error(f"yt-dlp failed: {e}")

    if success and file_path and os.path.exists(file_path):
        ext = os.path.splitext(file_path)[-1].lower()
        try:
            if ext in (".mp4", ".mkv", ".webm"):
                await update.message.reply_video(video=open(file_path, "rb"))
            elif ext in (".jpg", ".png", ".jpeg"):
                await update.message.reply_photo(photo=open(file_path, "rb"))
            elif ext in (".mp3", ".m4a"):
                await update.message.reply_audio(audio=open(file_path, "rb"))
            else:
                await update.message.reply_document(document=open(file_path, "rb"))
            await update.message.reply_text(get_message(lang, "feature_soon"), reply_markup=home_platform_keyboard(lang))
        except Exception as ex:
            logger.error(f"Send file error: {ex}")
            await update.message.reply_text(get_message(lang, "download_failed"), reply_markup=home_platform_keyboard(lang))
        try:
            os.remove(file_path)
        except Exception:
            pass
        return
    else:
        await update.message.reply_text(get_message(lang, "download_failed"), reply_markup=home_platform_keyboard(lang))

async def broadcast(admin_id, context, lang):
    medias = ADMIN_BROADCAST_MEDIA.get(admin_id, [])
    sent = 0
    if not medias:
        return
    if all(m[0] == "text" for m in medias):
        for uid in USER_IDS:
            try:
                for _, txt in medias:
                    await context.bot.send_message(uid, text=txt)
                sent += 1
            except Exception: pass
    elif len(medias) == 1 and medias[0][0] in ("photo", "video"):
        for uid in USER_IDS:
            try:
                if medias[0][0] == "photo":
                    await context.bot.send_photo(uid, medias[0][1])
                else:
                    await context.bot.send_video(uid, medias[0][1])
                sent += 1
            except Exception: pass
    else:
        media_group = []
        for typ, media in medias:
            if typ == "photo":
                media_group.append(InputMediaPhoto(media))
            elif typ == "video":
                media_group.append(InputMediaVideo(media))
        for uid in USER_IDS:
            try:
                await context.bot.send_media_group(uid, media_group)
                sent += 1
            except Exception: pass
    return sent

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "ar")
    if context.user_data.get("broadcast_mode"):
        typ = None
        file = None
        if update.message.photo:
            typ = "photo"
            file = await update.message.photo[-1].get_file()
        elif update.message.video:
            typ = "video"
            file = await update.message.video.get_file()
        if typ and file:
            ADMIN_BROADCAST_MEDIA[user_id].append((typ, file.file_id))
            await update.message.reply_text(get_message(lang, "broadcast_sent"), reply_markup=settings_keyboard(lang, user_id in ADMINS))
        context.user_data["broadcast_mode"] = False

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply_buttons))
    print("بوت التحميل الاحترافي يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
