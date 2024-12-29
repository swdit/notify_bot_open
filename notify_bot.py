from custom_logging import *
import os
import re
import time
from telegram import Update, Chat
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from send_mail import send_notifyclient
from datetime import datetime, timezone
import yaml


# Read config.yml
def parse_config(config_file):
    with open(config_file, 'r') as f:
        config_int = yaml.safe_load(f)

    telegram_bot_token = config_int.get('telegram_bot_token', '')
    if telegram_bot_token == "" or not telegram_bot_token:
        logger.error("No telegram-token specified in YAML")
        exit()

    authorized_user = config_int.get('authorized_user', '')
    if authorized_user == "" or not authorized_user:
        logger.error("No authorized user specified in YAML")
        exit()

    pup = config_int.get('pup', '')
    if pup == "" or not pup:
        logger.warning("No PUP specified in YAML")
        authorized_user = ""

    pup_mail = config_int.get('pup_mail', '')
    if pup_mail == "" or not pup_mail:
        logger.error("No PUP E-Mail specified in YAML")
        exit()

    own_mail = config_int.get('own_mail', '')
    if own_mail == "" or not own_mail:
        logger.error("No own E-Mail specified in YAML")
        exit()

    own_mail_nm = config_int.get('own_mail_nm', '')
    if own_mail_nm == "" or not own_mail_nm:
        logger.warning("No own E-Mail sender name specified in YAML")
        authorized_user = ""

    own_mail_pw = config_int.get('own_mail_pw', '')
    if own_mail_pw == "" or not own_mail_pw:
        logger.error("No own E-Mail password (account access) specified in YAML")
        exit()

    bcc_mail = config_int.get('bcc_mail', '')
    if bcc_mail == "" or not bcc_mail:
        logger.warning("No BCC E-Mail specified in YAML")
        authorized_user = ""

    sal_mail = config_int.get('sal_mail', '')
    if sal_mail == "" or not sal_mail:
        logger.warning("No salutation specified in YAML - PUP might not understand the context of your E-Mail without")
        authorized_user = ""

    lea_mail = config_int.get('lea_mail', '')
    if lea_mail == "" or not lea_mail:
        logger.warning("No leave greeting specified in YAML")
        authorized_user = ""

    return {
        'TELEGRAM_BOT_TOKEN': telegram_bot_token,
        'AUTHORIZED_USER': authorized_user,
        'PUP': pup,
        'PUP_MAIL': pup_mail,
        'OWN_MAIL': own_mail,
        'OWN_MAIL_NM': own_mail_nm,
        'OWN_MAIL_PW': own_mail_pw,
        'BCC_MAIL': bcc_mail,
        'SAL_MAIL': sal_mail,
        'LEA_MAIL': lea_mail
    }


# Generate a safe filename
def generate_filename(base_name: str, counter: int) -> str:
    base_name = re.sub(r'[^a-zA-Z0-9_-]', '_', base_name)
    base_name = base_name[:20] if base_name else "notify_attachment"
    timestamp = time.strftime("%Y%m%d%H%M%S")
    filename = f"{base_name}_{timestamp}_{counter}"
    return filename


# Start command handler
async def start(update: Update) -> None:
    logger.info("Start command received")
    await update.message.reply_text("Hello! I am listening to all messages.")


# Handle incoming messages (text, photos, videos)
async def handle_message(update: Update) -> None:
    # check for private chat
    if update.message.chat.type != Chat.PRIVATE:
        logger.warning(f"Ignored message from chat type {update.message.chat.type}. Only private chats are allowed.")
        return

    # starting message handling
    message = update.message
    logger.info(f"Message content is {message}")

    user_name = update.effective_user.username
    logger.info(f"User Name is {user_name}")

    # get message time
    message_date = message.date
    # get current time
    current_time = datetime.now(timezone.utc)

    # calculate message age
    message_age = (current_time - message_date).total_seconds()
    logger.info(f"Message age is {message_age}")

    # Process only if the sender is authorized
    if user_name != AUTHORIZED_USER:
        logger.warning(f"Ignored message from {user_name}. Only processing messages from {AUTHORIZED_USER}.")
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    # Process only if the message is younger than 60 sek, to avoid spamming your PUP in case of a restart
    if message_age > 60:
        logger.warning(f"Ignored message. Only processing messages younger than 60 Sec.")
        return

    base_name = message.text if message.text else (message.caption if message.caption else "notify_attachment")
    counter = 1

    # Collect text and attachments
    collected_text = message.text or message.caption
    attachments = []

    # Check if there is any text to process
    if not collected_text and not message.photo and not message.video:
        await update.message.reply_text("Error: No text or media provided. Please include a message text or media.")
        logger.warning("Received a message without text or media. No email was sent.")
        return

    # Handling photos
    if message.photo:
        logger.info("Photo received")
        photo = message.photo[-1]
        filename = generate_filename(base_name, counter) + ".jpg"
        file_path = os.path.join("./images", filename)
        file = await photo.get_file()
        await file.download_to_drive(file_path)
        logger.info(f"Photo saved as {file_path}")
        attachments.append(file_path)
        counter += 1

    # Handling videos
    if message.video:
        logger.info("Video received")
        filename = generate_filename(base_name, counter) + ".mp4"
        file_path = os.path.join("./images", filename)
        file = await message.video.get_file()
        await file.download_to_drive(file_path)
        logger.info(f"Video saved as {file_path}")
        attachments.append(file_path)
        counter += 1

    # Check if we have both text and attachments
    if not collected_text or not attachments:
        await update.message.reply_text("Notice: Your message only contains text or media, and no email was sent.")
        logger.warning("Message contained only text or only media, so no email was sent.")
        return

    # Send email with the collected information
    try:
        subject = f"Meldung/Information an {PUP}:"
        recipients = [PUP_MAIL]  # Replace with actual recipient email addresses
        mail_success = send_notifyclient(OWN_MAIL_PW, OWN_MAIL, recipients, BCC_MAIL, SAL_MAIL, collected_text,
                                         LEA_MAIL, f"{subject} {base_name[:20]}", OWN_MAIL_NM, attachments)
        logger.info(f"Email sent successfully send to {recipients}.")

        # Send confirmation message via Telegram
        if mail_success:
            await update.message.reply_text(f"Your message has been sent to {recipients}")
        else:
            await update.message.reply_text(f"Error: Failed to send your message. Please try again later.")
    except Exception as err:
        logger.error(f"Failed to send email: {err}")
        await update.message.reply_text(f"Error: Failed to send your message. Please try again later.")


# Error handler
async def error(update: Update, context: CallbackContext) -> None:
    logger.error(f"Update {update} caused error: {context.error}")


# Main function to start the bot
def main() -> None:
    logger.info("Starting bot")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))
    application.add_handler(MessageHandler(filters.VIDEO, handle_message))

    # Register error handler
    application.add_error_handler(error)

    # Start the Bot
    application.run_polling()
    logger.info("Bot has stopped.")


# Read YAML
try:
    config = parse_config("./config.yml")
    logger.info("YAML-Config-File found and loaded")
except Exception as e:
    logger.error(f"YAML-Config-File could not be loaded or does not exist\nError: {e}")
    exit()


# Define your Telegram Bot token
TELEGRAM_BOT_TOKEN = config['TELEGRAM_BOT_TOKEN']

# Define User / Telegram-User-Name
AUTHORIZED_USER = config['AUTHORIZED_USER']

# Recipient/public_utilities_provider (PUP)
PUP = config['PUP']

# E-Mail address of Recipient / public utilities provider (PUP)
PUP_MAIL = config['PUP_MAIL']

# Own E-Mail
OWN_MAIL = config['OWN_MAIL']

# Own E-Mail Sender-Name
OWN_MAIL_NM = config['OWN_MAIL_NM']

# Own E-Mail-Account password
OWN_MAIL_PW = config['OWN_MAIL_PW']

# Bcc Mail for self-copy
BCC_MAIL = config['BCC_MAIL']

# Standard Salutation in the E-Mail to PUP
SAL_MAIL = config['SAL_MAIL']

# Standard Leave Formulation in the E-Mail to PUP
LEA_MAIL = config['LEA_MAIL']


# Set up Working directory to avoid problems when executed by pflist file
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
# Ensure the images directory exists
os.makedirs('./images', exist_ok=True)

logger.info(f"Current User: {subprocess.run(['whoami'], stdout=subprocess.PIPE, text=True).stdout.strip()}")


if __name__ == "__main__":
    main()
