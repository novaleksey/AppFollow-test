"""
Модуль обработки загрузки новостей с определенной периодичностью
"""
import asyncio
from asyncpg.exceptions import NotNullViolationError
from asyncpg.pool import Pool
from aiohttp import ClientSession

__author__ = 'Novozhilov A.S.'

_GET_NEWS_IDS_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
_GET_NEWS_DATA_URL = 'https://hacker-news.firebaseio.com/v0/item/{}.json'


async def background_parser(db: Pool, timeout: int, max_news_count: int) -> None:
    """
    Корутина для обновления новостей в бд.
    Args:
        db(asyncpg.Pool): инстанс коннекта к бд
        timeout(int): периодичность выполнения задачи в секундах
        max_news_count(int): кол-во новостей, которые необходимо хранить

    Returns:
        None
    """
    while True:
        async with ClientSession() as session:
            await get_news(db, session, max_news_count)
        await asyncio.sleep(timeout)


async def get_news(db: Pool, session: ClientSession, news_count_max: int) -> None:
    """
    Получение информации о новости с источника, вычисление разницы с локальными данными.
    Args:
        db(asyncpg.Pool): инстанс коннекта к бд
        session(ClientSession): клиентская сессия
        news_count_max(int): кол-во новостей, которые необходимо хранить

    Returns:
        None
    """
    ids = await get_news_ids(session)
    ids = set(ids[:news_count_max])
    existed_ids = await get_existed_ids(db)
    ids_for_remove = existed_ids - ids
    # ids for insert
    ids.difference_update(existed_ids)
    for source_id in ids:
        async with session.get(_GET_NEWS_DATA_URL.format(source_id)) as res:
            assert res.status == 200
            content = await res.json()
            await collect_news(db, content)

    await remove_old_news(db, ids_for_remove)


async def get_news_ids(session: ClientSession) -> list:
    """
    Получение списка идентификаторов последних новостей
    Args:
        session(ClientSession): клиентская сессия

    Returns:
        list: список идентификаторов
    """
    async with session.get(_GET_NEWS_IDS_URL) as res:
        assert res.status == 200
        return await res.json()


async def get_existed_ids(db: Pool) -> set:
    """
    Получение списка идентификаторов новостей, которые уже сохранили в бд
    Args:
        db(asyncpg.Pool): инстанс коннекта к бд

    Returns:
        set: множество идентификаторов
    """
    async with db.acquire() as conn:
        async with conn.transaction():
            res = await conn.fetchrow('''
                SELECT array_agg(source_id) as existed_ids
                FROM news
            ''')
            res = res.get('existed_ids') or []
            return set(res)


async def collect_news(db: Pool, news_content: dict) -> None:
    """
    Заполнение бд записями
    Args:
        db(asyncpg.Pool): инстанс коннекта к бд
        news_content(dict): данные новости(url, title, ext_id)

    Returns:
        None
    """
    try:
        async with db.acquire() as conn:
            async with conn.transaction():
                await conn.execute('''
                    INSERT INTO news(title, url, source_id)
                    VALUES($1::TEXT, $2::TEXT, $3:: INT)
                ''', news_content.get('title'), news_content.get('url'), news_content.get('id'))
    except NotNullViolationError:
        pass


async def remove_old_news(db: Pool, news_ids: set) -> None:
    """
    Удаление локальных записей о новостях, которые уже не в топ N
    Args:
        db(asyncpg.Pool): инстанс коннекта к бд
        news_ids: идентификаторы для удаления

    Returns:
        None
    """
    async with db.acquire() as conn:
        async with conn.transaction():
            await conn.execute('''
            DELETE
            FROM news
            WHERE source_id = ANY($1::INT[])
            ''', news_ids)
