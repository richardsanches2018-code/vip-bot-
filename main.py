import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3, time, os
from datetime import datetime

# ===== TOKEN =====
TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    TOKEN = "8351324083:AAG0O16bSbF3k-UsBNaPJlZqeOLvi6N8nyk"

bot = telebot.TeleBot(TOKEN)

# ===== BANCO =====
conn = sqlite3.connect("vip.db", check_same_thread=False)
c = conn.cursor()

# RESULTADOS
c.execute("""
CREATE TABLE IF NOT EXISTS resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    mercado TEXT,
    msg_id INTEGER,
    data TEXT
)
""")

# APOSTAS ATIVAS
c.execute("""
CREATE TABLE IF NOT EXISTS apostas (
    msg_id INTEGER,
    inicio INTEGER,
    mercado TEXT
)
""")
conn.commit()

# ===== CONFIG =====
TEMPO_MAX = 90 * 60  # 90 minutos (mude se quiser)

# ===== BARRA =====
def barra():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🟢 GREEN", callback_data="green"),
        InlineKeyboardButton("🔴 RED", callback_data="red"),
        InlineKeyboardButton("♻️ REEMBOLSO", callback_data="refund")
    )
    return kb

# ===== SALVAR APOSTA =====
def salvar_aposta(msg_id, mercado):
    inicio = int(time.time())
    c.execute("INSERT INTO apostas VALUES (?, ?, ?)", (msg_id, inicio, mercado))
    conn.commit()

# ===== SALVAR RESULTADO =====
def salvar_resultado(tipo, msg_id):
    data = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT mercado FROM apostas WHERE msg_id=?", (msg_id,))
    mercado = c.fetchone()
    mercado = mercado[0] if mercado else "desconhecido"

    c.execute("INSERT INTO resultados (tipo, mercado, msg_id, data) VALUES (?, ?, ?, ?)",
              (tipo, mercado, msg_id, data))
    conn.commit()

# ===== VERIFICAR TEMPO =====
def expirou(msg_id):
    c.execute("SELECT inicio FROM apostas WHERE msg_id=?", (msg_id,))
    r = c.fetchone()
    if not r:
        return True
    return int(time.time()) - r[0] > TEMPO_MAX

# ===== DETECTAR APOSTA DO FOLLOWAL =====
PALAVRAS_GOL = ["over", "under", "gol", "ht", "ft"]
PALAVRAS_CANTO = ["escanteio", "canto", "corners"]

@bot.message_handler(func=lambda msg: msg.text and ("Odd" in msg.text or "odd" in msg.text))
def detectar_aposta(msg):
    texto = msg.text.lower()
    mercado = "outro"

    if any(p in texto for p in PALAVRAS_GOL):
        mercado = "gols"
    if any(p in texto for p in PALAVRAS_CANTO):
        mercado = "escanteios"

    # adiciona barra NA MESMA mensagem
    try:
        bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=barra())
        salvar_aposta(msg.message_id, mercado)
    except:
        pass

# ===== CLIQUE GREEN/RED =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    msg_id = call.message.message_id

    if expirou(msg_id):
        bot.answer_callback_query(call.id, "⏱️ JOGO ENCERRADO (tempo limite)")
        return

    if call.data == "green":
        salvar_resultado("green", msg_id)
        bot.answer_callback_query(call.id, "GREEN registrado 🟢")
        bot.edit_message_text(call.message.text + "\n\n🟢 RESULTADO: GREEN", call.message.chat.id, msg_id, reply_markup=barra())

    elif call.data == "red":
        salvar_resultado("red", msg_id)
        bot.answer_callback_query(call.id, "RED registrado 🔴")
        bot.edit_message_text(call.message.text + "\n\n🔴 RESULTADO: RED", call.message.chat.id, msg_id, reply_markup=barra())

    elif call.data == "refund":
        salvar_resultado("refund", msg_id)
        bot.answer_callback_query(call.id, "REEMBOLSO ♻️")
        bot.edit_message_text(call.message.text + "\n\n♻️ RESULTADO: REEMBOLSO", call.message.chat.id, msg_id, reply_markup=barra())

# ===== PAINEL VIP =====
@bot.message_handler(commands=["start"])
def painel(msg):
    bot.send_message(msg.chat.id, f"""
🤖 PAINEL VIP INSTITUCIONAL

📊 MERCADOS:
✔ GOLS HT / FT
✔ ESCANTEIOS HT / FT

💎 PLANO VIP
Mensal: R$97
Vitalício: R$297

💰 PIX:
Richard Sanches da Cruz
Chave: SUA_CHAVE_PIX

📈 Comandos:
➡ /relatorio
➡ /diario
➡ /mensal
""")

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
    winrate = (green/total*100) if total>0 else 0

    bot.send_message(msg.chat.id, f"""
📊 RELATÓRIO HISTÓRICO VIP

🟢 Green: {green}
🔴 Red: {red}
♻️ Reembolso: {refund}
📈 Winrate: {winrate:.2f}%
""")

# ===== RELATÓRIO DIÁRIO =====
@bot.message_handler(commands=["diario"])
def diario(msg):
    hoje = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='green' AND data=?", (hoje,))
    green = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='red' AND data=?", (hoje,))
    red = c.fetchone()[0]
    total = green+red
    winrate = (green/total*100) if total>0 else 0

    bot.send_message(msg.chat.id, f"""
📊 RELATÓRIO DIÁRIO

🟢 Green: {green}
🔴 Red: {red}
📈 Winrate: {winrate:.2f}%
""")

# ===== RELATÓRIO MENSAL =====
@bot.message_handler(commands=["mensal"])
def mensal(msg):
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='green'")
    green = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM resultados WHERE tipo='red'")
    red = c.fetchone()[0]
    total = green+red
    winrate = (green/total*100) if total>0 else 0

    bot.send_message(msg.chat.id, f"""
📆 RELATÓRIO MENSAL VIP

🟢 Green: {green}
🔴 Red: {red}
📈 Winrate: {winrate:.2f}%
""")

bot.infinity_polling()
