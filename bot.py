from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import yt_dlp
import os
from datetime import date, timedelta

TOKEN = "8195479025:AAEW6n8Ba_RQxRbfIPJaEYMY1wbF2WSyiEo"
ADMIN_ID = 987654321  # <-- coloca aqui o TEU ID

VIP_USERS = {}
user_downloads = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Grátis: 3 downloads/dia\nVIP: ilimitado (150MT/mês)")

async def addvip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Sem permissão.")
        return

    try:
        user_id = int(context.args[0])
        VIP_USERS[user_id] = date.today() + timedelta(days=30)
        await update.message.reply_text(f"VIP ativado até {VIP_USERS[user_id]}")
    except:
        await update.message.reply_text("Usa: /addvip ID")

def is_vip(user_id):
    if user_id in VIP_USERS:
        if date.today() <= VIP_USERS[user_id]:
            return True
        else:
            del VIP_USERS[user_id]
    return False

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    today = str(date.today())

    if user_id not in user_downloads:
        user_downloads[user_id] = {"date": today, "count": 0}

    if user_downloads[user_id]["date"] != today:
        user_downloads[user_id] = {"date": today, "count": 0}

    if not is_vip(user_id):
        if user_downloads[user_id]["count"] >= 3:
            await update.message.reply_text("Limite grátis atingido.\nPaga 150MT para VIP.")
            return

    url = update.message.text
    filename = "video.mp4"

    ydl_opts = {
        'outtmpl': filename,
        'format': 'best',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await update.message.reply_video(video=open(filename, "rb"))

        if not is_vip(user_id):
            user_downloads[user_id]["count"] += 1

    except:
        await update.message.reply_text("Erro ao baixar.")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addvip", addvip))
app.add_handler(MessageHandler(filters.TEXT, download))
app.run_polling()
