import asyncio
import argparse
import logging
import json
import aiofiles

from environs import Env

logging.basicConfig(level=logging.DEBUG)


async def registration_chat(host, port, nickname, file_path):
    reader = None
    writer = None
    try:
        reader, writer = await asyncio.open_connection(host, port)

        writer.write(b'\n')
        await writer.drain()

        writer.write(nickname.encode() + b'\n')
        await writer.drain()

        server_response = {}
        while True:
            response_chunk = await reader.readuntil(b'\n')
            response_str = response_chunk.decode().strip()

            if "nickname" in response_str and "account_hash" in response_str:
                if not server_response:
                    server_response = json.loads(response_str)
            if "Welcome to chat!" in response_str:
                break
        async with aiofiles.open(file_path, 'w', encoding="utf-8") as file:
            await file.write(json.dumps(server_response, indent=4))

    except ConnectionResetError:
        logger.debug("Сетевое подключение разорвано. Повторная попытка соединения через 5 секунд...")
        await asyncio.sleep(5)
    except Exception as e:
        logger.error(f'Произошла ошибка: {str(e)}')
    finally:
        if not reader.at_eof():
            writer.close()
            await writer.wait_closed()


def main():
    env = Env()
    env.read_env()
    chat_host = env('CHAT_HOST')
    chat_send_port = env('CHAT_SEND_PORT')
    account_hash = env('ACCOUNT_HASH_PATH')
    parser = argparse.ArgumentParser(description='Регистрация в чате')
    parser.add_argument('--host', default=chat_host, help='Хост сервера')
    parser.add_argument('--port', default=chat_send_port, help='Порт сервера')
    parser.add_argument('--name', help='Желаемое имя для регистрации')
    parser.add_argument('--hash', default=account_hash, help='Путь к файлу с регистрационными данными')
    args = parser.parse_args()
    asyncio.run(registration_chat(args.host, args.port, args.name, args.hash))


if __name__ == '__main__':
    logger = logging.getLogger('sender')
    main()
