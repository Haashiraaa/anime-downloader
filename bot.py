

# bot.py - Simple Telegram Bot for Anime Downloader


import os
import sys
import logging
from typing import Optional
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes
)

from anime_dl.main import AnimeDownloader
from haashi_pkg.utility import Logger


# Bot token from environment variable (for Railway)
BOT_TOKEN = os.getenv("TG_ANIME_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when /start is issued"""

    welcome_text = (
        "👋 *Welcome to Anime Downloader Bot!*\n\n"
        "📺 Send me an anime URL and I'll download it for you!\n\n"
        "*Commands:*\n"
        "/download <url> - Download anime\n"
        "/help - Show this message\n\n"
        "*Example:*\n"
        "`/download https://animeheaven.me/anime.php?9rp26`"
    )

    assert update.message
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send help message"""

    help_text = (
        "*How to use:*\n\n"
        "1️⃣ Send /download followed by anime URL\n"
        "2️⃣ Wait for download to complete\n"
        "3️⃣ Get your anime!\n\n"
        "*Tips:*\n"
        "• Use AnimeHeaven URLs\n"
        "• Downloads are saved automatically\n"
        "• Be patient for large downloads\n\n"
        "*Example:*\n"
        "`/download https://animeheaven.me/anime.php?9rp26`"
    )

    assert update.message
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def download_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /download command"""

    # Check if URL was provided (and is not empty)
    if not context.args:
        assert update.message
        await update.message.reply_text(
            "❌ Please provide an anime URL!\n\n"
            "Usage: `/download <url>`\n"
            "Example: `/download https://animeheaven.me/anime.php?9rp26`",
            parse_mode='Markdown'
        )
        return

    url = context.args[0]

    # Notify user download started
    assert update.message
    await update.message.reply_text(
        f"🔽 *Starting download...*\n"
        f"URL: `{url}`\n\n"
        f"⏳ This may take a few minutes...",
        parse_mode='Markdown'
    )

    try:

        AnimeDownloader.main([url])

        # Success message
        await update.message.reply_text(
            "✅ *Download Complete!*\n\n"
            "📁 Check your downloads folder!",
            parse_mode='Markdown'
        )

    except Exception as e:
        # Error message
        await update.message.reply_text(
            f"❌ *Download Failed*\n\n"
            f"Error: `{str(e)}`\n\n"
            f"Please check the URL and try again.",
            parse_mode='Markdown'
        )


async def url_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle URLs sent directly (without /download command)"""

    assert update.message is not None
    message_text = update.message.text

    # Check if message contains animeheaven URL
    assert message_text is not None
    if 'animeheaven' in message_text.lower():
        # Extract URL
        url = message_text.strip()

        # Call download command with the URL
        context.args = [url]
        await download_command(update, context)
    else:
        await update.message.reply_text(
            "👋 Send me an AnimeHeaven URL to download!\n"
            "Or use /help for more info."
        )


async def error_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    logger: Optional[Logger] = None
) -> None:
    """Handle errors"""
    logger = logger or Logger(logging.INFO)
    logger.error(f"Update {update} caused error {context.error}")


def main(logger: Optional[Logger] = None) -> None:
    """Start the bot"""

    logger = logger or Logger(logging.INFO)
    try:
        logger.info("🤖 Starting Anime Downloader Bot...")
        assert BOT_TOKEN is not None
        logger.info(f"📡 Token: {BOT_TOKEN[:10]}...")

        # Create application
        app = Application.builder().token(BOT_TOKEN).build()

        # Add command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("download", download_command))

        # Handle URLs sent directly
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, url_handler))

        # Error handler
        app.add_error_handler(error_handler)  # type: ignore

        logger.info("✅ Bot is running!")
        logger.info("Press Ctrl+C to stop")

        # Start polling for messages
        app.run_polling(allowed_updates=Update.ALL_TYPES)

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(exception=e, save_to_json=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
