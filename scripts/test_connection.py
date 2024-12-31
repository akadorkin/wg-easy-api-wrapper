# scripts/test_connection.py

import asyncio
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection():
    url = "http://omhvp.co:1481/api/session"  # Укажите правильный протокол
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Ответ от сервера: {data}")
                else:
                    data = await response.text()
                    logger.error(f"Неверный статус ответа: {response.status}, Тело ответа: {data}")
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка подключения: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
