#!/usr/bin/env python3


import asyncio
import json

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler


async def ytdl(*ytdl_args):
    print('yt-dlp', *ytdl_args, '...', end=' ')
    process = await asyncio.subprocess.create_subprocess_exec(
        'yt-dlp',
        *ytdl_args,
        stdout=asyncio.subprocess.PIPE
    )
    info = json.loads(await process.stdout.read())
    await process.wait()
    print('done')
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
    if len(message.command) < 2:
        return

    link = message.command[1]

    print(f'[{link}] getting info')
    info = await ytdl_get_info(link)
    print(f'[{link}] got info')

    format = {'id': None, 'width': 0, 'height': 0}
    for cur_format in info['formats']:
        if cur_format['vcodec'] == 'none' or cur_format['acodec'] == 'none' or cur_format['height'] > 1080:
            continue

        if cur_format['width'] > format['width'] or cur_format['height'] > format['height']:
            format['id'] = cur_format['format_id']
            format['width'] = cur_format['width']
            format['height'] = cur_format['height']

    print(f'[{link}] selected format: {format}')
    if format['id'] is None:
        return

    print(f'[{link}] getting video')
    info = await ytdl_get_video(link, format['id'])
    print(f'[{link}] got video \'{info["filename"]}\'')

    print(f'[{link}] sending video')
    await client.send_document(message.chat.id, info['filename'], force_document=True)
    print(f'[{link}] sent video')


def main():
    client = Client('client')
    client.add_handler(MessageHandler(download, filters.me & filters.command(['d'])))
    client.run()


if __name__ == '__main__':
    main()
