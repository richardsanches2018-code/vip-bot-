import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ===== BANCO DE DADOS =====
conn = sqlite3.connect("/tmp/stats.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ===== FUNÇÃO PRA SALVAR =====
def salvar(tipo):
    c.execute("INSERT INTO resultados (tipo) VALUES (?)", (tipo,))
    conn.commit()

# ===== BOTÕES =====
def teclado_resultado():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🟢 GREEN", callback_data="green"),
        InlineKeyboardButton("🔴 RED", callback_data="red"),
        InlineKeyboardButton("♻️ REEMBOLSO", callback_data="refund")
    )
    return kb

# ===== ENVIAR SINAL =====
@bot.message_handler(commands=['sinal'])
def sinal(msg):
    bot.send_message(msg.chat.id, "📊 RESULTADO DA APOSTA:", reply_markup=teclado_resultado())

# ===== BOTÕES CALLBACK =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "green":
        salvar("green")
        bot.answer_callback_query(call.id, "GREEN registrado 🟢")
    elif call.data == "red":
        salvar("red")
        bot.answer_callback_query(call.id, "RED registrado 🔴")
    elif call.data == "refund":
        salvar("refund")
        bot.answer_callback_query(call.id, "REEMBOLSO registrado ♻️")

# ===== RELATÓRIO =====
@bot.message_handler(commands=['relatorio'])
def relatorio(msg):
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='green'")
    green = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='red'")
    red = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='refund'")
    refund = c.fetchone()[0]

    total = green + red
    winrate = (green / total * 100) if total > 0 else 0

    texto = f"""📊 RELATÓRIO VIP

🟢 Green: {green}
🔴 Red: {red}
♻️ Reembolso: {refund}

🎯 Winrate: {winrate:.2f}%
"""
    bot.send_message(msg.chat.id, texto)

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "🤖 Bot VIP Institucional Online")

bot.infinity_polling()
