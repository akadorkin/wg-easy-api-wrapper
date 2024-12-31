# scripts/create_client_with_expiration.py

import asyncio
import logging
from wg_easy_api_wrapper import Server
from wg_easy_api_wrapper.errors import (
    AuthenticationError,
    AlreadyLoggedInError,
    InvalidDateFormatError,
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    server_url = "http://omhvp.co:1481"  # Убедитесь, что протокол указан правильно
    password = "rKGkoMJCskoioJXWzrs4KXmr6d9J82Q7vTTNusdm"
    client_name = "cli_expiration_test"
    expired_date = "2025-01-02T00:00:00Z"  # Дата истечения в формате ISO 8601

    try:
        async with Server(server_url, password) as server:
            await server.create_client(
                name=client_name,
                expired_date=expired_date  # Указание даты истечения
            )
            logger.info("Клиент успешно создан с датой истечения.")
    except InvalidDateFormatError as e:
        logger.error(f"Неверный формат даты: {e}")
    except AuthenticationError as e:
        logger.error(f"Ошибка аутентификации: {e}")
    except AlreadyLoggedInError as e:
        logger.error(f"Пользователь уже аутентифицирован: {e}")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
