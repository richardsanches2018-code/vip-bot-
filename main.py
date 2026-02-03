import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

BOT_TOKEN = os.getenv("8351324083:AAG0O16bSbF3k-UsBNaPJlZqeOLvi6N8nyk")

# Relatório em memória
dados = {
    "green": 0,
    "red": 0,
    "refund": 0
}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot online!\n\n"
        "Use /aposta para registrar uma entrada\n"
        "Use /relatorio para ver os resultados"
    )

# /aposta
async def aposta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🟢 GREEN", callback_data="green"),
            InlineKeyboardButton("🔴 RED", callback_data="red"),
            InlineKeyboardButton("♻️ REEMBOLSO", callback_data="refund")
        ]
    ]

    await update.message.reply_text(
        "📊 Entrada registrada\n\n"
        "Selecione o resultado:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Clique nos botões
async def resultado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "green":
        dados["green"] += 1
        texto = "🟢 GREEN confirmado!"
    elif query.data == "red":
        dados["red"] += 1
        texto = "🔴 RED confirmado!"
    else:
        dados["refund"] += 1
        texto = "♻️ Reembolso registrado!"

    await query.edit_message_text(texto)

# /relatorio
async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = dados["green"] + dados["red"] + dados["refund"]

    await update.message.reply_text(
        f"📈 RELATÓRIO\n\n"
        f"🟢 Greens: {dados['green']}\n"
        f"🔴 Reds: {dados['red']}\n"
        f"♻️ Reembolso: {dados['refund']}\n\n"
        f"📊 Total: {total}"
    )

# MAIN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aposta", aposta))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(CallbackQueryHandler(resultado))

    print("🤖 Bot rodando no Railway")
    app.run_polling()

if __name__ == "__main__":
    main()
