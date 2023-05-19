#!/usr/bin/env python3


import asyncio
import json
import logging

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler


async def ytdl(*ytdl_args):
    logging.info('yt-dlp ' + ' '.join(ytdl_args))
    process = await asyncio.subprocess.create_subprocess_exec(
        'yt-dlp',
        *ytdl_args,
        stdout=asyncio.subprocess.PIPE
    )
    info = json.loads(await process.stdout.read())
    await process.wait()
    return info


async def ytdl_get_info(link):
    return await ytdl('--dump-json', link)


async def ytdl_get_video(link, format):
    return await ytdl(
        '--dump-json',
        '--no-simulate',
        '--output', f'files/%(title)s %(id)s.%(ext)s',
        '--format', f'{format}',
        link
    )


async def download(client, message):
    logging.info('%s %s', message.id, message.text)
    if len(message.command) < 2:
        return

    link = message.command[1]

    logging.info('[%s] getting info', link)
    info = await ytdl_get_info(link)
    logging.info('[%s] got info', link)

    format = {'id': None, 'width': 0, 'height': 0}
    for cur_format in info['formats']:
        if cur_format['vcodec'] == 'none' or cur_format['acodec'] == 'none' or cur_format['height'] > 1080:
            continue

        if cur_format['width'] > format['width'] or cur_format['height'] > format['height']:
            format['id'] = cur_format['format_id']
            format['width'] = cur_format['width']
            format['height'] = cur_format['height']

    logging.info('[%s] selected format: %s', link, format)
    if format['id'] is None:
        return

    logging.info('[%s] getting video', link)
    info = await ytdl_get_video(link, format['id'])
    logging.info('[%s] got video \'%s\'', link, info['filename'])

    logging.info('[%s] sending video', link)
    await client.send_document(message.chat.id, info['filename'], force_document=True)
    logging.info('[%s] sent video', link)


def main():
    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname).1s %(message)s',
        level=logging.INFO
    )
    client = Client('client')
    client.add_handler(MessageHandler(download, filters.me & filters.command(['d'])))
    client.run()


if __name__ == '__main__':
    main()
