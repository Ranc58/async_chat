import asyncio
import os
import socket
import argparse
import sys
from datetime import datetime

from aiofile import AIOFile


async def write_to_file(text, history_log_path):
    async with AIOFile(f'{history_log_path}/history_logs.txt', 'a+') as afp:
        current_datetime = datetime.now().strftime('%d.%m.%y %H:%M')
        text_to_output = f'[{current_datetime}] {text}\n'
        await afp.write(text_to_output)


async def get_reader(host, port, history_log_path, attempts):
    attempts_count = 0
    reader = None
    while not reader:
        try:
            reader, _ = await asyncio.open_connection(host, port)
            sucess_connect_msg = 'Соединение установлено'
            print(sucess_connect_msg)
            await write_to_file(sucess_connect_msg, history_log_path)
        except (socket.gaierror, ConnectionRefusedError, ConnectionResetError, asyncio.TimeoutError) as e:
            if attempts_count < attempts:
                error_msg = 'Нет соединения. Повторная попытка.'
                print(error_msg)
                await write_to_file(error_msg, history_log_path)
                attempts_count += 1
                reader = None
                continue
            else:
                error_msg = 'Нет соединения. Повторная попытка через 3 сек.'
                print(error_msg)
                await write_to_file(error_msg, history_log_path)
                reader = None
                await asyncio.sleep(3)
                continue
    return reader


async def read_chat(host, port,  history_log_path, attempts):
    reader = await get_reader(host, port, history_log_path, attempts)
    while True:
        data = await reader.readline()
        decoded_data = data.decode().rstrip('\n\r')
        print(f'{decoded_data}')
        await write_to_file(decoded_data, history_log_path)


def create_parser_for_user_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=False,
                        help='chat host',
                        type=str)
    parser.add_argument('--port', required=False,
                        help='chat port',
                        type=int)
    parser.add_argument('--history', required=False,
                        help='history log path',
                        type=str)
    parser.add_argument('--attempts', required=False,
                        help='connect attempts before timeout',
                        type=str)
    namespace = parser.parse_args()
    return namespace


if __name__ == '__main__':
    user_arguments = create_parser_for_user_arguments()
    history_log_path = user_arguments.history or os.getenv('HISTORY_LOG_PATH', f'{os.getcwd()}')
    if not os.path.exists(history_log_path):
        print(f'history log path does not exist {history_log_path}', file=sys.stderr)
        sys.exit(2)
    host = user_arguments.host or os.getenv('HOST', 'minechat.dvmn.org')
    port = user_arguments.port or os.getenv('PORT', 5000)
    attempts = user_arguments.attempts or os.getenv('ATTEMPTS_COUNT', 5000)
    asyncio.run(read_chat(host, port, history_log_path, attempts))
