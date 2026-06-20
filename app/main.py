from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    create_user,
    first_user_is_admin,
    get_current_user,
    require_admin,
    verify_password,
)
from app.database import get_session
from app.models import Episode, Season, Show, User, View
from app.schemas import (
    EpisodeCreate,
    EpisodeResponse,
    EpisodeUpdate,
    LoginRequest,
    SeasonCreate,
    SeasonResponse,
    SeasonUpdate,
    ShowCreate,
    ShowResponse,
    ShowUpdate,
    SignupRequest,
    TokenResponse,
    UserResponse,
    ViewStateResponse,
)

app = FastAPI(title="TV Show Schedules")

auth_router = APIRouter(prefix="/auth", tags=["auth"])
shows_router = APIRouter(prefix="/shows", tags=["shows"])
seasons_router = APIRouter(prefix="/shows/{show_id}/seasons", tags=["seasons"])
episodes_router = APIRouter(prefix="/shows/{show_id}/seasons/{season_id}/episodes", tags=["episodes"])


async def get_show_or_404(show_id: int, session: AsyncSession) -> type[Show]:
    show = await session.get(Show, show_id)
    if show is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    return show


async def get_season_or_404(show_id: int, season_id: int, session: AsyncSession) -> type[Season]:
    season = await session.get(Season, season_id)
    if season is None or season.show_id != show_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Season not found")
    return season


async def get_episode_or_404(show_id: int, season_id: int, episode_id: int, session: AsyncSession) -> type[Episode]:
    season = await get_season_or_404(show_id, season_id, session)
    episode = await session.get(Episode, episode_id)
    if episode is None or episode.season_id != season.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    return episode


async def get_view_state_or_none(user_id: int, episode_id: int, session: AsyncSession) -> View | None:
    result = await session.execute(select(View).where(View.user_id == user_id, View.episode_id == episode_id))
    return result.scalar_one_or_none()


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signup(payload: SignupRequest, session: AsyncSession = Depends(get_session)):
    existing = await session.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = await create_user(session, payload.email, payload.password, await first_user_is_admin(session))
    return UserResponse.model_validate(user)


@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(user.id, user.is_admin))


@shows_router.post("", status_code=status.HTTP_201_CREATED, response_model=ShowResponse)
async def create_show(
    payload: ShowCreate, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)
):
    show = Show(**payload.model_dump())
    session.add(show)
    await session.commit()
    await session.refresh(show)
    return ShowResponse.model_validate(show)


@shows_router.get("", response_model=list[ShowResponse])
async def list_shows(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Show).order_by(Show.id))
    return [ShowResponse.model_validate(show) for show in result.scalars().all()]


@shows_router.get("/{show_id}", response_model=ShowResponse)
async def get_show(show_id: int, session: AsyncSession = Depends(get_session)):
    show = await get_show_or_404(show_id, session)
    return ShowResponse.model_validate(show)


@shows_router.put("/{show_id}", response_model=ShowResponse)
async def update_show(
    show_id: int, payload: ShowUpdate, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)
):
    show = await get_show_or_404(show_id, session)
    show.title = payload.title
    show.release_date = payload.release_date
    await session.commit()
    await session.refresh(show)
    return ShowResponse.model_validate(show)


@shows_router.delete("/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(show_id: int, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    show = await get_show_or_404(show_id, session)
    await session.delete(show)
    await session.commit()


@seasons_router.post("", status_code=status.HTTP_201_CREATED, response_model=SeasonResponse)
async def create_season(
    show_id: int,
    payload: SeasonCreate,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    await get_show_or_404(show_id, session)
    season = Season(show_id=show_id, **payload.model_dump())
    session.add(season)
    await session.commit()
    await session.refresh(season)
    return SeasonResponse.model_validate(season)


@seasons_router.get("", response_model=list[SeasonResponse])
async def list_seasons(show_id: int, session: AsyncSession = Depends(get_session)):
    await get_show_or_404(show_id, session)
    result = await session.execute(select(Season).where(Season.show_id == show_id).order_by(Season.id))
    return [SeasonResponse.model_validate(season) for season in result.scalars().all()]


@seasons_router.get("/{season_id}", response_model=SeasonResponse)
async def get_season(show_id: int, season_id: int, session: AsyncSession = Depends(get_session)):
    season = await get_season_or_404(show_id, season_id, session)
    return SeasonResponse.model_validate(season)


@seasons_router.put("/{season_id}", response_model=SeasonResponse)
async def update_season(
    show_id: int,
    season_id: int,
    payload: SeasonUpdate,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    season = await get_season_or_404(show_id, season_id, session)
    season.number = payload.number
    season.release_date = payload.release_date
    await session.commit()
    await session.refresh(season)
    return SeasonResponse.model_validate(season)


@seasons_router.delete("/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_season(
    show_id: int,
    season_id: int,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    season = await get_season_or_404(show_id, season_id, session)
    await session.delete(season)
    await session.commit()


@episodes_router.post("", status_code=status.HTTP_201_CREATED, response_model=EpisodeResponse)
async def create_episode(
    show_id: int,
    season_id: int,
    payload: EpisodeCreate,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    season = await get_season_or_404(show_id, season_id, session)
    episode = Episode(season_id=season.id, **payload.model_dump())
    session.add(episode)
    await session.commit()
    await session.refresh(episode)
    return EpisodeResponse.model_validate(episode)


@episodes_router.get("", response_model=list[EpisodeResponse])
async def list_episodes(show_id: int, season_id: int, session: AsyncSession = Depends(get_session)):
    await get_season_or_404(show_id, season_id, session)
    result = await session.execute(select(Episode).where(Episode.season_id == season_id).order_by(Episode.id))
    return [EpisodeResponse.model_validate(episode) for episode in result.scalars().all()]


@episodes_router.get("/{episode_id}", response_model=EpisodeResponse)
async def get_episode(show_id: int, season_id: int, episode_id: int, session: AsyncSession = Depends(get_session)):
    episode = await get_episode_or_404(show_id, season_id, episode_id, session)
    return EpisodeResponse.model_validate(episode)


@episodes_router.put("/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    show_id: int,
    season_id: int,
    episode_id: int,
    payload: EpisodeUpdate,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    episode = await get_episode_or_404(show_id, season_id, episode_id, session)
    episode.title = payload.title
    episode.number = payload.number
    episode.release_date = payload.release_date
    await session.commit()
    await session.refresh(episode)
    return EpisodeResponse.model_validate(episode)


@episodes_router.delete("/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_episode(
    show_id: int,
    season_id: int,
    episode_id: int,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    episode = await get_episode_or_404(show_id, season_id, episode_id, session)
    await session.delete(episode)
    await session.commit()


@episodes_router.get("/{episode_id}/view", response_model=ViewStateResponse)
async def get_episode_view(
    show_id: int,
    season_id: int,
    episode_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await get_episode_or_404(show_id, season_id, episode_id, session)
    view = await get_view_state_or_none(user.id, episode_id, session)
    return ViewStateResponse(viewed=view is not None, viewed_at=view.viewed_at if view else None)


@episodes_router.post("/{episode_id}/view", response_model=ViewStateResponse)
async def mark_episode_viewed(
    show_id: int,
    season_id: int,
    episode_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await get_episode_or_404(show_id, season_id, episode_id, session)
    view = await get_view_state_or_none(user.id, episode_id, session)
    if view is None:
        view = View(user_id=user.id, episode_id=episode_id)
        session.add(view)
        await session.commit()
        await session.refresh(view)
    return ViewStateResponse(viewed=True, viewed_at=view.viewed_at)


@episodes_router.delete("/{episode_id}/view", response_model=ViewStateResponse)
async def unmark_episode_viewed(
    show_id: int,
    season_id: int,
    episode_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await get_episode_or_404(show_id, season_id, episode_id, session)
    view = await get_view_state_or_none(user.id, episode_id, session)
    if view is not None:
        await session.delete(view)
        await session.commit()
    return ViewStateResponse(viewed=False, viewed_at=None)


app.include_router(auth_router)
app.include_router(shows_router)
app.include_router(seasons_router)
app.include_router(episodes_router)
