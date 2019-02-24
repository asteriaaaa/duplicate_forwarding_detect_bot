from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram.messageentity
import bot_db as db
import logging
import datetime
import json
import sys

TRIGGERS = {}
BAN_IDS = []
INIT_TIMESTAMP = datetime.datetime.now()


def process_chat_message(bot, update):
    print(str(update.message.date) , update.message.chat_id)
    if not update.message.text:
        print('no text')
        return
    if update.message.forward_from or update.message.forward_from_chat:
        duplicated = db.search_duplicate(update.message.text, update.message.chat_id)
        if duplicated:
            duplicated = list(duplicated)
            link = 'tg://openmessage?chat_id=' + str(duplicated[2]) + '&message_id=' + str(duplicated[0])
            update.message.reply_text(text='<a href="' + link + '">Duplicated!</a>', parse_mode=telegram.ParseMode.HTML)
            return
        if (len(update.message.text) >= 20):
            print('saved one forward')
            db.log_message(message_id=update.message.message_id, text=update.message.text,
                            chat_id=update.message.chat_id,
                            user_id=update.message.from_user.id, time=update.message.date)



def show_help(bot, update):
    if update.message.date < INIT_TIMESTAMP:
        return
    if update.message.from_user.id in BAN_IDS:
        return
    text = 'Just detect long duplicated forwards.'
    update.message.reply_text(text)


def main():
    config = {}
    try:
        with open('config.json') as f:
            config = json.load(f)
    except json.JSONDecodeError or FileNotFoundError:
        print('Bad config!!!')
        exit(1)

    global BAN_IDS
    BAN_IDS = config['ban_id']
    db.__init__(config['db_path'], config['db_user'], config['db_passwd'], config['db_name'])
    if len(sys.argv) >= 2:
        if sys.argv[1] == '--setup':
            db.setup()
    logging.basicConfig(level=config['debug_level'])

    updater = Updater(token=config['bot_token'])
    updater.dispatcher.add_handler(MessageHandler(Filters.all, process_chat_message, allow_edited=True), group=-1)
    # text logger & counter & user info update & recent edits
    updater.dispatcher.add_handler(CommandHandler('help', show_help))
    # process text triggers
    updater.start_polling()


if __name__ == '__main__':
    main()
