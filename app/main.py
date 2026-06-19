from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, first_user_is_admin, get_current_user, hash_password, require_admin, verify_password
from app.database import get_session
from app.models import Episode, Season, Show, User, View
from app.schemas import EpisodeCreate, EpisodeResponse, EpisodeUpdate, LoginRequest, SeasonCreate, SeasonResponse, SeasonUpdate, ShowCreate, ShowResponse, ShowUpdate, SignupRequest, TokenResponse, UserResponse, ViewResponse

app = FastAPI(title="TV Show Schedules")


@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, session: AsyncSession = Depends(get_session)):
    email = payload.email
    password = payload.password
    existing = await session.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(email=email, password_hash=hash_password(password), is_admin=await first_user_is_admin(session))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserResponse.model_validate(user)


@app.post("/auth/login")
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(user.id, user.is_admin))


@app.post("/shows", status_code=status.HTTP_201_CREATED)
async def create_show(payload: ShowCreate, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    show = Show(**payload.model_dump())
    session.add(show)
    await session.commit()
    await session.refresh(show)
    return ShowResponse.model_validate(show)


@app.get("/shows")
async def list_shows(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Show).order_by(Show.id))
    return [ShowResponse.model_validate(show) for show in result.scalars().all()]


@app.get("/shows/{show_id}")
async def get_show(show_id: int, session: AsyncSession = Depends(get_session)):
    show = await session.get(Show, show_id)
    if show is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    return ShowResponse.model_validate(show)


@app.put("/shows/{show_id}")
async def update_show(show_id: int, payload: ShowUpdate, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    show = await session.get(Show, show_id)
    if show is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    show.title = payload.title
    show.release_date = payload.release_date
    await session.commit()
    await session.refresh(show)
    return ShowResponse.model_validate(show)


@app.delete("/shows/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(show_id: int, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    show = await session.get(Show, show_id)
    if show is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    await session.delete(show)
    await session.commit()


@app.post("/seasons", status_code=status.HTTP_201_CREATED)
async def create_season(payload: SeasonCreate, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    season = Season(**payload.model_dump())
    session.add(season)
    await session.commit()
    await session.refresh(season)
    return SeasonResponse.model_validate(season)


@app.get("/seasons")
async def list_seasons(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Season).order_by(Season.id))
    return [SeasonResponse.model_validate(season) for season in result.scalars().all()]


@app.get("/seasons/{season_id}")
async def get_season(season_id: int, session: AsyncSession = Depends(get_session)):
    season = await session.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Season not found")
    return SeasonResponse.model_validate(season)


@app.put("/seasons/{season_id}")
async def update_season(season_id: int, payload: SeasonUpdate, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    season = await session.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Season not found")
    for key, value in payload.model_dump().items():
        setattr(season, key, value)
    await session.commit()
    await session.refresh(season)
    return SeasonResponse.model_validate(season)


@app.delete("/seasons/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_season(season_id: int, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    season = await session.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Season not found")
    await session.delete(season)
    await session.commit()


@app.post("/episodes", status_code=status.HTTP_201_CREATED)
async def create_episode(payload: EpisodeCreate, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    episode = Episode(**payload.model_dump())
    session.add(episode)
    await session.commit()
    await session.refresh(episode)
    return EpisodeResponse.model_validate(episode)


@app.get("/episodes")
async def list_episodes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Episode).order_by(Episode.id))
    return [EpisodeResponse.model_validate(episode) for episode in result.scalars().all()]


@app.get("/episodes/{episode_id}")
async def get_episode(episode_id: int, session: AsyncSession = Depends(get_session)):
    episode = await session.get(Episode, episode_id)
    if episode is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    return EpisodeResponse.model_validate(episode)


@app.put("/episodes/{episode_id}")
async def update_episode(episode_id: int, payload: EpisodeUpdate, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    episode = await session.get(Episode, episode_id)
    if episode is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    for key, value in payload.model_dump().items():
        setattr(episode, key, value)
    await session.commit()
    await session.refresh(episode)
    return EpisodeResponse.model_validate(episode)


@app.delete("/episodes/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_episode(episode_id: int, _: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    episode = await session.get(Episode, episode_id)
    if episode is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    await session.delete(episode)
    await session.commit()


@app.post("/episodes/{episode_id}/view")
async def mark_episode_viewed(
    episode_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    episode = await session.get(Episode, episode_id)
    if episode is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    view = View(user_id=user.id, episode_id=episode.id)
    session.add(view)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Episode already marked as viewed")
    await session.refresh(view)
    return ViewResponse.model_validate(view)
