from contextlib import asynccontextmanager
from datetime import datetime
import asyncio
import logging
import socket


async def get_connection_tools(host, port, attempts, log_file):
    attempts_count = 0
    reader = None
    writer = None
    while not reader:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            success_connect_msg = 'Соединение установлено'
            logging.debug(success_connect_msg)
            await write_to_file(success_connect_msg, log_file)
        except (
                socket.gaierror,
                ConnectionRefusedError,
                ConnectionResetError,
                ConnectionError,
        ):
            if attempts_count < int(attempts):
                error_msg = 'Нет соединения. Повторная попытка.'
                logging.debug(error_msg)
                await write_to_file(error_msg, log_file)
                attempts_count += 1
                continue
            else:
                error_msg = 'Нет соединения. Повторная попытка через 3 сек.'
                logging.debug(error_msg)
                await write_to_file(error_msg, log_file)
                await asyncio.sleep(3)
                continue
    return reader, writer


@asynccontextmanager
async def get_reader_writer_tools(host, port, attempts, log_file):
    writer = None
    try:
        reader, writer = await get_connection_tools(host, port, attempts, log_file)
        yield reader, writer
    finally:
        if writer:
            writer.close()


async def write_to_file(text, log_file):
    current_datetime = datetime.now().strftime('%d.%m.%y %H:%M')
    text_to_output = f'[{current_datetime}] {text}\n'
    await log_file.write(text_to_output)


async def read_message_from_chat(reader):
    try:
        response = await reader.readline()
    except (
            socket.gaierror,
            ConnectionRefusedError,
            ConnectionResetError,
            ConnectionError,
    ):
        raise
    else:
        decoded_data = response.decode().rstrip('\n\r')
        logging.debug(decoded_data)
        return decoded_data


async def write_message_to_chat(writer, message=None):
    if not message:
        message = f'\n'
    try:
        writer.write(message.encode())
    except (
            socket.gaierror,
            ConnectionRefusedError,
            ConnectionResetError,
            ConnectionError,
    ):
        raise
