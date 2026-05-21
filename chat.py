from ollama import chat, ChatResponse
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN_HERE"
MODEL = "gemma4:31b"

SYSTEM_PROMPT = """You are an expert AI prompt engineer specializing in:
1. Image generation prompts (Seedream, Stable Diffusion, Flux, Midjourney)
2. Video generation prompts (Seedance, Kling, Hailuo)

Your job is to help users:
- Create detailed, effective prompts for image generation
- Create motion prompts for video generation from images
- Improve and refine existing prompts
- Suggest creative ideas based on user descriptions

Always respond in the same language as the user.
When suggesting prompts, format them clearly and explain what each part does."""

# ─── Simpan history per user ───
user_history = {}

def get_history(user_id):
    if user_id not in user_history:
        user_history[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    return user_history[user_id]

# ─── Chat dengan Ollama ───
def chat_ollama(messages):
    response: ChatResponse = chat(
        model=MODEL,
        messages=messages
    )
    return response.message.content

# ─── Handler /start ───
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *AI Prompt Assistant*\n\n"
        "Saya boleh bantu awak buat prompt untuk:\n\n"
        "🎨 *Image Generation*\n"
        "_'buat prompt gambar wanita di Tokyo malam hari'_\n\n"
        "🎬 *Video Generation*\n"
        "_'buat motion prompt perempuan melambai'_\n\n"
        "✨ *Improve Prompt*\n"
        "_'improve prompt ni: a girl in park'_\n\n"
        "Taip je apa yang awak nak! 🚀",
        parse_mode="Markdown"
    )

# ─── Handler /clear ───
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_history[user_id] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    await update.message.reply_text("🗑️ History cleared! Boleh start baru.")

# ─── Handler /help ───
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

# ─── Handler teks ───
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    thinking = await update.message.reply_text("🤔 Sedang fikir...")

    try:
        history = get_history(user_id)
        history.append({"role": "user", "content": user_message})

        reply = chat_ollama(history)

        history.append({"role": "assistant", "content": reply})

        # Limit history
        if len(history) > 21:
            history = [history[0]] + history[-20:]
            user_history[user_id] = history

        await thinking.delete()
        await update.message.reply_text(reply)

    except Exception as e:
        print("Error:", e)
        await thinking.delete()
        await update.message.reply_text(
            "❌ Gagal connect ke Ollama.\n\n"
            "Pastikan Ollama running:\n"
            "`ollama serve`",
            parse_mode="Markdown"
        )

# ─── Run Bot ───
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