import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    CallbackContext,
)
import openai

# Настройка OpenAI и Telegram API
openai.api_key = "openai.api_key"

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Основной промпт, обучающий модель стилю
base_prompt = """
You are generating engaging weekly newsletters on any given topic, as requested by the user.
Each newsletter should follow a friendly, simple, and professional tone, emphasizing clarity, actionable advice, and reader engagement.
Your newsletters must include:
1. **Introduction**
   - Start with a warm, welcoming greeting (e.g., "Hi there, Hydro Heroes!").
   - Briefly summarize the key topics to be covered in the email in an inviting manner.
2. **Main Content**
   - Provide **detailed, easy-to-follow guidance** on the requested topic.
   - Divide the content into **2–4 subtopics**, with clear actionable advice for each.
   - Use **bullet points** for clarity and easy readability.
   - Incorporate the following emojis to make the content visually appealing: 🌱, 🌿, 🌞.
   - Ensure smooth transitions between subtopics for a cohesive flow.
3. **Conclusion**
   - Summarize the main points of the email in a clear and concise way.
   - Add a friendly **call to action**, encouraging readers to share their experiences, ask questions, or get involved.
   - Include a **personalized sign-off** like this:
     > **"Want to support my work? Consider donating to my TipJar!"**  
     > **Chris Cook 🌱**  
     > Founder of **Happy Hydro Farm**
4. **Additional Requirements**
   - Maintain a consistent structure across all newsletters.
   - Use concise and professional language with a touch of warmth.
   - Adapt content to suit the given topic while keeping the tone engaging and approachable.
   - Include appropriate emojis 🌱🌿🌞 throughout the email to highlight key points.
"""


# Функция генерации текста
def generate_email(user_prompt, language):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Можно изменить на другую модель, если нужно
            messages=[
                {"role": "system", "content": f"Write the email in {language}."},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,  # Более креативный ответ
            max_tokens=300,  # Максимальное количество токенов в ответе (можно настроить)
        )
        return response["choices"][0]["message"]["content"]
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        return (
            "Sorry, I couldn't generate an email at the moment. Please try again later."
        )


# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Русский", callback_data="ru")],
        [InlineKeyboardButton("English", callback_data="en")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please select a language for communication:", reply_markup=reply_markup
    )

    context.user_data["language"] = "en"  # Default to English


# Языковая настройка
async def language_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data in ["ru", "en"]:
        context.user_data["language"] = query.data
        await query.message.reply_text("Language selected. Now send me your prompt.")


# Генерация и отправка email по промпту
async def handle_message(update: Update, context: CallbackContext) -> None:
    language = context.user_data.get("language", "en")
    user_prompt = update.message.text
    email_content = generate_email(user_prompt, language)

    await update.message.reply_text(email_content)


# Основная функция для инициализации бота
async def main() -> None:
    # Создаем объект Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(language_selection))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Запуск бота
    await application.run_polling()


if __name__ == "__main__":
    import nest_asyncio

    nest_asyncio.apply()  # Позволяет использовать уже запущенный событийный цикл
    import asyncio

    asyncio.run(main())
