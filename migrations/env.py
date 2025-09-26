from sqlalchemy.ext.asyncio import create_async_engine
from app.database.models import Base
from alembic import context
from logging.config import fileConfig

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_online():
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"))
    async def do_run_migrations(connection):
        async with connection.begin() as conn:
            await conn.run_sync(lambda sync_conn: context.configure(connection=sync_conn, target_metadata=target_metadata))
            await conn.run_sync(context.run_migrations)

    import asyncio
    asyncio.run(do_run_migrations(connectable))

run_migrations_online()
