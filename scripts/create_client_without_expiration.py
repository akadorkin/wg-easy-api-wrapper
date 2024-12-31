# scripts/create_client_without_expiration.py

import asyncio
import logging
from wg_easy_api_wrapper import Server
from wg_easy_api_wrapper.errors import (
    AuthenticationError,
    AlreadyLoggedInError,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    server_url = "http://omhvp.co:1481"  # Убедитесь, что протокол указан правильно
    password = "rKGkoMJCskoioJXWzrs4KXmr6d9J82Q7vTTNusdm"
    client_name = "1234cli11e000nt_name"

    try:
        async with Server(server_url, password) as server:
            await server.create_client(
                name=client_name
                # expired_date не указывается
            )
            logger.info("Клиент успешно создан без даты истечения.")
    except AuthenticationError as e:
        logger.error(f"Ошибка аутентификации: {e}")
    except AlreadyLoggedInError as e:
        logger.error(f"Пользователь уже аутентифицирован: {e}")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
