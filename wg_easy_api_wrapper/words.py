#!/usr/bin/env python3
import asyncio
import os
import datetime
import logging

import click
from dotenv import load_dotenv

from .server import Server
from .words_generator import get_random_name

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@click.group()
@click.option('--url', default=None, help='WG-Easy server URL')
@click.option('--password', default=None, help='WG-Easy admin password')
@click.pass_context
def cli(ctx, url, password):
    """
    CLI для управления WG-Easy.
    Параметры можно указать через флаги или через файл .env.
    """
    # Загружаем переменные окружения из .env, если он существует
    load_dotenv()

    # Если URL не указан, берем из переменных окружения или используем значение по умолчанию
    if url is None:
        url = os.getenv("WG_EASY_SERVER_URL", "http://127.0.0.1:51821")

    # Если пароль не указан, берем из переменных окружения
    if password is None:
        password = os.getenv("WG_EASY_PASSWORD", "")

    ctx.ensure_object(dict)
    ctx.obj['url'] = url
    ctx.obj['password'] = password

@cli.command()
@click.pass_context
def list_clients(ctx):
    """Вывести список всех WireGuard-клиентов."""
    url = ctx.obj['url']
    password = ctx.obj['password']

    async def _list():
        async with Server(url, password) as server:
            clients = await server.get_clients()
            if not clients:
                click.echo("Нет доступных клиентов.")
                return
            for client in clients:
                click.echo(
                    f"UID: {client.uid}\n"
                    f"  Имя: {client.name}\n"
                    f"  Включен: {'Да' if client.enabled else 'Нет'}\n"
                    f"  Адрес: {client.address}\n"
                    f"  Дата создания: {client.created_at.strftime('%Y-%m-%d')}\n"
                    f"  Дата последней связи: {client.last_handshake_at.strftime('%Y-%m-%d') if client.last_handshake_at else 'Никогда'}\n"
                    f"  Перманентный KeepAlive: {client.persistent_keepalive}\n"
                    f"  Трафик RX: {client.transfer_rx} байт\n"
                    f"  Трафик TX: {client.transfer_tx} байт\n"
                    f"  Обновлено: {client.updated_at.strftime('%Y-%m-%d')}\n"
                    "-------------------------------------"
                )
    try:
        asyncio.run(_list())
    except Exception as e:
        logger.exception("Ошибка при выводе списка клиентов")
        click.echo(f"Ошибка при выводе списка клиентов: {e}")

@cli.command()
@click.argument('name')
@click.option('--expire-date', default=None, help="Дата истечения в формате YYYY-MM-DD")
@click.option('--days', default=None, type=int, help="Количество дней до истечения от сегодняшней даты")
@click.pass_context
def create_client(ctx, name, expire_date, days):
    """
    Создать нового клиента с заданным ИМЕНЕМ.
    Если клиент с таким именем уже существует, обновить его дату истечения.
    Можно указать дату истечения либо в виде абсолютной даты, либо в днях от текущей даты.
    """
    url = ctx.obj['url']
    password = ctx.obj['password']

    async def _create_or_update():
        # Если указано количество дней, вычисляем дату истечения
        if days is not None:
            new_date = datetime.date.today() + datetime.timedelta(days=days)
            calculated_expire_date = new_date.strftime("%Y-%m-%d")
        else:
            calculated_expire_date = expire_date

        async with Server(url, password) as server:
            try:
                # Получаем список всех клиентов
                clients = await server.get_clients()
                # Ищем клиента с заданным именем
                existing_client = next((c for c in clients if c.name == name), None)
                if existing_client:
                    # Если клиент существует, обновляем его дату истечения
                    await server.update_client_expire_date(existing_client.uid, calculated_expire_date)
                    click.echo(
                        f"Клиент '{name}' уже существует. Дата истечения обновлена до: {calculated_expire_date or 'Нет'}"
                    )
                else:
                    # Если клиента нет, создаём нового
                    await server.create_client(name, calculated_expire_date)
                    click.echo(
                        f"Клиент '{name}' создан. Дата истечения: {calculated_expire_date or 'Нет'}"
                    )
            except Exception as e:
                # Логируем полную трассировку ошибки
                logger.exception("Ошибка при создании или обновлении клиента")
                click.echo(f"Ошибка при создании или обновлении клиента: {e}")

    try:
        asyncio.run(_create_or_update())
    except Exception as e:
        logger.exception("Необработанная ошибка при создании или обновлении клиента")
        click.echo(f"Необработанная ошибка при создании или обновлении клиента: {e}")

@cli.command()
@click.argument('uid')
@click.pass_context
def delete_client(ctx, uid):
    """Удалить клиента по UID."""
    url = ctx.obj['url']
    password = ctx.obj['password']

    async def _delete():
        async with Server(url, password) as server:
            try:
                client = await server.get_client(uid)
                if not client:
                    click.echo(f"Клиент с UID={uid} не найден.")
                    return
                await server.remove_client(uid)
                click.echo(f"Клиент '{client.name}' (UID={uid}) удален.")
            except Exception as e:
                logger.exception("Ошибка при удалении клиента")
                click.echo(f"Ошибка при удалении клиента: {e}")

    try:
        asyncio.run(_delete())
    except Exception as e:
        logger.exception("Необработанная ошибка при удалении клиента")
        click.echo(f"Необработанная ошибка при удалении клиента: {e}")

@cli.command()
@click.argument('uid')
@click.pass_context
def enable_client(ctx, uid):
    """Включить клиента по UID."""
    url = ctx.obj['url']
    password = ctx.obj['password']

    async def _enable():
        async with Server(url, password) as server:
            try:
                client = await server.get_client(uid)
                if not client:
                    click.echo(f"Клиент с UID={uid} не найден.")
                    return
                if client.enabled:
                    click.echo(f"Клиент '{client.name}' уже включен.")
                    return
                await client.enable()
                click.echo(f"Клиент '{client.name}' (UID={uid}) включен.")
            except Exception as e:
                logger.exception("Ошибка при включении клиента")
                click.echo(f"Ошибка при включении клиента: {e}")

    try:
        asyncio.run(_enable())
    except Exception as e:
        logger.exception("Необработанная ошибка при включении клиента")
        click.echo(f"Необработанная ошибка при включении клиента: {e}")

@cli.command()
@click.argument('uid')
@click.pass_context
def disable_client(ctx, uid):
    """Отключить клиента по UID."""
    url = ctx.obj['url']
    password = ctx.obj['password']

    async def _disable():
        async with Server(url, password) as server:
            try:
                client = await server.get_client(uid)
                if not client:
                    click.echo(f"Клиент с UID={uid} не найден.")
                    return
                if not client.enabled:
                    click.echo(f"Клиент '{client.name}' уже отключен.")
                    return
                await client.disable()
                click.echo(f"Клиент '{client.name}' (UID={uid}) отключен.")
            except Exception as e:
                logger.exception("Ошибка при отключении клиента")
                click.echo(f"Ошибка при отключении клиента: {e}")

    try:
        asyncio.run(_disable())
    except Exception as e:
        logger.exception("Необработанная ошибка при отключении клиента")
        click.echo(f"Необработанная ошибка при отключении клиента: {e}")

@cli.command()
@click.argument('uid')
@click.option('--expire-date', default=None, help="Новая дата истечения в формате YYYY-MM-DD")
@click.option('--days', default=None, type=int, help="Количество дней до нового истечения от сегодняшней даты")
@click.pass_context
def update_client_expire(ctx, uid, expire_date, days):
    """Обновить дату истечения для клиента по UID."""
    url = ctx.obj['url']
    password = ctx.obj['password']

    async def _update():
        # Если указано количество дней, вычисляем новую дату истечения
        if days is not None:
            new_date = datetime.date.today() + datetime.timedelta(days=days)
            calculated_expire_date = new_date.strftime("%Y-%m-%d")
        else:
            calculated_expire_date = expire_date

        async with Server(url, password) as server:
            try:
                client = await server.get_client(uid)
                if not client:
                    click.echo(f"Клиент с UID={uid} не найден.")
                    return
                await server.update_client_expire_date(uid, calculated_expire_date)
                click.echo(
                    f"Дата истечения для клиента '{client.name}' (UID={uid}) обновлена до: "
                    f"{calculated_expire_date or 'Нет'}"
                )
            except Exception as e:
                logger.exception("Ошибка при обновлении даты истечения")
                click.echo(f"Ошибка при обновлении даты истечения: {e}")

    try:
        asyncio.run(_update())
    except Exception as e:
        logger.exception("Необработанная ошибка при обновлении даты истечения клиента")
        click.echo(f"Необработанная ошибка при обновлении даты истечения клиента: {e}")

@cli.command()
@click.argument('uid')
@click.pass_context
def get_qr(ctx, uid):
    """Получить QR-код клиента в формате SVG по UID."""
    url = ctx.obj['url']
    password = ctx.obj['password']

    async def _qr():
        async with Server(url, password) as server:
            try:
                client = await server.get_client(uid)
                if not client:
                    click.echo(f"Клиент с UID={uid} не найден.")
                    return
                response = await client.get_qr_code()
                if response.status != 200:
                    try:
                        json_response = await response.json()
                        error_message = json_response.get("error", "Неизвестная ошибка при получении QR-кода.")
                    except aiohttp.ContentTypeError:
                        error_message = await response.text()
                    raise Exception(f"Ошибка при получении QR-кода: {error_message}")
                svg_content = await response.text()
                click.echo(svg_content)
            except Exception as e:
                logger.exception("Ошибка при получении QR-кода")
                click.echo(f"Ошибка при получении QR-кода: {e}")

    try:
        asyncio.run(_qr())
    except Exception as e:
        logger.exception("Необработанная ошибка при получении QR-кода клиента")
        click.echo(f"Необработанная ошибка при получении QR-кода клиента: {e}")

@cli.command()
@click.argument('uid')
@click.pass_context
def get_conf(ctx, uid):
    """Получить конфигурацию клиента по UID."""
    url = ctx.obj['url']
    password = ctx.obj['password']

    async def _conf():
        async with Server(url, password) as server:
            try:
                client = await server.get_client(uid)
                if not client:
                    click.echo(f"Клиент с UID={uid} не найден.")
                    return
                config_text = await client.get_configuration()
                click.echo(config_text)
            except Exception as e:
                logger.exception("Ошибка при получении конфигурации")
                click.echo(f"Ошибка при получении конфигурации: {e}")

    try:
        asyncio.run(_conf())
    except Exception as e:
        logger.exception("Необработанная ошибка при получении конфигурации клиента")
        click.echo(f"Необработанная ошибка при получении конфигурации клиента: {e}")

@cli.command()
@click.option('--count', '-n', default=1, help='Количество клиентов для генерации.')
@click.option('--expire-date', default=None, help='Дата истечения в формате YYYY-MM-DD')
@click.option('--days', default=None, type=int, help='Количество дней до истечения от сегодняшней даты')
@click.pass_context
def generate_clients(ctx, count, expire_date, days):
    """
    Генерировать случайные имена клиентов (прилагательное + существительное) и создавать их.
    Пример: 'happy-lion'.
    """
    url = ctx.obj['url']
    password = ctx.obj['password']

    async def _generate():
        async with Server(url, password) as server:
            for _ in range(count):
                try:
                    name = get_random_name()
                    # Если указано количество дней, вычисляем дату истечения
                    if days is not None:
                        new_date = datetime.date.today() + datetime.timedelta(days=days)
                        calculated_expire_date = new_date.strftime("%Y-%m-%d")
                    else:
                        calculated_expire_date = expire_date
                    await server.create_client(name, calculated_expire_date)
                    click.echo(
                        f"Создан клиент '{name}'. "
                        f"Дата истечения: {calculated_expire_date or 'Нет'}"
                    )
                except Exception as e:
                    logger.exception(f"Ошибка при создании клиента '{name}'")
                    click.echo(f"Ошибка при создании клиента '{name}': {e}")

    try:
        asyncio.run(_generate())
    except Exception as e:
        logger.exception("Необработанная ошибка при генерации клиентов")
        click.echo(f"Необработанная ошибка при генерации клиентов: {e}")
