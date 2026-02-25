import os
import pickle
import random
import string
from datetime import date, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# ================== CONFIG ==================
TOKEN = os.getenv("TOKEN")

# ⚠️ COLOCA AQUI O TEU ID DO TELEGRAM (@userinfobot)
ADMIN_ID =8195479025

OWNERS = [8195479025:AAEW6n8Ba_RQxRbfIPJaEYMY1wbF2WSyiEo]

# ================== VIP ==================
def load_vips():
    try:
        with open("vip.pkl", "rb") as f:
            return pickle.load(f)
    except:
        return {}

def save_vips(vips):
    with open("vip.pkl", "wb") as f:
        pickle.dump(vips, f)

VIP_USERS = load_vips()

# ================== CÓDIGOS ==================
def load_codigos():
    try:
        with open("codigos.pkl", "rb") as f:
            return pickle.load(f)
    except:
        return []

def save_codigos(c):
    with open("codigos.pkl", "wb") as f:
        pickle.dump(c, f)

CODIGOS = load_codigos()
USED_CODES = []

# ================== DOWNLOAD ==================
user_downloads = {}

def is_vip(user_id):
    if user_id in OWNERS:
        return True
    if user_id in VIP_USERS:
        if date.today() <= VIP_USERS[user_id]:
            return True
        else:
            del VIP_USERS[user_id]
            save_vips(VIP_USERS)
    return False

# ================== COMANDOS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in OWNERS:
        await update.message.reply_text("👑 És DONO - Acesso ilimitado.")
        return
    if is_vip(user_id):
        await update.message.reply_text("🎉 És VIP! Downloads ilimitados.")
    else:
        today = str(date.today())
        if user_id not in user_downloads:
            user_downloads[user_id] = {"date": today, "count": 0}
        if user_downloads[user_id]["date"] != today:
            user_downloads[user_id] = {"date": today, "count": 0}
        restam = 3 - user_downloads[user_id]["count"]
        await update.message.reply_text(
            f"📥 Tens {restam} downloads grátis hoje.\n\n"
            "💎 VIP = ilimitado por 150MT/mês\n"
            "Usa /vip para comprar"
        )

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 VIP = Downloads ilimitados\n"
        "Preço: 150MT / mês\n\n"
        "💰 Pagamento via:\n"
        "M-Pesa: 856614967\n"
        "mKesh: 834195579\n"
        "e-Mola: 876405044\n\n"
        "Depois usa o código via /ativar CODIGO"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in OWNERS:
        await update.message.reply_text("👑 És DONO - VIP infinito.")
        return
    if is_vip(user_id):
        exp = VIP_USERS[user_id]
        await update.message.reply_text(f"💎 VIP ativo até: {exp}")
    else:
        await update.message.reply_text("❌ Não és VIP.\nUsa /vip")

async def gerar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        quantidade = int(context.args[0])
    except:
        await update.message.reply_text("Usa: /gerar 10")
        return
    novos = []
    for _ in range(quantidade):
        codigo = "VIP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        CODIGOS.append(codigo)
        novos.append(codigo)
    save_codigos(CODIGOS)
    lista = "\n".join(novos)
    await update.message.reply_text(f"Códigos criados:\n\n{lista}")

async def ativar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        codigo = context.args[0]
    except:
        await update.message.reply_text("Usa: /ativar CODIGO")
        return
    if codigo in CODIGOS:
        VIP_USERS[user_id] = date.today() + timedelta(days=30)
        CODIGOS.remove(codigo)
        save_codigos(CODIGOS)
        save_vips(VIP_USERS)
        await update.message.reply_text("🎉 VIP ativado por 30 dias!")
    else:
        await update.message.reply_text("❌ Código inválido.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in OWNERS:
        pass
    else:
        today = str(date.today())
        if user_id not in user_downloads:
            user_downloads[user_id] = {"date": today, "count": 0}
        if user_downloads[user_id]["date"] != today:
            user_downloads[user_id] = {"date": today, "count": 0}
        if not is_vip(user_id) and user_downloads[user_id]["count"] >= 3:
            await update.message.reply_text("Limite grátis atingido.\n💎 Paga 150MT para VIP.")
            return
    url = update.message.text
    filename = "video.mp4"
    ydl_opts = {'outtmpl': filename,'format': 'best','quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await update.message.reply_video(video=open(filename, "rb"))
        if user_id not in OWNERS and not is_vip(user_id):
            user_downloads[user_id]["count"] += 1
    except:
        await update.message.reply_text("Erro ao baixar o vídeo.")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# ================== RUN ==================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("vip", vip))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("gerar", gerar))
app.add_handler(CommandHandler("ativar", ativar))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download))
app.run_polling()
