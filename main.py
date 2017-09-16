#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uuid import uuid4

import re
import json

from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging
from os import environ

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def build_kaomoji_index(data):
    ix = {}
    for category in data['categories']:
        category_name = category['name'].lower()
        if category_name not in ix:
            ix[category_name] = []
        ix[category_name].extend(d['emoticon'] for d in category['entries'])
    return ix

data = json.load(open('data/kaomoji.json'))
kaomoji_ix = build_kaomoji_index(data)

def start(bot, update):
    update.message.reply_text('Use @inlennybot inline and choose a kaomoji!')

def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)

def inlinequery(bot, update):
    query = update.inline_query.query.lower()
    results = list()
    if query in tuple(kaomoji_ix.keys()):
        for kaomoji in kaomoji_ix[query][:10]:
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=kaomoji,
                    input_message_content=InputTextMessageContent(kaomoji)
                )
            )
    update.inline_query.answer(results)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def main():
    # Create the Updater and pass it your bot's token.
    try:
        telegram_token = environ['TELEGRAM_TOKEN']
    except KeyError:
        print("There's no TELEGRAM_TOKEN environment variable")
        return
    updater = Updater(telegram_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
