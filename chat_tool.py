import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
import socket

from aiofile import AIOFile


class ChatTool:

    def __init__(self, host, port, history_log_path, attempts):
        self.host = host
        self.port = port
        self.history_log_path = history_log_path
        self.attempts = attempts
        self.reader = None
        self.writer = None
        self.log_file = None

    async def write_to_file(self, text):
        current_datetime = datetime.now().strftime('%d.%m.%y %H:%M')
        text_to_output = f'[{current_datetime}] {text}\n'
        await self.log_file.write(text_to_output)

    async def read_message_from_chat(self):
        try:
            response = await self.reader.readline()

        except (
                socket.gaierror,
                ConnectionRefusedError,
                ConnectionResetError,
                ConnectionError,
        ) as error:
            raise error
        else:
            decoded_data = response.decode().rstrip('\n\r')
            logging.debug(decoded_data)
            return decoded_data

    async def write_message_to_chat(self, message=None):

        if not message:
            message = f'\n'
        try:
            self.writer.write(message.encode())
        except (
                socket.gaierror,
                ConnectionRefusedError,
                ConnectionResetError,
                ConnectionError,
        ) as error:
            raise error

    @asynccontextmanager
    async def reader_writer_tools(self):
        try:
            self.log_file = await AIOFile(f'{self.history_log_path}/history_logs.txt', 'a+')
            await self.log_file.open()
            await self.get_connection_tools()
            yield
        finally:
            await self.log_file.close()
            if self.writer:
                self.writer.close()

    async def get_connection_tools(self):
        attempts_count = 0

        while not self.reader:
            try:
                self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
                success_connect_msg = 'Соединение установлено'
                logging.debug(success_connect_msg)
                await self.write_to_file(success_connect_msg)
            except (
                    socket.gaierror,
                    ConnectionRefusedError,
                    ConnectionResetError,
                    ConnectionError,
            ):
                if attempts_count < int(self.attempts):
                    error_msg = 'Нет соединения. Повторная попытка.'
                    logging.debug(error_msg)
                    await self.write_to_file(error_msg)
                    attempts_count += 1
                    continue
                else:
                    error_msg = 'Нет соединения. Повторная попытка через 3 сек.'
                    logging.debug(error_msg)
                    await self.write_to_file(error_msg)
                    await asyncio.sleep(3)
                    continue

    async def read_chat(self):
        async with self.reader_writer_tools():
            while True:
                try:
                    data = await self.reader.readline()
                except (
                        socket.gaierror,
                        ConnectionRefusedError,
                        ConnectionResetError,
                        ConnectionError,
                ):
                    await self.get_connection_tools()
                    data = await self.reader.readline()
                decoded_data = data.decode().rstrip('\n\r')
                logging.debug(decoded_data)
                await self.write_to_file(decoded_data)

    async def _register(self, username):
        await self.read_message_from_chat()
        await self.write_message_to_chat()
        await self.read_message_from_chat()
        if username:
            await self.write_message_to_chat(f'{username}\n')
            logging.debug(f'SENDED: {username}')
        else:
            await self.write_message_to_chat()
        decoded_data = await self.read_message_from_chat()
        return json.loads(decoded_data)

    async def _authorise(self, token):
        success = True
        await self.read_message_from_chat()
        await self.write_message_to_chat(f'{token}\n')
        logging.debug(f'SENDED: {token}')
        decoded_data = await self.read_message_from_chat()
        if not json.loads(decoded_data):
            logging.debug('incorrect token')
            success = False
        else:
            logging.debug(decoded_data)
        return success

    async def _submit_message(self, message):

        await self.write_message_to_chat(f'{message}\n\n')
        logging.debug(f'SENDED: {message}')

    async def write_to_chat(self, message, token=None, username=None):

        async with self.reader_writer_tools():
            try:
                if not token:
                    registered_data = await self._register(username)
                    token = registered_data.get('account_hash')
                    # for reconnect by token
                    self.reader = None
                    self.writer.close()
                    await self.get_connection_tools()
                authorised = await self._authorise(token)
                if not authorised:
                    return
                await self._submit_message(message)
            except (
                    socket.gaierror,
                    ConnectionRefusedError,
                    ConnectionResetError,
                    ConnectionError,
            ) as error:
                logging.error(str(error))
                sys.exit()
