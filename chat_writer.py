import asyncio
import logging
import os
import argparse
import sys

from chat_tool import ChatTool


def create_parser_for_user_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=False,
                        help='chat host',
                        type=str)
    parser.add_argument('--port', required=False,
                        help='chat port for message sending',
                        type=int)
    parser.add_argument('--history', required=False,
                        help='history log path',
                        type=str)
    parser.add_argument('--attempts', required=False,
                        help='connect attempts before timeout',
                        type=str)
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
    history_log_path = user_arguments.history or os.getenv('HISTORY_LOG_PATH', f'{os.getcwd()}')
    if not os.path.exists(history_log_path):
        print(f'history log path does not exist {history_log_path}', file=sys.stderr)
        sys.exit(2)
    host = user_arguments.host or os.getenv('HOST', 'minechat.dvmn.org')
    port = user_arguments.port or os.getenv('WRITE_PORT', 5050)
    attempts = user_arguments.attempts or os.getenv('ATTEMPTS_COUNT', 3)
    token = user_arguments.token or os.getenv('TOKEN')
    username = user_arguments.username or os.getenv('USERNAME')
    message = user_arguments.message or os.getenv('MESSAGE')
    chat_tool = ChatTool(host, port, history_log_path, attempts)
    asyncio.run(chat_tool.write_to_chat(token=token, username=username, message=message))
