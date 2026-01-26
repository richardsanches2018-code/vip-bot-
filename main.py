import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

# ================= CONFIG =================
TOKEN = "8351324083:AAG0O16bSbF3k-UsBNaPJlZqeOLvi6N8nyk"
BOT_ORIGEM_ID = -1003547693254  # <-- ID do Over0,5 bot

VIP_PRECO = "R$25,00"
PIX = "SUA_CHAVE_PIX"
NOME_PIX = "Richard Sanches Da Cruz"

# ================= BANCO DE DADOS =================
conn = sqlite3.connect("stats.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS stats (
    tipo TEXT,
    green INTEGER,
    red INTEGER,
    reembolso INTEGER
)
""")
conn.commit()

def init_stats():
    for t in ["gols", "cantos"]:
        cursor.execute("SELECT * FROM stats WHERE tipo=?", (t,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO stats VALUES (?,0,0,0)", (t,))
    conn.commit()

def add_result(tipo, res):
    cursor.execute(f"UPDATE stats SET {res}={res}+1 WHERE tipo=?", (tipo,))
    conn.commit()

def get_stats(tipo):
    cursor.execute("SELECT green, red, reembolso FROM stats WHERE tipo=?", (tipo,))
    return cursor.fetchone()

init_stats()

# ================= COPIAR SINAIS AUTOMÁTICO =================
async def copiar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return

    if update.message.from_user.id != BOT_ORIGEM_ID:
        return

    texto = update.message.text.lower()

    # filtro sinais reais
    palavras = ["over", "under", "0.5", "1.5", "2.5", "ht", "ft", "escanteio", "canto"]
    if not any(p in texto for p in palavras):
        return

    tipo = "gols"
    if "escanteio" in texto or "canto" in texto:
        tipo = "cantos"

    teclado = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ GREEN", callback_data=f"green|{tipo}"),
            InlineKeyboardButton("❌ RED", callback_data=f"red|{tipo}"),
            InlineKeyboardButton("♻️ REEMBOLSO", callback_data=f"reembolso|{tipo}")
        ]
    ])

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=update.message.text,
        reply_markup=teclado
    )

# ================= BOTÕES RESULTADO =================
async def resultado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    res, tipo = query.data.split("|")
    add_result(tipo, res)

    if res == "green":
        txt = "\n\n✅ RESULTADO: GREEN"
    elif res == "red":
        txt = "\n\n❌ RESULTADO: RED"
    else:
        txt = "\n\n♻️ RESULTADO: REEMBOLSO"

    await query.edit_message_text(query.message.text + txt)

# ================= PARCIAL GOLS =================
async def parcial_gols(update: Update, context: ContextTypes.DEFAULT_TYPE):
    g, r, e = get_stats("gols")
    total = g + r
    win = (g / total * 100) if total > 0 else 0
    await update.message.reply_text(
        f"📊 PARCIAL GOLS\nGreen: {g}\nRed: {r}\nReembolso: {e}\nWinrate: {win:.2f}%"
    )

# ================= PARCIAL CANTOS =================
async def parcial_cantos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    g, r, e = get_stats("cantos")
    total = g + r
    win = (g / total * 100) if total > 0 else 0
    await update.message.reply_text(
        f"📊 PARCIAL ESCANTEIOS\nGreen: {g}\nRed: {r}\nReembolso: {e}\nWinrate: {win:.2f}%"
    )

# ================= RELATÓRIO =================
async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gg, gr, ge = get_stats("gols")
    cg, cr, ce = get_stats("cantos")

    total_green = gg + cg
    total_red = gr + cr
    total = total_green + total_red
    win = (total_green / total * 100) if total > 0 else 0

    await update.message.reply_text(
        f"📈 RELATÓRIO DIÁRIO\n\n"
        f"GOLS: {gg}G / {gr}R\n"
        f"CANTOS: {cg}G / {cr}R\n\n"
        f"TOTAL GREEN: {total_green}\nTOTAL RED: {total_red}\nWINRATE: {win:.2f}%"
    )

# ================= RESET =================
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("UPDATE stats SET green=0, red=0, reembolso=0")
    conn.commit()
    await update.message.reply_text("🔄 RESETADO!")

# ================= VIP =================
async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💎 VIP PREMIUM\n\nMensal: {VIP_PRECO}\n\nPIX: {PIX}\nNome: {NOME_PIX}"
    )

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🤖 BOT VIP ONLINE

/parcial_gols
/parcial_cantos
/relatorio
/reset
/vip
""")

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, copiar))
    app.add_handler(CallbackQueryHandler(resultado))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("parcial_gols", parcial_gols))
    app.add_handler(CommandHandler("parcial_cantos", parcial_cantos))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("vip", vip))

    print("🔥 BOT DEFINITIVO ONLINE")
    app.run_polling()

if __name__ == "__main__":
    main()
