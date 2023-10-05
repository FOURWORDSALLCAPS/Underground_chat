import asyncio
import argparse
import logging


from environs import Env


logging.basicConfig(level=logging.DEBUG)


async def send_message(host, port, token, message):
    try:
        reader, writer = await asyncio.open_connection(host, port)

        writer.write(token.encode() + b'\n')
        await writer.drain()

        writer.write(message.encode() + b'\n' + b'\n')
        await writer.drain()

        while True:
            response = await reader.read(1000)
            if not response:
                break
            logger.debug(f'{response.decode()!r}')

        writer.close()
        await writer.wait_closed()

    except ConnectionResetError:
        logger.debug("Сетевое подключение разорвано. Повторная попытка соединения через 5 секунд...")
        await asyncio.sleep(5)


def main():
    env = Env()
    env.read_env()
    chat_host = env('CHAT_HOST')
    chat_send_port = env('CHAT_SEND_PORT')
    chat_token = env('CHAT_TOKEN')
    parser = argparse.ArgumentParser(description='Отправка сообщений чату в реальном времени')
    parser.add_argument('--host', default=chat_host, help='Хост сервера')
    parser.add_argument('--port', default=chat_send_port, help='Порт сервера')
    parser.add_argument('--token', default=chat_token, help='Токен для авторизации')
    args = parser.parse_args()
    asyncio.run(send_message(args.host, args.port, args.token, 'Я снова тестирую чатик. Это третье сообщение.'))


if __name__ == '__main__':
    logger = logging.getLogger('sender')
    main()
