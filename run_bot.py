from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram.messageentity
import bot_db as db
import logging
import datetime
import json
import sys
import time
import random

TRIGGERS = {}
BAN_IDS = []
INIT_TIMESTAMP = datetime.datetime.now()
git_fileid = ''

def process_chat_message(bot, update):
    if not update.message:
        print('no message entity', time.time())
        return
    print(str(update.message.date) , update.message.chat_id)
    if update.message.new_chat_members:
        bot.sendMessage(chat_id=update.message.chat_id ,text='有')
        return
    if not update.message.text:
        print('no text')
        return
    if update.message.text == '#群组图片':
        bot.sendMessage(chat_id=update.message.chat_id, text='CDD又换头像啦')
    if update.message.text and (len(update.message.text) <= 40):
        print('short message')
        return
    print(update.channel_post)

    
    if update.message.forward_from or update.message.forward_from_chat:
        duplicated = db.search_duplicate(update.message.text, update.message.chat_id)
        if duplicated:
            print('duplicated')
            duplicated = list(duplicated)
            link = 'tg://openmessage?chat_id=' + str(duplicated[2]) + '&message_id=' + str(duplicated[0])
            #mse = MessageEntity(offset=0, length=len(link), type='text_link', url=link)
            #msg = Message(message_id=update.message.message_id, from_user=0, date=update.message.date, chat=update.message.chat_id, text='Duplicated')
            #update.message.reply_text(text=msg.parse_entity(mse))
            #update.message.reply_text(type='text_link', link=link, text='Duplicated!')
            update.message.reply_text(text='<a href="' + link + '">Duplicated!</a>', parse_mode=telegram.ParseMode.HTML)
            return
        if (len(update.message.text) >= 20):
            print('saved one forward')
            db.log_message(message_id=update.message.message_id, text=update.message.text, chat_id=update.message.chat_id,user_id=update.message.from_user.id, time=update.message.date)
    print(update.message.from_user['first_name'] + ": " + update.message.text)

#    if update.message.text or update.message.forward_from_chat:
 #       print('saved one forward')
  #      db.log_message(message_id=update.message.message_id, text=update.message.text,
   #                   chat_id=update.message.chat_id,
    #                  user_id=update.message.from_user.id, time=update.message.date)
    #else:
     #   print('no save')



def show_help(bot, update):
    if update.message.date < INIT_TIMESTAMP:
        return
    if update.message.from_user.id in BAN_IDS:
        return
    text = 'Just detect long duplicated forwards.'
    update.message.reply_text(text)


def stats(bot, update):
    if update.message.date < INIT_TIMESTAMP:
        return
    if update.message.from_user.id in BAN_IDS:
        return
    result = db.query_chat_stats(update.message.chat_id)
    if not result:
        update.message.reply_text('No stats to show')
    else:
        lines = []
        for user in result:
            lines.append('%s %s (%d) => %d' % user)
        update.message.reply_text('\n'.join(lines), quote=False)

def send_police(bot, update):
    police_car = u'\U0001F693'
    rand = int((random.random() + 1) * 10)
    cars='FBI! open the door '
    for i in range(rand):
        cars += police_car
    update.message.reply_text(cars)
    bot.sendAnimation(chat_id=update.message.chat.id, animation='CgADBQADVQADOnv4VhiAwbpYxn0eFgQ')




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
    updater.dispatcher.add_handler(CommandHandler('callpolice', send_police))
    # process text triggers
    updater.start_polling()


if __name__ == '__main__':
    main()
