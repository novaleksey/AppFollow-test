"""
Модуль вспомогательных функций и обработчиков запросов
"""

from typing import List, Dict

__author__ = 'Novozhilov A.S.'


def validate_params(params) -> bool:
    """
    Валидация параметров запроса. Проверка типов.
    Args:
        params(MultiDictProxy): параметры

    Returns:
        bool: валидные или нет
    """
    if 'limit' in params:
        try:
            if int(params['limit']) < 0:
                return False
        except ValueError:
            return False

    if 'offset' in params:
        try:
            if int(params['offset']) < 0:
                return False
        except ValueError:
            return False

    if 'order' in params and params['order'] not in ['id', 'title', 'url', 'created_at']:
        return False

    if 'sort' in params and params['sort'] not in ['asc', 'desc']:
        return False

    return True


async def get_local_news(db=None, **kwargs) -> List[Dict]:
    """
    Получение записей из бд согласно фильтру
    Args:
        db: инстанс коннекта к бд
        **kwargs: параметры запроса

    Returns:
        List[Dict]: выборка из бд
    """
    limit = int(kwargs.get('limit', 5))
    offset = int(kwargs.get('offset', 0))
    order = kwargs.get('order') or 'id'
    sort = kwargs.get('sort') or 'asc'
    async with db.acquire() as conn:
        async with conn.transaction():
            res = await conn.fetch(f'''
                SELECT id, title, url, created_at
                FROM news
                ORDER BY {order} {sort}
                LIMIT $1
                OFFSET $2
            ''', limit, offset)
            res = [dict(rec) for rec in res]
            for row in res:
                row['created_at'] = str(row['created_at'])
            return res
