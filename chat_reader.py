import asyncio
import os
import argparse
import socket
import sys
import logging

from aiofile import AIOFile

from chat_tool import get_reader_writer_tools, read_message_from_chat, write_to_file


async def read_chat(host, port, log_file, attempts):
    async with get_reader_writer_tools(host, port, attempts, log_file) as (reader, writer):
        while True:
            try:
                decoded_data = await read_message_from_chat(reader)
            except (
                    socket.gaierror,
                    ConnectionRefusedError,
                    ConnectionResetError,
                    ConnectionError,
            ) as error:
                raise error
            await write_to_file(decoded_data, log_file)


async def stream_chat(host, port, history_log_path, attempts):
    async with AIOFile(f'{history_log_path}/history_logs.txt', 'a+') as log_file:
        while True:
            try:
                await read_chat(host, port, log_file, attempts)
            except (
                    socket.gaierror,
                    ConnectionRefusedError,
                    ConnectionResetError,
                    ConnectionError,
            ):
                continue


def create_parser_for_user_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=False,
                        help='chat host',
                        type=str)
    parser.add_argument('--port', required=False,
                        help='chat port for reading messages',
                        type=int)
    parser.add_argument('--history', required=False,
                        help='history log dir path',
                        type=str)
    parser.add_argument('--attempts', required=False,
                        help='connect attempts before timeout',
                        type=str)
    namespace = parser.parse_args()
    return namespace


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    user_arguments = create_parser_for_user_arguments()
    history_log_path = user_arguments.history or os.getenv('HISTORY_LOG_DIR_PATH', f'{os.getcwd()}')
    if not os.path.exists(history_log_path):
        logging.error(f'history log path does not exist {history_log_path}')
        sys.exit(2)
    host = user_arguments.host or os.getenv('HOST', 'minechat.dvmn.org')
    port = user_arguments.port or os.getenv('READ_PORT', 5000)
    attempts = int(user_arguments.attempts or os.getenv('ATTEMPTS_COUNT', 3))
    asyncio.run(stream_chat(host, port, history_log_path, attempts))
