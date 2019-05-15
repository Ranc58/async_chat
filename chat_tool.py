import asyncio
import json
import logging
from datetime import datetime
import socket

from aiofile import AIOFile


async def write_to_file(text, history_log_path):
    async with AIOFile(f'{history_log_path}/history_logs.txt', 'a+') as afp:
        current_datetime = datetime.now().strftime('%d.%m.%y %H:%M')
        text_to_output = f'[{current_datetime}] {text}\n'
        await afp.write(text_to_output)


class ChatTool:

    def __init__(self, host, port, history_log_path, attempts):
        self.host = host
        self.port = port
        self.history_log_path = history_log_path
        self.attempts = attempts

    async def get_connection_tools(self):
        attempts_count = 0
        reader = None
        writer = None
        while not reader:
            try:
                reader, writer = await asyncio.open_connection(self.host, self.port)
                success_connect_msg = 'Соединение установлено'
                logging.debug(success_connect_msg)
                await write_to_file(success_connect_msg, self.history_log_path)
            except (
                    socket.gaierror,
                    ConnectionRefusedError,
                    ConnectionResetError,
            ):
                if attempts_count < self.attempts:
                    error_msg = 'Нет соединения. Повторная попытка.'
                    logging.debug(error_msg)
                    await write_to_file(error_msg, self.history_log_path)
                    attempts_count += 1
                    reader = None
                    continue
                else:
                    error_msg = 'Нет соединения. Повторная попытка через 3 сек.'
                    logging.debug(error_msg)
                    await write_to_file(error_msg, self.history_log_path)
                    reader = None
                    await asyncio.sleep(3)
                    continue
        return reader, writer

    async def read_chat(self):
        reader, _ = await self.get_connection_tools()
        while True:
            data = await reader.readline()
            decoded_data = data.decode().rstrip('\n\r')
            logging.debug(decoded_data)
            await write_to_file(decoded_data, self.history_log_path)

    async def _register(self,  writer, reader, username):
        response = await reader.readline()
        decoded_data = response.decode().rstrip('\n\r')
        logging.debug(decoded_data)
        writer.write(f'\n'.encode())
        response = await reader.readline()
        decoded_data = response.decode().rstrip('\n\r')
        logging.debug(decoded_data)
        if username:
            writer.write(f'{username}\n'.encode())
            logging.debug(f'SENDED: {username}')
        else:
            writer.write('\n'.encode())
        response = await reader.readline()
        decoded_data = response.decode().rstrip('\n\r')
        logging.debug(decoded_data)
        writer.close()
        return json.loads(decoded_data)

    async def _authorise(self, token, writer, reader):
        success = True
        response = await reader.readline()
        decoded_data = response.decode().rstrip('\n\r')
        logging.debug(decoded_data)
        writer.write(f'{token}\n'.encode())
        logging.debug(f'SENDED: {token}')
        response = await reader.readline()
        decoded_data = response.decode().rstrip('\n\r')
        if not json.loads(decoded_data):
            logging.debug('incorrect token')
            success = False
        else:
            logging.debug(decoded_data)
        return success

    async def _submit_message(self, message, writer):
        message = message.replace('\n', '')
        writer.write(f'{message}\n\n'.encode())
        logging.debug(f'SENDED: {message}')

    async def write_to_chat(self, message, token=None, username=None):
        reader, writer = await self.get_connection_tools()

        if not token:
            registred_data = await self._register(writer, reader, username)
            token = registred_data.get('account_hash')
            reader, writer = await self.get_connection_tools()

        authorised = await self._authorise(token, writer, reader)

        if not authorised:
            writer.close()
            return

        await self._submit_message(message, writer)
        writer.close()

