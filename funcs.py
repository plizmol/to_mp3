import logging
import os
import time
from contextlib import suppress

import ffmpeg
import youtube_dl

POISON_PILL = '__its_time_to_stop'
SIZE_THRESHOLD = 20 * 60  # minutes
log = logging.getLogger('to_mp3')


def setug_log():
    log = logging.getLogger('to_mp3')
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler())
    return log


def is_url(text):
    return text.startswith('http')


def download_mp3(url, path):
    ydl_opts = {
        'outtmpl': f'{path}/%(title)s.%(ext)s',
        'prefer_ffmpeg': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '5',
            'nopostoverwrites': False
        }]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    open(f'{path}/{POISON_PILL}', 'w').close()


def insert_chunk_num(in_file, i):
   file_name, _, extension = in_file.partition('.')
   return f'{file_name}_chunk_{i}.{extension}'


def prepare_downloaded(in_file, out_path):
    """Split audio from in_path in chunks if their duration is above threshold and save those chunks to out_path"""
    filename = in_file.split('/')[-1]
    duration = ffmpeg.probe(in_file)['format']['duration']

    if float(duration) < SIZE_THRESHOLD:
        os.rename(in_file, f'{out_path}/{filename}')
        return

    log.info('Splitting audio')
    name, _, extension = filename.partition('.')
    ffmpeg.input(in_file).output(
        f'{out_path}/{name}_%d.{extension}', f='segment', segment_time=SIZE_THRESHOLD, c='copy'
    ).run()
    with suppress(FileNotFoundError):
        os.remove(in_file)


def mp3_files(in_path):
    """Yield mp3 files from in_path when they stop changing their modified date"""
    while True:
        for in_file in os.listdir(in_path):
            file_path = f'{in_path}/{in_file}'
            if in_file == POISON_PILL:
                log.info('Got poison pill, shutting down pipeline')
                os.remove(file_path)
                break

            if in_file.endswith('.mp3'):
                print('Waiting for mp3 finalisation .')
                while True:
                    # wait until file downloaded completely
                    previous = os.stat(file_path).st_mtime
                    time.sleep(2)
                    current = os.stat(file_path).st_mtime
                    if current == previous:
                        break
                    print('.', end='')
                yield file_path

        time.sleep(3)


def send_downloaded(out_path, bot, chat_id):
    for out_file in sorted(os.listdir(out_path)):
        out_file_path = f'{out_path}/{out_file}'
        with open(out_file_path, 'rb') as f:
            bot.send_audio(chat_id, f)
        with suppress(FileNotFoundError):
            os.remove(out_file_path)


def run_pipeline(in_path, out_path, bot, chat_id):
    for in_file in mp3_files(in_path):
        prepare_downloaded(in_file, out_path)
        send_downloaded(out_path, bot, chat_id)
