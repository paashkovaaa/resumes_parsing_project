import os

from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    Application,
)

from telegram_bot.telegram_bot import (
    SELECT_SITE,
    select_site,
    SET_POSITION,
    set_position,
    SET_LOCATION,
    SET_KEYWORDS,
    FETCH_RESUMES,
    set_location,
    set_keywords,
    fetch_resumes,
    cancel,
)

from telegram_bot.telegram_bot import start


def main() -> None:
    application = (
        Application.builder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_SITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_site)],
            SET_POSITION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_position)
            ],
            SET_LOCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_location)
            ],
            SET_KEYWORDS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_keywords)
            ],
            FETCH_RESUMES: [CommandHandler("fetch", fetch_resumes)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.add_handler(CommandHandler("start", start))

    application.run_polling()


if __name__ == "__main__":
    main()
