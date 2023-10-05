import asyncio
import aiofiles
import argparse

from datetime import datetime
from environs import Env


async def stream_chat(host, port, file_path):
    try:
        async with aiofiles.open(file_path, mode="a", encoding="utf-8") as file:
            reader, writer = await asyncio.open_connection(host, port)

            while True:
                correspondence = await reader.read(500 * 1024)
                decoded_correspondence = correspondence.decode()

                current_datetime = datetime.now().strftime("[%d.%m.%y %H:%M]")

                lines = decoded_correspondence.split('\n')
                formatted_lines = [f"{current_datetime} {line}" if line.strip() else line for line in lines]

                formatted_text = '\n'.join(formatted_lines)
                await file.write(formatted_text)
                print(formatted_text, end='')
    except ConnectionResetError:
        print("Сетевое подключение разорвано. Повторная попытка соединения через 5 секунд...")
        await asyncio.sleep(5)


def main():
    env = Env()
    env.read_env()
    chat_host = env('CHAT_HOST')
    chat_read_port = env('CHAT_READ_PORT')
    chat_history_path = env('CHAT_HISTORY_PATH')
    parser = argparse.ArgumentParser(description='Запись и вывод переписки из чата в реальном времени')
    parser.add_argument('--host', default=chat_host, help='Хост сервера')
    parser.add_argument('--port', default=chat_read_port, help='Порт сервера')
    parser.add_argument('--history', default=chat_history_path, help='Путь к файлу с историей переписки')
    args = parser.parse_args()
    asyncio.run(stream_chat(args.host, args.port, args.history))


if __name__ == '__main__':
    main()
