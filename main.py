import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from datetime import datetime
import os

# ===== TOKEN =====
TOKEN = os.getenv("8351324083:AAG0O16bSbF3k-UsBNaPJlZqeOLvi6N8nyk")  # ou coloque direto entre aspas
bot = telebot.TeleBot(TOKEN)

# ===== BANCO =====
conn = sqlite3.connect("stats.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    mensagem_id INTEGER,
    data TEXT
)
""")
conn.commit()

# ===== SALVAR =====
def salvar(tipo, msg_id):
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO resultados (tipo, mensagem_id, data) VALUES (?, ?, ?)", (tipo, msg_id, data))
    conn.commit()

# ===== BARRA =====
def barra():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🟢 GREEN", callback_data="green"),
        InlineKeyboardButton("🔴 RED", callback_data="red"),
        InlineKeyboardButton("♻️ REEMBOLSO", callback_data="refund")
    )
    return kb

# ===== DETECTAR APOSTA AUTOMATICAMENTE =====
PALAVRAS = ["over", "under", "escanteio", "canto", "gol", "ht", "ft", "odd"]

@bot.message_handler(func=lambda msg: msg.text and any(p in msg.text.lower() for p in PALAVRAS))
def auto_barra(msg):
    # Só responde mensagens SUAS (profissional)
    ADMIN_ID = 7669721386  # COLOQUE SEU ID TELEGRAM AQUI
    
    if msg.from_user.id != ADMIN_ID:
        return

    bot.send_message(msg.chat.id, "📊 Marque o resultado:", reply_markup=barra())

# ===== CLIQUE NOS BOTÕES =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    msg_id = call.message.message_id

    if call.data == "green":
        salvar("green", msg_id)
        bot.answer_callback_query(call.id, "GREEN registrado 🟢")
        bot.edit_message_text("🟢 RESULTADO: GREEN CONFIRMADO", call.message.chat.id, msg_id)
    
    elif call.data == "red":
        salvar("red", msg_id)
        bot.answer_callback_query(call.id, "RED registrado 🔴")
        bot.edit_message_text("🔴 RESULTADO: RED CONFIRMADO", call.message.chat.id, msg_id)
    
    elif call.data == "refund":
        salvar("refund", msg_id)
        bot.answer_callback_query(call.id, "REEMBOLSO registrado ♻️")
        bot.edit_message_text("♻️ RESULTADO: REEMBOLSO", call.message.chat.id, msg_id)

# ===== RELATÓRIO =====
@bot.message_handler(commands=["relatorio"])
def relatorio(msg):
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='green'")
    green = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='red'")
    red = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='refund'")
    refund = c.fetchone()[0]

    total = green + red
    winrate = (green / total * 100) if total > 0 else 0

    bot.send_message(msg.chat.id, f"""
📊 RELATÓRIO VIP

🟢 Green: {green}
🔴 Red: {red}
♻️ Reembolso: {refund}

📈 Winrate: {winrate:.2f}%
""")

bot.infinity_polling()
