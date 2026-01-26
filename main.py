import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3, os
from datetime import datetime

TOKEN = os.getenv("TOKEN") or "8351324083:AAG0O16bSbF3k-UsBNaPJlZqeOLvi6N8nyk"
bot = telebot.TeleBot(TOKEN)

# ===== BANCO =====
conn = sqlite3.connect("vip.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    msg_id INTEGER,
    data TEXT
)
""")
conn.commit()

# ===== BOTÕES =====
def barra():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🟢 GREEN", callback_data="green"),
        InlineKeyboardButton("🔴 RED", callback_data="red"),
        InlineKeyboardButton("♻️ REEMBOLSO", callback_data="refund")
    )
    return kb

# ===== DETECTAR APOSTA (AUTO FORWARDER) =====
# ISSO AQUI FAZ APARECER EM TODA MENSAGEM
@bot.message_handler(func=lambda msg: msg.text and len(msg.text) > 10)
def auto_barra(msg):
    try:
        bot.edit_message_reply_markup(
            msg.chat.id,
            msg.message_id,
            reply_markup=barra()
        )
    except:
        pass

# ===== CLIQUES =====
@bot.callback_query_handler(func=lambda call: True)
def clicar(call):
    msg_id = call.message.message_id
    data = datetime.now().strftime("%Y-%m-%d")

    # evita duplicar
    c.execute("SELECT * FROM resultados WHERE msg_id=?", (msg_id,))
    if c.fetchone():
        bot.answer_callback_query(call.id, "Já marcado ⚠️")
        return

    if call.data == "green":
        tipo = "green"
    elif call.data == "red":
        tipo = "red"
    else:
        tipo = "refund"

    c.execute("INSERT INTO resultados (tipo,msg_id,data) VALUES (?,?,?)", (tipo,msg_id,data))
    conn.commit()

    bot.answer_callback_query(call.id, f"{tipo.upper()} registrado")

# ===== PAINEL VIP =====
@bot.message_handler(commands=["start"])
def painel(msg):
    bot.send_message(msg.chat.id, """
🤖 VIP INSTITUCIONAL

⚽ GOLS HT / FT
🚩 ESCANTEIOS HT / FT

💰 VIP MENSAL: R$25
Pix: SUA CHAVE PIX
""")

bot.infinity_polling()
