import asyncio
import aiofiles

from datetime import datetime
from environs import Env


async def stream_chat(host, port):
    try:
        async with aiofiles.open("chat_history.txt", mode="a", encoding="utf-8") as file:
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
    chat_port = env('CHAT_PORT')
    asyncio.run(stream_chat(chat_host, chat_port))


if __name__ == '__main__':
    main()
