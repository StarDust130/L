from logging.config import fileConfig

from alembic import context
from app.core.config import get_settings
from app.db.db import Base
from sqlalchemy import engine_from_config, pool

# ⚙️ Get Alembic's configuration object.
config = context.config

# 🔧 Load application settings.
settings = get_settings()

# 🗄️ Use the same database URL as FastAPI.
config.set_main_option(
    "sqlalchemy.url",
    settings.database_url,
)

# 📝 Configure Alembic logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# 🧠 Import models so Alembic can detect their tables.
from app.job.job_model import Job  # noqa: F401

# 📋 Tell Alembic about our SQLAlchemy tables.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without opening a database connection."""

    # 🔗 Get the database URL.
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    # 🚀 Run the migration.
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a database connection."""

    # 🔌 Create a database engine.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # 🔗 Connect to PostgreSQL.
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        # 🚀 Run the migration.
        with context.begin_transaction():
            context.run_migrations()


# 🔀 Choose the migration mode.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
