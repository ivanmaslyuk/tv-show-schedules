import os
from collections.abc import AsyncIterator
from datetime import date, timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.auth import create_access_token, create_user
from app.database import get_session
from app.main import app
from app.models import Base, Episode, Season, Show, User


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def unit_client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    database_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(database_url, future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def integration_client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_session():
        yield db_session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    return await create_user(db_session, "admin@example.com", "secret123", is_admin=True)


@pytest_asyncio.fixture
async def admin_headers(admin_user: User) -> dict[str, str]:
    token = create_access_token(admin_user.id, admin_user.is_admin)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def viewer_user(db_session: AsyncSession) -> User:
    return await create_user(db_session, "viewer@example.com", "secret123", is_admin=False)


@pytest_asyncio.fixture
async def viewer_headers(viewer_user: User) -> dict[str, str]:
    token = create_access_token(viewer_user.id, viewer_user.is_admin)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def show_data(db_session: AsyncSession) -> dict:
    show = Show(title="Shared State", release_date=date(2026, 1, 1))
    db_session.add(show)
    await db_session.commit()
    await db_session.refresh(show)

    season_one = Season(show_id=show.id, number=1, release_date=date(2026, 1, 2))
    season_two = Season(show_id=show.id, number=2, release_date=date(2026, 2, 2))
    db_session.add_all([season_one, season_two])
    await db_session.commit()
    await db_session.refresh(season_one)
    await db_session.refresh(season_two)

    season_one_episodes = [
        Episode(season_id=season_one.id, title="Pilot", number=1, release_date=date(2026, 1, 3)),
        Episode(season_id=season_one.id, title="Second", number=2, release_date=date(2026, 1, 10)),
        Episode(season_id=season_one.id, title="Third", number=3, release_date=date(2026, 1, 17)),
    ]
    season_two_episodes = [
        Episode(season_id=season_two.id, title="Return", number=1, release_date=date(2026, 2, 3)),
        Episode(season_id=season_two.id, title="Middle", number=2, release_date=date(2026, 2, 10)),
        Episode(season_id=season_two.id, title="Finale", number=3, release_date=date(2026, 2, 17)),
    ]
    db_session.add_all(season_one_episodes + season_two_episodes)
    await db_session.commit()
    for episode in season_one_episodes + season_two_episodes:
        await db_session.refresh(episode)

    return {
        "show": show,
        "seasons": 2,
        "seasons_one": season_one,
        "season_one_episodes": season_one_episodes,
        "seasons_two": season_two,
        "season_two_episodes": season_two_episodes,
    }


@pytest_asyncio.fixture
async def upcoming_show_data(db_session: AsyncSession) -> dict:
    today = date.today()

    shows = [
        Show(title="Watched Later", release_date=today),
        Show(title="Watched Soonest", release_date=today),
        Show(title="Watched After Past Episode", release_date=today),
        Show(title="Unwatched Show", release_date=today),
    ]
    db_session.add_all(shows)
    await db_session.commit()
    for show in shows:
        await db_session.refresh(show)

    seasons = [
        Season(show_id=shows[0].id, number=1, release_date=today),
        Season(show_id=shows[1].id, number=1, release_date=today),
        Season(show_id=shows[2].id, number=1, release_date=today),
        Season(show_id=shows[3].id, number=1, release_date=today),
    ]
    db_session.add_all(seasons)
    await db_session.commit()
    for season in seasons:
        await db_session.refresh(season)

    episodes = {
        "watched_later": [
            Episode(season_id=seasons[0].id, title="Later One", number=1, release_date=today + timedelta(days=7)),
            Episode(season_id=seasons[0].id, title="Later Two", number=2, release_date=today + timedelta(days=14)),
        ],
        "watched_soonest": [
            Episode(season_id=seasons[1].id, title="Soonest One", number=1, release_date=today + timedelta(days=1)),
            Episode(season_id=seasons[1].id, title="Soonest Two", number=2, release_date=today + timedelta(days=10)),
        ],
        "watched_after_past": [
            Episode(season_id=seasons[2].id, title="Already Aired", number=1, release_date=today - timedelta(days=3)),
            Episode(season_id=seasons[2].id, title="Next Up", number=2, release_date=today + timedelta(days=3)),
        ],
        "unwatched": [
            Episode(season_id=seasons[3].id, title="Ignored", number=1, release_date=today + timedelta(days=2)),
        ],
    }
    db_session.add_all(
        episodes["watched_later"]
        + episodes["watched_soonest"]
        + episodes["watched_after_past"]
        + episodes["unwatched"]
    )
    await db_session.commit()
    for episode_list in episodes.values():
        for episode in episode_list:
            await db_session.refresh(episode)

    return {
        "watched_later": {"show": shows[0], "season": seasons[0], "episodes": episodes["watched_later"]},
        "watched_soonest": {"show": shows[1], "season": seasons[1], "episodes": episodes["watched_soonest"]},
        "watched_after_past": {"show": shows[2], "season": seasons[2], "episodes": episodes["watched_after_past"]},
        "unwatched": {"show": shows[3], "season": seasons[3], "episodes": episodes["unwatched"]},
    }
