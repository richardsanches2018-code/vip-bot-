import telebot, os, psycopg2
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = telebot.TeleBot(TOKEN)

# ===== CONEXÃO =====
conn = psycopg2.connect(DATABASE_URL)
c = conn.cursor()

# ===== TABELA =====
c.execute("""
CREATE TABLE IF NOT EXISTS resultados (
    id SERIAL PRIMARY KEY,
    tipo TEXT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ===== SALVAR =====
def salvar(tipo):
    c.execute("INSERT INTO resultados (tipo) VALUES (%s)", (tipo,))
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

# ===== RELATÓRIO TOTAL =====
def stats():
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='green'")
    green = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='red'")
    red = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='refund'")
    refund = c.fetchone()[0]

    total = green + red
    winrate = (green / total * 100) if total > 0 else 0
    lucro = green - red

    return green, red, refund, winrate, lucro

@bot.message_handler(commands=['relatorio'])
def relatorio(msg):
    green, red, refund, winrate, lucro = stats()
    texto = f"""
📊 RELATÓRIO HISTÓRICO VIP

🟢 Green total: {green}
🔴 Red total: {red}
♻️ Reembolso: {refund}

📈 Winrate geral: {winrate:.2f}%
💰 Lucro total: {lucro} unidades
"""
    bot.send_message(msg.chat.id, texto)

# ===== RELATÓRIO MENSAL =====
@bot.message_handler(commands=['mensal'])
def mensal(msg):
    c.execute("""
    SELECT 
        SUM(CASE WHEN tipo='green' THEN 1 ELSE 0 END),
        SUM(CASE WHEN tipo='red' THEN 1 ELSE 0 END)
    FROM resultados 
    WHERE date_trunc('month', data) = date_trunc('month', CURRENT_DATE)
    """)
    green, red = c.fetchone()
    green = green or 0
    red = red or 0
    total = green + red
    winrate = (green/total*100) if total>0 else 0

    bot.send_message(msg.chat.id, f"""
📆 RELATÓRIO MENSAL VIP

🟢 Green: {green}
🔴 Red: {red}
📈 Winrate: {winrate:.2f}%
""")

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "🤖 VIP INSTITUCIONAL HISTÓRICO ONLINE")

bot.infinity_polling()
