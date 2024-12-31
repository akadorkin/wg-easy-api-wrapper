# scripts/list_clients.py

import asyncio
import logging
from wg_easy_api_wrapper.server import Server
from wg_easy_api_wrapper.errors import (
    AuthenticationError,
    AlreadyLoggedInError,
)
from wg_easy_api_wrapper.client import Client
from dotenv import load_dotenv
import os

# Загрузка переменных из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    server_url = os.getenv("WG_EASY_SERVER_URL")
    password = os.getenv("WG_EASY_PASSWORD")

    if not server_url or not password:
        logger.error("Переменные окружения WG_EASY_SERVER_URL и WG_EASY_PASSWORD не установлены.")
        return

    try:
        async with Server(server_url, password) as server:
            clients = await server.get_clients()
            if not clients:
                logger.info("Клиенты не найдены.")
                return
            for client in clients:
                expired_at = client.expired_at.strftime("%Y-%m-%dT%H:%M:%SZ") if client.expired_at else "No expiration"
                logger.info(f"UID: {client.uid}, Name: {client.name}, Expired At: {expired_at}")
    except AuthenticationError as e:
        logger.error(f"Ошибка аутентификации: {e}")
    except AlreadyLoggedInError as e:
        logger.error(f"Пользователь уже аутентифицирован: {e}")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())