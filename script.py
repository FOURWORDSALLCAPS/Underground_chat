import asyncio

from environs import Env


async def stream_chat(host, port):
    reader, writer = await asyncio.open_connection(
        host, port
    )

    while True:
        correspondence = await reader.read(500 * 1024)
        print(correspondence.decode(), end='')


def main():
    env = Env()
    env.read_env()
    chat_host = env('CHAT_HOST')
    chat_port = env('CHAT_PORT')
    asyncio.run(stream_chat(chat_host, chat_port))


if __name__ == '__main__':
    main()
