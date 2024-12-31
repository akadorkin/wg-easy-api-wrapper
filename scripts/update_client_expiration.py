# scripts/update_client_expiration.py

import asyncio
import logging
from wg_easy_api_wrapper import Server
from wg_easy_api_wrapper.errors import (
    AuthenticationError,
    AlreadyLoggedInError,
    ClientNotFoundError,
    InvalidDateFormatError,
)
import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    server_url = "http://omhvp.co:1481"  # Убедитесь, что протокол указан правильно
    password = "rKGkoMJCskoioJXWzrs4KXmr6d9J82Q7vTTNusdm"
    client_uid = "your_client_uid_here"  # Замените на UID вашего клиента
    new_expired_date = "2025-01-02T00:00:00Z"  # Новая дата истечения в формате ISO 8601

    # Валидация формата и будущего времени даты истечения
    try:
        expired_datetime = datetime.datetime.strptime(new_expired_date, "%Y-%m-%dT%H:%M:%SZ")
        if expired_datetime <= datetime.datetime.utcnow():
            raise ValueError("Дата истечения должна быть в будущем.")
    except ValueError as ve:
        logger.error(f"Неверная дата истечения: {ve}")
        return

    try:
        async with Server(server_url, password) as server:
            await server.update_client_expired_date(
                uid=client_uid,
                expired_date=new_expired_date
            )
            logger.info("Дата истечения клиента успешно обновлена.")
    except ClientNotFoundError as e:
        logger.error(f"Клиент не найден: {e}")
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
