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

    season = await integration_client.post("/seasons", json={"number": 1, "show_id": show_id, "release_date": "2026-01-02"}, headers=headers)
    assert season.status_code == 201
    season_id = season.json()["id"]

    episode = await integration_client.post("/episodes", json={"title": "Pilot", "number": 1, "season_id": season_id, "release_date": "2026-01-03"}, headers=headers)
    assert episode.status_code == 201
    episode_id = episode.json()["id"]

    viewed = await integration_client.post(f"/episodes/{episode_id}/view", headers=headers)
    assert viewed.status_code == 200
    duplicate = await integration_client.post(f"/episodes/{episode_id}/view", headers=headers)
    assert duplicate.status_code == 409

