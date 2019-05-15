import asyncio
import os
import argparse
import sys
import logging

from chat_tool import ChatTool


def create_parser_for_user_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=False,
                        help='chat host',
                        type=str)
    parser.add_argument('--port', required=False,
                        help='chat port for reading messages',
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
    logging.basicConfig(level=logging.DEBUG)
    user_arguments = create_parser_for_user_arguments()
    history_log_path = user_arguments.history or os.getenv('HISTORY_LOG_PATH', f'{os.getcwd()}')
    if not os.path.exists(history_log_path):
        logging.error(f'history log path does not exist {history_log_path}')
        sys.exit(2)
    host = user_arguments.host or os.getenv('HOST', 'minechat.dvmn.org')
    port = user_arguments.port or os.getenv('READ_PORT', 5000)
    attempts = int(user_arguments.attempts or os.getenv('ATTEMPTS_COUNT', 3))
    chat_tool = ChatTool(host, port, history_log_path, attempts)
    asyncio.run(chat_tool.read_chat())
