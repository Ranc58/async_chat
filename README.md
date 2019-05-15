# Async chat
Async char reader/writer
# How to install
Python version required: 3.7+
1. Recomended use venv or virtualenv for better isolation.\
   Venv setup example: \
   `python3 -m venv myenv`\
   `source myenv/bin/activate`
2. Install requirements: \
   `pip3 install -r requirements.txt` (alternatively try add `sudo` before command)
3. `cp env/.env env/.env_file`. If it need setup env file(or use default settings):
        - `HOST` - chat host. \
        - `READ_PORT` - port for read messages from chat. \
        - `WRITE_PORT` - port for write messages to chat. \
        - `ATTEMPTS_COUNT` - connection attempts before 3 sec timeout.  \
        - `HISTORY_LOG_PATH` - path to folder where will be created `history_log.txt` file with chat messages history. \
        Additional vars (for message writing): \
        - `TOKEN` - unique token (issued after registration) for chat. \
        - `USERNAME` - desirable username for chat registration. \
        - `MESSAGE` - message for sending. \

# How to launch
Instead environ vars you can use arguments. For more info use `python3 chat_reader.py --help` for reading script and `python3 chat_writer.py --help` for sending script.
1) For reading chat run `python3 chat_reader.py`
2) For sending message run `python3 chat_writer.py`

# Project Goals
The code is written for educational purposes. Training course for web-developers - [DVMN.org](https://dvmn.org)
