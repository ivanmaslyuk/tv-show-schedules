import pytest


pytestmark = pytest.mark.integration


async def test_signup_first_user_becomes_admin(integration_client):
    response = await integration_client.post("/auth/signup", json={"email": "admin@example.com", "password": "secret123"})
    assert response.status_code == 201
    assert response.json()["is_admin"] is True


async def test_admin_can_manage_show_and_view_episode(integration_client):
    await integration_client.post("/auth/signup", json={"email": "admin@example.com", "password": "secret123"})
    login = await integration_client.post("/auth/login", json={"email": "admin@example.com", "password": "secret123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    show = await integration_client.post("/shows", json={"title": "The Last Code", "release_date": "2026-01-01"}, headers=headers)
    assert show.status_code == 201
    show_id = show.json()["id"]

    seasons = await integration_client.post(
        f"/shows/{show_id}/seasons",
        json={"number": 1, "release_date": "2026-01-02"},
        headers=headers,
    )
    assert seasons.status_code == 201
    season_id = seasons.json()["id"]

    season_list = await integration_client.get(f"/shows/{show_id}/seasons", headers=headers)
    assert season_list.status_code == 200
    assert len(season_list.json()) == 1

    season = await integration_client.get(f"/shows/{show_id}/seasons/{season_id}", headers=headers)
    assert season.status_code == 200
    assert season.json()["show_id"] == show_id

    episode = await integration_client.post(
        f"/shows/{show_id}/seasons/{season_id}/episodes",
        json={"title": "Pilot", "number": 1, "release_date": "2026-01-03"},
        headers=headers,
    )
    assert episode.status_code == 201
    episode_id = episode.json()["id"]

    episode_list = await integration_client.get(f"/shows/{show_id}/seasons/{season_id}/episodes", headers=headers)
    assert episode_list.status_code == 200
    assert len(episode_list.json()) == 1

    viewed_before = await integration_client.get(f"/shows/{show_id}/seasons/{season_id}/episodes/{episode_id}/view", headers=headers)
    assert viewed_before.status_code == 200
    assert viewed_before.json()["viewed"] is False

    viewed = await integration_client.post(f"/shows/{show_id}/seasons/{season_id}/episodes/{episode_id}/view", headers=headers)
    assert viewed.status_code == 200
    assert viewed.json()["viewed"] is True

    viewed_after = await integration_client.get(f"/shows/{show_id}/seasons/{season_id}/episodes/{episode_id}/view", headers=headers)
    assert viewed_after.status_code == 200
    assert viewed_after.json()["viewed"] is True

    undone = await integration_client.delete(f"/shows/{show_id}/seasons/{season_id}/episodes/{episode_id}/view", headers=headers)
    assert undone.status_code == 200
    assert undone.json()["viewed"] is False
