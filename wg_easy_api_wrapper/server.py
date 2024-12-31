import aiohttp
import logging
from .client import Client
from .errors import AlreadyLoggedInError

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Server:
    def __init__(self, url: str, password: str, session: aiohttp.ClientSession = None):
        """
        :param url: Адрес WG-Easy, например http://wg.example.com:51821
        :param password: Пароль для WG-Easy
        :param session: Опциональная aiohttp.ClientSession
        """
        self.url = url.rstrip("/")
        self._password = password
        self._session_provided = session is not None
        self._session = session if session else aiohttp.ClientSession()

    def get_session_request(self):
        """Возвращает контекстный менеджер для запроса информации о сессии."""
        return self._session.get(self.url_builder("/api/session"))

    async def is_logged_in(self) -> bool:
        """Проверяем, залогинен ли текущий сеанс."""
        async with self.get_session_request() as response:
            json_response = await response.json()
            return json_response.get("authenticated", False)

    def url_builder(self, path: str) -> str:
        """Функция для создания полного URL."""
        return f"{self.url}{path}"

    async def __aenter__(self):
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        try:
            if await self.is_logged_in():
                await self.logout()
        except Exception as e:
            # Логируем ошибку выхода, но не поднимаем исключение
            logger.error(f"Ошибка при выходе: {e}")
        finally:
            # Закрываем сессию, только если мы её создавали
            if not self._session_provided:
                await self._session.close()

        if exc_type:
            raise exc_value

    async def login(self):
        """Выполняет вход в WG-Easy."""
        if await self.is_logged_in():
            raise AlreadyLoggedInError("Вы уже вошли в систему.")

        async with self._session.post(
            self.url_builder("/api/session"),
            json={"password": self._password}
        ) as response:
            if response.status != 200:
                try:
                    json_response = await response.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при входе.")
                except aiohttp.ContentTypeError:
                    error_message = await response.text()
                raise Exception(f"Ошибка входа: {error_message}")

            # Обновляем куки из ответа
            self._session.cookie_jar.update_cookies(response.cookies)

            # Потребляем тело ответа, чтобы избежать предупреждений
            try:
                await response.text()
            except Exception as e:
                logger.warning(f"Не удалось полностью потребить тело ответа при входе: {e}")

    async def logout(self):
        """Выполняет выход из WG-Easy."""
        if not await self.is_logged_in():
            raise AlreadyLoggedInError("Вы не вошли в систему.")

        async with self._session.delete(self.url_builder("/api/session")) as response:
            if response.status not in [204, 200]:
                try:
                    json_response = await response.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при выходе.")
                except aiohttp.ContentTypeError:
                    error_message = await response.text()
                logger.debug(f"Ответ сервера при logout: статус={response.status}, сообщение={error_message}")
                raise Exception(f"Ошибка выхода: {error_message}")
            else:
                logger.debug("Успешно завершена сессия.")
                # Потребляем тело ответа, чтобы избежать предупреждений
                try:
                    await response.text()
                except Exception as e:
                    logger.warning(f"Не удалось полностью потребить тело ответа при выходе: {e}")

    async def get_clients(self):
        """Возвращает список всех WireGuard-клиентов как объекты Client."""
        async with self._session.get(self.url_builder("/api/wireguard/client")) as response:
            if response.status != 200:
                try:
                    json_response = await response.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при получении клиентов.")
                except aiohttp.ContentTypeError:
                    error_message = await response.text()
                raise Exception(f"Ошибка при получении клиентов: {error_message}")
            data = await response.json()
            return [Client.from_json(item, self._session, self) for item in data]

    async def get_client(self, uid: str):
        """Возвращает объект Client по его UID, или None, если не найден."""
        clients = await self.get_clients()
        for client in clients:
            if client.uid == uid:
                return client
        return None

    async def get_client_by_name(self, name: str):
        """Возвращает объект Client по его имени, или None, если не найден."""
        clients = await self.get_clients()
        for client in clients:
            if client.name == name:
                return client
        return None

    async def remove_client(self, uid: str):
        """Удаляет клиента по UID."""
        async with self._session.delete(self.url_builder(f"/api/wireguard/client/{uid}")) as response:
            if response.status != 204:
                try:
                    json_response = await response.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при удалении клиента.")
                except aiohttp.ContentTypeError:
                    error_message = await response.text()
                raise Exception(f"Ошибка при удалении клиента: {error_message}")

    async def create_client(self, name: str, expire_date: str = None):
        """
        Создаёт нового клиента. Можно указать дату истечения (expire_date).
        Формат обычно YYYY-MM-DD.
        """
        payload = {"name": name}
        if expire_date:
            payload["expiredDate"] = expire_date

        async with self._session.post(
            self.url_builder("/api/wireguard/client"),
            json=payload
        ) as response:
            if response.status not in [200, 201]:
                try:
                    json_response = await response.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при создании клиента.")
                except aiohttp.ContentTypeError:
                    error_message = await response.text()
                logger.debug(f"Ответ сервера при создании клиента: статус={response.status}, сообщение={error_message}")
                raise Exception(f"Ошибка при создании клиента: {error_message}")
            else:
                logger.debug(f"Клиент '{name}' успешно создан.")
                # Потребляем тело ответа, чтобы избежать предупреждений
                try:
                    await response.text()
                except Exception as e:
                    logger.warning(f"Не удалось полностью потребить тело ответа при создании клиента: {e}")

    async def update_client_expire_date(self, uid: str, expire_date: str = None):
        """
        Обновляет дату истечения у клиента по UID.
        Если expire_date=None, возможно, нужно передать {"expireDate": null} или пустой JSON.
        """
        payload = {"expireDate": expire_date} if expire_date is not None else {}
        async with self._session.put(
            self.url_builder(f"/api/wireguard/client/{uid}/expireDate"),
            json=payload
        ) as response:
            if response.status != 200:
                try:
                    json_response = await response.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при обновлении даты истечения.")
                except aiohttp.ContentTypeError:
                    error_message = await response.text()
                logger.debug(f"Ответ сервера при обновлении даты истечения: статус={response.status}, сообщение={error_message}")
                raise Exception(f"Ошибка при обновлении даты истечения: {error_message}")
            else:
                logger.debug(f"Дата истечения клиента '{uid}' успешно обновлена.")
                # Потребляем тело ответа, чтобы избежать предупреждений
                try:
                    await response.text()
                except Exception as e:
                    logger.warning(f"Не удалось полностью потребить тело ответа при обновлении даты истечения: {e}")
