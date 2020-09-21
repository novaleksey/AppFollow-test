import asyncpg
import asyncio
from main import init_args


async def make_migrations():
    args = init_args()
    db = await asyncpg.create_pool(
        f'postgres://{args.user}:{args.passwd}@{args.host}:{args.port}/{args.dbname}'
    )
    async with db.acquire() as conn:
        async with conn.transaction():
            await conn.execute('''
                CREATE SEQUENCE "public"."news_seq"
                INCREMENT 1
                MINVALUE 1
                MAXVALUE 999999
                START 1
                CACHE 1;
            ''')
            await conn.execute('''
                CREATE TABLE "public"."news" (
                "id" Integer DEFAULT nextval('news_seq'::regclass) NOT NULL,
                "title" Character Varying( 2044 ) NOT NULL,
                "url" Character Varying( 2044 ),
                "created_at" Timestamp With Time Zone DEFAULT now() NOT NULL,
                "source_id" Integer NOT NULL,
                CONSTRAINT "unique_news_id" UNIQUE( "id" ) );
            ''')

asyncio.get_event_loop().run_until_complete(make_migrations())