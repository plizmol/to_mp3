import os
from multiprocessing.dummy import Pool as ThreadPool

import telebot

from funcs import setug_log, is_url, download_mp3, run_pipeline

DOWNLOADS = 'downloads'
PREPARED = 'prepared'
TG_TOKEN = os.getenv('TG_TOKEN')
THREAD_NUM = 2


if __name__ == '__main__':
    log = setug_log()
    log.info('Bot started')
    bot = telebot.TeleBot(TG_TOKEN)
    pool = ThreadPool(THREAD_NUM)

    @bot.message_handler(func=lambda m: m.content_type == 'text')
    def handle_text(message):
        if not is_url(message.text):
            return
        chat_id = message.chat.id

        pool.apply_async(download_mp3, (message.text, DOWNLOADS))
        run_pipeline(DOWNLOADS, PREPARED, bot, chat_id)

    # noinspection PyBroadException
    try:
        bot.polling(none_stop=False, interval=3, timeout=20)
    except Exception as e:
        log.exception('Bot failed')
        pool.close()
        pool.join()
