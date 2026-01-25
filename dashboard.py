import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3, os, time
from datetime import datetime

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ===== BANCO =====
conn = sqlite3.connect("/tmp/vip.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    data DATE DEFAULT (date('now'))
)
""")
conn.commit()

# ===== SALVAR =====
def salvar(tipo):
    c.execute("INSERT INTO resultados (tipo) VALUES (?)", (tipo,))
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
@bot.message_handler(commands=['sinal'])
def sinal(msg):
    bot.send_message(msg.chat.id, "📊 RESULTADO DA OPERAÇÃO:", reply_markup=teclado())

# ===== CALLBACK =====
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
def stats():
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='green'")
    green = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='red'")
    red = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='refund'")
    refund = c.fetchone()[0]
    total = green + red
    winrate = (green / total * 100) if total > 0 else 0
    lucro = green * 1 - red * 1  # ajuste stake
    return green, red, refund, winrate, lucro

@bot.message_handler(commands=['relatorio'])
def relatorio(msg):
    green, red, refund, winrate, lucro = stats()
    texto = f"""
📊 RELATÓRIO VIP INSTITUCIONAL

🟢 Green: {green}
🔴 Red: {red}
♻️ Reembolso: {refund}

📈 Winrate: {winrate:.2f}%
💰 Lucro (unidades): {lucro}
"""
    bot.send_message(msg.chat.id, texto)

# ===== RESET DIÁRIO AUTOMÁTICO =====
def reset_diario():
    while True:
        agora = datetime.now().strftime("%H:%M")
        if agora == "00:00":
            c.execute("DELETE FROM resultados")
            conn.commit()
            print("Reset diário feito")
            time.sleep(60)
        time.sleep(10)

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "🤖 VIP INSTITUCIONAL 2.0 ONLINE")

# ===== LOOP =====
import threading
threading.Thread(target=reset_diario).start()
bot.infinity_polling()
