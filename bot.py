import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
import os

TELEGRAM_TOKEN = os.getenv("8624321051:AAG4rMO52R5lZP5vSgyITfEohaB3UeIHVPA")
OPENAI_API_KEY = os.getenv("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")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Ты — мастер Dungeons & Dragons.
Веди текстовую RPG игру.
Создавай сюжет, события, врагов.
Будь кратким и атмосферным.
Иногда проси бросить d20.
"""

memory = {}

def roll_d20():
    return random.randint(1, 20)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    memory[update.effective_user.id] = []
    await update.message.reply_text("🎮 D&D началась! Пиши действия.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in memory:
        memory[user_id] = []

    if "куб" in text.lower():
        text += f" (d20={roll_d20()})"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *memory[user_id][-10:],
                {"role": "user", "content": text}
            ]
        )

        answer = response.choices[0].message.content

        memory[user_id].append({"role": "user", "content": text})
        memory[user_id].append({"role": "assistant", "content": answer})

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
