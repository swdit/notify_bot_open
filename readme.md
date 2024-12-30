# Notify Bot Open
A Simple Notification Tool to inform Public Utility Providers (PUPs), regarding issues in public areas.

## Overview
Notify Bot Open is a simple notification tool that allows you to send a commented picture to a Telegram channel, which is then converted into properly formatted email and sent to the mail address of your public utility provider.

## Setup

### Telegram Setup

1. Create a Telegram bot: [How-to guide](https://sarafian.github.io/low-code/2020/03/24/create-private-telegram-chatbot.html)
2. Create a private channel and invite your bot
3. Get the access token for your bot

### Python Setup

1. Clone this repository
2. Alter the `config.yml` file with your credentials
3. Install dependencies
4. Execute the script

## Configuration File (config.yml)

The configuration file is used to store your credentials and settings. You need to configure it before running the script.

## Security Measures

To prevent abuse, Notify Bot Open includes several security measures:

* Only messages from the Telegram username set in the `config.yml` are accepted as sender
* Only messages younger than 60 seconds are taken into account to prevent spamming of old messages
* Messages from group chats are not taken into account
* Messages that only contain text or only contain an image are also ignored
* Messages with a very short explanation text (less than 10 characters) are also ignored

## How-to Use

1. Send a commented picture to the Telegram channel created in the setup process.
2. The script will convert your message into a properly formatted email and send it to the mail address of your public utility provider.


Example:

Suppose you send the following text as a comment: "overfilled garbage can in the central park near main entrance"

The script will format this text into an email that looks like this:
```
Dear Sir or Madam,

Information:
overfilled garbage can in the central park near main entrance

Best regards,
Jane Doe
```

Note: Make sure to configure the `config.yml` file correctly before running the script.


Here's an explanation of each field:

* `telegram_bot_token`: Your Telegram bot's access token, obtained during the setup process.
* `authorized_user`: The username of the authorized user who can send messages to the Telegram channel.
* `pup`: The name of the public utility provider you want to notify.
* `pup_mail`: The email address of the public utility provider.
* `own_mail`: Your own email address, used for sending and receiving emails.
* `own_mail_nm`: Your full name, used in the email signature.
* `own_mail_pw`: Your email password, used for authentication.
* `bcc_mail`: A backup email address to receive a copy of each sent email (optional).
* `sal_mail`: The salutation text used at the beginning of each email.
* `lea_mail`: The leave text used at the end of each email.

Example:
```
telegram_bot_token: "your_telegram_bot_access_token"
authorized_user: "your_telegram_user_name"
pup: "the_name_of_the_public_utility_provider_pup_you_want_to_notify"
pup_mail: "pup@mail.com"
own_mail: "your@mail.com"
own_mail_nm: "your_name"
own_mail_pw: "your_supersecret_mail_password"
bcc_mail: "bcc@mail.com"
sal_mail: "Sehr geehrte Damen und Herren,\n\nich moechte folgende Information/Auffaelligkeit melden:\n\n"
lea_mail: "\nMit freundlichen Grüßen\nMaxime Mustermann"
```
Make sure to replace the placeholders with your actual credentials and settings.