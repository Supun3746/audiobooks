from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, SecretStr
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Settings(BaseSettings):
    URL_DB: str
    TOKEN: SecretStr
    PATH_TO_BOOKS: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

engine = create_async_engine(settings.URL_DB)

session_factory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class Book(Base):
    __tablename__ = "books"
    name: Mapped[str]
    author: Mapped[str]
    book: Mapped[str]


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
