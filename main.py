import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3, os
from datetime import datetime

TOKEN = os.getenv("TOKEN") or "COLE_SEU_TOKEN_AQUI"
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

# ===== DETECTAR APOSTA (BETBOTS / FORWARDER) =====
@bot.message_handler(func=lambda msg: msg.text and (
    "oportunidade" in msg.text.lower() or
    "estratégia" in msg.text.lower() or
    "bet365" in msg.text.lower() or
    "liga" in msg.text.lower()
))
def auto_barra(msg):
    try:
        bot.edit_message_reply_markup(
            msg.chat.id,
            msg.message_id,
            reply_markup=barra()
        )
    except:
        pass

# ===== CLIQUE NOS BOTÕES =====
@bot.callback_query_handler(func=lambda call: True)
def clicar(call):
    msg_id = call.message.message_id
    data = datetime.now().strftime("%Y-%m-%d")

    # evita marcar duas vezes
    c.execute("SELECT * FROM resultados WHERE msg_id=?", (msg_id,))
    if c.fetchone():
        bot.answer_callback_query(call.id, "⚠️ Já marcado")
        return

    if call.data == "green":
        tipo = "green"
    elif call.data == "red":
        tipo = "red"
    else:
        tipo = "refund"

    c.execute("INSERT INTO resultados (tipo,msg_id,data) VALUES (?,?,?)", (tipo,msg_id,data))
    conn.commit()

    bot.answer_callback_query(call.id, f"{tipo.upper()} REGISTRADO")

# ===== PAINEL VIP =====
@bot.message_handler(commands=["start"])
def painel(msg):
    bot.send_message(msg.chat.id, f"""
🤖 VIP INSTITUCIONAL

⚽ GOLS HT / FT
⛳ ESCANTEIOS HT / FT

💰 VIP MENSAL: R$25
Pix: SUA CHAVE PIX

📊 /relatorio
""")

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
    winrate = (green/total*100) if total > 0 else 0

    bot.send_message(msg.chat.id, f"""
📊 RELATÓRIO VIP

🟢 Green: {green}
🔴 Red: {red}
♻️ Reembolso: {refund}
📈 Winrate: {winrate:.2f}%
""")

bot.infinity_polling()
