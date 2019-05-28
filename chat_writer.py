import asyncio
import json
import logging
import os
import argparse
import socket
import sys

from aiofile import AIOFile

from chat_tool import get_open_connection_tools, read_message_from_chat, write_message_to_chat


async def authorise(reader, writer, token):
    success = True
    await read_message_from_chat(reader)
    await write_message_to_chat(writer, f'{token}\n')
    logging.debug(f'SENDED: {token}')
    decoded_data = await read_message_from_chat(reader)
    if not json.loads(decoded_data):
        logging.debug('incorrect token')
        success = False
    else:
        logging.debug(decoded_data)
    return success


async def register(reader, writer, username):
    await read_message_from_chat(reader)
    await write_message_to_chat(writer)
    await read_message_from_chat(reader)
    if username:
        await write_message_to_chat(writer, f'{username}\n')
        logging.debug(f'SENDED: {username}')
    else:
        await write_message_to_chat(writer)
    decoded_data = await read_message_from_chat(reader)
    return json.loads(decoded_data)


async def submit_message(writer, message):
    await write_message_to_chat(writer, f'{message}\n\n')
    logging.debug(f'SENDED: {message}')


async def write_to_chat(host, port, attempts, history_log_path, message, token=None, username=None):
    async with AIOFile(f'{history_log_path}/history_logs.txt', 'a+') as log_file:
        async with get_open_connection_tools(host, port, attempts, log_file) as (reader, writer):
            try:
                if token:
                    authorised = await authorise(reader, writer, token)
                    if not authorised:
                        return
                else:
                    await register(reader, writer, username)
                await submit_message(writer, message)
            except (
                    socket.gaierror,
                    ConnectionRefusedError,
                    ConnectionResetError,
                    ConnectionError,
            ) as error:
                logging.error(str(error))
                sys.exit()


def create_parser_for_user_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=False,
                        help='chat host',
                        type=str)
    parser.add_argument('--port', required=False,
                        help='chat port for message sending',
                        type=int)
    parser.add_argument('--history', required=False,
                        help='history log dir path',
                        type=str)
    parser.add_argument('--attempts', required=False,
                        help='connect attempts before timeout',
                        type=int)
    parser.add_argument('--token', required=False,
                        help='user token',
                        type=str)
    parser.add_argument('--username', required=False,
                        help='username',
                        type=str)
    parser.add_argument('--message', required=False,
                        help='message for sent',
                        type=str)
    namespace = parser.parse_args()
    return namespace


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    user_arguments = create_parser_for_user_arguments()
    history_log_path = user_arguments.history or os.getenv('HISTORY_LOG_DIR_PATH', f'{os.getcwd()}')
    if not os.path.exists(history_log_path):
        print(f'history log path does not exist {history_log_path}', file=sys.stderr)
        sys.exit(2)
    host = user_arguments.host or os.getenv('HOST', 'minechat.dvmn.org')
    port = user_arguments.port or os.getenv('WRITE_PORT', 5050)
    attempts = user_arguments.attempts or os.getenv('ATTEMPTS_COUNT', 3)
    token = user_arguments.token or os.getenv('TOKEN')
    username = user_arguments.username or os.getenv('USERNAME')
    message = user_arguments.message or os.getenv('MESSAGE')
    asyncio.run(write_to_chat(
        host, port, attempts, history_log_path, message=message, token=token, username=username
    ))
