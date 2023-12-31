import asyncio
import argparse
import logging
import aiofiles
import json

from environs import Env

logging.basicConfig(level=logging.DEBUG)


async def register(host, port, nickname, file_path):
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

        return server_response.get("account_hash", "")

    except ConnectionResetError:
        logger.debug("Сетевое подключение разорвано. Повторная попытка соединения через 5 секунд...")
        await asyncio.sleep(5)
    except Exception as e:
        logger.error(f'Произошла ошибка: {str(e)}')
    finally:
        if not reader.at_eof():
            writer.close()
            await writer.wait_closed()


async def authorise(reader, writer, token):
    writer.write(token.encode() + b'\n')
    await writer.drain()

    response_chunk = await reader.readuntil(b'\n')
    response_str = response_chunk.decode().strip()
    logger.debug(f'{response_str!r}')

    if response_str == 'null':
        logger.error("Неизвестный токен. Проверьте его или зарегистрируйте заново.")
    return response_str


async def submit_message(reader, writer, message):
    writer.write(message.encode() + b'\n' + b'\n')
    await writer.drain()

    while True:
        response_chunk = await reader.readuntil(b'\n')
        if not response_chunk:
            break

        response_str = response_chunk.decode().strip()
        logger.debug(f'{response_str!r}')

        if response_str == 'null':
            logger.error("Неизвестный токен. Проверьте его или зарегистрируйте заново.")
            break


def main():
    env = Env()
    env.read_env()
    chat_host = env('CHAT_HOST')
    chat_send_port = env('CHAT_SEND_PORT')
    account_hash_path = env('ACCOUNT_HASH_PATH')
    parser = argparse.ArgumentParser(description='Регистрация в чате')
    parser.add_argument('--host', default=chat_host, help='Хост сервера')
    parser.add_argument('--port', default=chat_send_port, help='Порт сервера')
    parser.add_argument('--name', help='Желаемое имя для регистрации')
    parser.add_argument('--token', help='Токен для авторизации')
    parser.add_argument('--message', help='Сообщение для отправки в чат')
    parser.add_argument('--hash', default=account_hash_path, help='Путь к файлу с регистрационными данными')
    args = parser.parse_args()

    async def main_connection():
        reader = None
        writer = None
        try:
            if args.name:
                token = await register(args.host, args.port, args.name, args.hash)
            elif args.token:
                token = args.token
            else:
                try:
                    async with aiofiles.open(args.hash, 'r', encoding="utf-8") as file:
                        token_data = await file.read()
                        token_json = json.loads(token_data)
                        token = token_json.get("account_hash", "")
                except (FileNotFoundError, json.JSONDecodeError):
                    token = ""

            if token:
                reader, writer = await asyncio.open_connection(args.host, args.port)
                await authorise(reader, writer, token)
                await submit_message(reader, writer, args.message)
        finally:
            if not reader.at_eof():
                writer.close()
                await writer.wait_closed()
    asyncio.run(main_connection())


if __name__ == '__main__':
    logger = logging.getLogger('sender')
    main()
