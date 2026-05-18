import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# ============================================================
#  CONFIGURATION — fill these in before running
# ============================================================

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")  # From BotFather

ADMIN_ID = 689045542  # Your Telegram user ID (see README for how to find this)

GROUP_CHAT_IDS = [
    -5244890092,  # Group 1  (replace with your real group IDs)
    -5121742879,  # Group 2
]

# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receives a DM from the admin and broadcasts ANY message type to all groups."""

    # Ignore messages that aren't from the admin
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ You are not authorized to use this bot.")
        return

    # Only handle private (DM) messages
    if update.effective_chat.type != "private":
        return

    success = 0
    failed = 0

    for chat_id in GROUP_CHAT_IDS:
        try:
            await context.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
            success += 1

        except Exception as e:
            logging.error(f"Failed to copy message to {chat_id}: {e}")
            failed += 1

    await update.message.reply_text(
        f"✅ Sent to {success} group(s)" +
        (f"\n❌ Failed: {failed}" if failed else "")
    )


async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Helper command — DM the bot /myid to get your Telegram user ID."""
    uid = update.effective_user.id
    cid = update.effective_chat.id
    await update.message.reply_text(
        f"👤 Your user ID: `{uid}`\n💬 This chat ID: `{cid}`",
        parse_mode="Markdown"
    )


async def get_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run /groupid inside a group to get its chat ID."""
    cid = update.effective_chat.id
    name = update.effective_chat.title or "this chat"
    await update.message.reply_text(
        f"💬 Chat ID for *{name}*: `{cid}`",
        parse_mode="Markdown"
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("myid", get_my_id))
    app.add_handler(CommandHandler("groupid", get_group_id))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
