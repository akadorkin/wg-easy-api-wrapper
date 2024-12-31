from datetime import datetime
from typing import TYPE_CHECKING

import aiohttp

time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

if TYPE_CHECKING:
    from .server import Server


class Client:
    def __init__(
        self,
        address: str,
        created_at: str,
        enabled: bool,
        uid: str,
        last_handshake_at: str,
        name: str,
        persistent_keepalive: str,
        public_key: str,
        transfer_rx: int,
        transfer_tx: int,
        updated_at: str,
        session: aiohttp.ClientSession,
        server: 'Server',
    ):
        self._address = address
        self._created_at = datetime.strptime(created_at, time_format)
        self._enabled = bool(enabled)
        self._uid = uid
        self._last_handshake_at = (
            datetime.strptime(last_handshake_at, time_format) if last_handshake_at else None
        )
        self._name = name
        self._persistent_keepalive = persistent_keepalive
        self._public_key = public_key
        self._transfer_rx = transfer_rx
        self._transfer_tx = transfer_tx
        self._updated_at = datetime.strptime(updated_at, time_format)
        self._session = session
        self._server = server

    @classmethod
    def from_json(cls, json, session: aiohttp.ClientSession, server: 'Server'):
        return cls(
            address=json["address"],
            created_at=json["createdAt"],
            enabled=bool(json["enabled"]),
            uid=json["id"],
            last_handshake_at=json["latestHandshakeAt"],
            name=json["name"],
            persistent_keepalive=json["persistentKeepalive"],
            public_key=json["publicKey"],
            transfer_rx=json["transferRx"],
            transfer_tx=json["transferTx"],
            updated_at=json["updatedAt"],
            session=session,
            server=server,
        )

    @property
    def name(self):
        return self._name

    @name.setter
    async def name(self, value):
        async with self._session.put(
            self._server.url_builder(f"/api/wireguard/client/{self._uid}/name"),
            json={"name": value},
        ) as response:
            if response.status != 200:
                try:
                    json_response = await response.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при обновлении имени клиента.")
                except aiohttp.ContentTypeError:
                    error_message = await response.text()
                raise Exception(f"Ошибка при обновлении имени клиента: {error_message}")
            self._name = value

    @property
    def address(self):
        return self._address

    @address.setter
    async def address(self, value):
        async with self._session.put(
            self._server.url_builder(f"/api/wireguard/client/{self._uid}/address"),
            json={"address": value},
        ) as response:
            if response.status != 200:
                try:
                    json_response = await response.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при обновлении адреса клиента.")
                except aiohttp.ContentTypeError:
                    error_message = await response.text()
                raise Exception(f"Ошибка при обновлении адреса клиента: {error_message}")
            self._address = value

    @property
    def created_at(self):
        return self._created_at

    @property
    def last_handshake_at(self):
        return self._last_handshake_at

    @property
    def updated_at(self):
        return self._updated_at

    @property
    def enabled(self):
        return self._enabled

    @property
    def uid(self):
        return self._uid

    @property
    def persistent_keepalive(self):
        return self._persistent_keepalive

    @property
    def public_key(self):
        return self._public_key

    @property
    def transfer_rx(self):
        return self._transfer_rx

    @property
    def transfer_tx(self):
        return self._transfer_tx

    async def enable(self):
        if self._enabled:
            raise ValueError("Client is already enabled")
        async with self._session.post(
            self._server.url_builder(f"/api/wireguard/client/{self._uid}/enable"),
            json={"enable": True},
        ) as response:
            if response.status != 200:
                try:
                    json_response = await response.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при включении клиента.")
                except aiohttp.ContentTypeError:
                    error_message = await response.text()
                raise Exception(f"Ошибка при включении клиента: {error_message}")
            self._enabled = True

    async def disable(self):
        if not self._enabled:
            raise ValueError("Client is already disabled")
        async with self._session.post(
            self._server.url_builder(f"/api/wireguard/client/{self._uid}/disable"),
        ) as response:
            if response.status != 200:
                try:
                    json_response = await response.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при отключении клиента.")
                except aiohttp.ContentTypeError:
                    error_message = await response.text()
                raise Exception(f"Ошибка при отключении клиента: {error_message}")
            self._enabled = False

    async def get_qr_code(self) -> str:
        """Возвращает SVG-код QR в виде строки."""
        async with self._session.get(
            self._server.url_builder(f"/api/wireguard/client/{self._uid}/qrcode.svg")
        ) as response:
            if response.status != 200:
                try:
                    json_response = await response.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при получении QR-кода.")
                except aiohttp.ContentTypeError:
                    error_message = await response.text()
                raise Exception(f"Ошибка при получении QR-кода: {error_message}")
            svg_content = await response.text()
            return svg_content

    async def get_configuration(self) -> str:
        """Возвращает конфигурацию клиента (строкой)."""
        async with self._session.get(
            self._server.url_builder(f"/api/wireguard/client/{self._uid}/configuration")
        ) as config_file:
            if config_file.status != 200:
                try:
                    json_response = await config_file.json()
                    error_message = json_response.get("error", "Неизвестная ошибка при получении конфигурации.")
                except aiohttp.ContentTypeError:
                    error_message = await config_file.text()
                raise Exception(f"Ошибка при получении конфигурации: {error_message}")
            config_text = await config_file.text()
            return config_text
