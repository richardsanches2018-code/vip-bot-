import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# ===== COLOQUE SEU TOKEN AQUI =====
TOKEN = "8351324083:AAG0O16bSbF3k-UsBNaPJlZqeOLvi6N8nyk"
bot = telebot.TeleBot(TOKEN)

# ===== BANCO HISTÓRICO =====
conn = sqlite3.connect("stats.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    data TEXT
)
""")
conn.commit()

# ===== SALVAR RESULTADO =====
def salvar(tipo):
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO resultados (tipo, data) VALUES (?, ?)", (tipo, data))
    conn.commit()

# ===== BOTÕES =====
def teclado():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🟢 GREEN", callback_data="green"),
        InlineKeyboardButton("🔴 RED", callback_data="red"),
        InlineKeyboardButton("♻️ REEMBOLSO", callback_data="refund")
    )
    return kb

# ===== ENVIAR SINAL =====
@bot.message_handler(commands=["sinal"])
def sinal(msg):
    bot.send_message(msg.chat.id, "📊 RESULTADO DA OPERAÇÃO:", reply_markup=teclado())

# ===== CLIQUE NOS BOTÕES =====
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

# ===== RELATÓRIO TOTAL =====
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
    lucro = green - red

    texto = f"""
📊 RELATÓRIO VIP HISTÓRICO

🟢 Green: {green}
🔴 Red: {red}
♻️ Reembolso: {refund}

📈 Winrate: {winrate:.2f}%
💰 Lucro: {lucro} unidades
"""
    bot.send_message(msg.chat.id, texto)

# ===== START =====
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, "🤖 BOT VIP INSTITUCIONAL ONLINE")

# ===== RODAR =====
bot.infinity_polling()
