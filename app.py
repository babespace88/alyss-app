import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
FAL_KEY = os.environ.get("FAL_KEY")

SYSTEM_PROMPT = """You are a friendly AI prompt assistant. 

When users greet you (hi, hello, hey, helo, hai, salam, etc), respond warmly and explain what you can help with in their language.

You specialize in:
1. Image generation prompts 
2. Video generation prompts 

Your job is to help users:
- Create detailed, effective prompts for image generation
- Create motion prompts for video generation from images
- Improve and refine existing prompts
- Suggest creative ideas based on user descriptions

Always respond in the same language as the user.
When suggesting prompts, format them clearly and explain what each part does."""

user_history = {}

def get_history(user_id):
    if user_id not in user_history:
        user_history[user_id] = []
    return user_history[user_id]

def chat_fal(messages, user_message):
    url = "https://fal.run/fal-ai/any-llm"
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "anthropic/claude-3.5-sonnet",  # fix model name
        "system_prompt": SYSTEM_PROMPT,
        "messages": messages,
        "prompt": user_message
    }
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    print("Response:", data)
    return data.get("output") or data.get("response") or data.get("text") or str(data)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Hai! Apa yang boleh saya bantu?*\n\n"
        "Saya boleh bantu awak dengan:\n\n"
        "🎨 *Buat prompt image*\n"
        "_'buat prompt gambar wanita di Tokyo malam hari'_\n\n"
        "🎬 *Buat prompt video*\n"
        "_'buat motion prompt perempuan melambai'_\n\n"
        "✨ *Improve prompt sedia ada*\n"
        "_'improve prompt ni: a girl in park'_\n\n"
        "💡 *Minta idea prompt*\n"
        "_'cadangkan prompt untuk product photography'_\n\n"
        "Taip je apa yang awak nak! 😊",
        parse_mode="Markdown"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_history[user_id] = []
    await update.message.reply_text("🗑️ History cleared! Boleh start baru.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Cara Guna Bot*\n\n"
        "🎨 *Prompt image:*\n"
        "_'buat prompt gambar sunset di tepi pantai'_\n\n"
        "🎬 *Prompt video:*\n"
        "_'buat motion prompt untuk perempuan berjalan'_\n\n"
        "✨ *Improve prompt:*\n"
        "_'improve: a cat sitting'_\n\n"
        "💡 *Idea:*\n"
        "_'cadangkan prompt untuk product photography'_\n\n"
        "🔄 /clear — Reset conversation\n"
        "❓ /help — Tunjuk menu ini",
        parse_mode="Markdown"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    thinking = await update.message.reply_text("🤔 Sedang fikir...")

    try:
        history = get_history(user_id)
        reply = chat_fal(history, user_message)

        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})

        if len(history) > 20:
            history = history[-20:]
            user_history[user_id] = history

        await thinking.delete()
        await update.message.reply_text(reply)

    except Exception as e:
        print("Error:", e)
        await thinking.delete()
        await update.message.reply_text(f"❌ Error: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Chat Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
