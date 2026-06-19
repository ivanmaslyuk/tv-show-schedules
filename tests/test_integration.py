import pytest


pytestmark = pytest.mark.integration


async def test_signup_first_user_becomes_admin(integration_client):
    response = await integration_client.post("/auth/signup", json={"email": "admin@example.com", "password": "secret123"})
    assert response.status_code == 201
    assert response.json()["is_admin"] is True


async def test_admin_can_manage_show_and_view_episode(integration_client, admin_headers, show_data):
    headers = admin_headers
    show = show_data["show"]
    season_one = show_data["seasons_one"]
    season_one_episodes = show_data["season_one_episodes"]

    shows = await integration_client.get("/shows", headers=headers)
    assert shows.status_code == 200
    assert shows.json()[0]["id"] == show.id

    show_response = await integration_client.get(f"/shows/{show.id}", headers=headers)
    assert show_response.status_code == 200
    assert show_response.json()["id"] == show.id

    season_list = await integration_client.get(f"/shows/{show.id}/seasons", headers=headers)
    assert season_list.status_code == 200
    assert len(season_list.json()) == 2

    season = await integration_client.get(f"/shows/{show.id}/seasons/{season_one.id}", headers=headers)
    assert season.status_code == 200
    assert season.json()["show_id"] == show.id

    episode_list = await integration_client.get(f"/shows/{show.id}/seasons/{season_one.id}/episodes", headers=headers)
    assert episode_list.status_code == 200
    assert len(episode_list.json()) == 3

    episode = season_one_episodes[0]
    viewed_before = await integration_client.get(
        f"/shows/{show.id}/seasons/{season_one.id}/episodes/{episode.id}/view",
        headers=headers,
    )
    assert viewed_before.status_code == 200
    assert viewed_before.json()["viewed"] is False

    viewed = await integration_client.post(
        f"/shows/{show.id}/seasons/{season_one.id}/episodes/{episode.id}/view",
        headers=headers,
    )
    assert viewed.status_code == 200
    assert viewed.json()["viewed"] is True

    viewed_after = await integration_client.get(
        f"/shows/{show.id}/seasons/{season_one.id}/episodes/{episode.id}/view",
        headers=headers,
    )
    assert viewed_after.status_code == 200
    assert viewed_after.json()["viewed"] is True

    undone = await integration_client.delete(
        f"/shows/{show.id}/seasons/{season_one.id}/episodes/{episode.id}/view",
        headers=headers,
    )
    assert undone.status_code == 200
    assert undone.json()["viewed"] is False


async def test_view_state_is_user_specific(integration_client, admin_headers, viewer_headers, show_data):
    show = show_data["show"]
    season_one = show_data["seasons_one"]
    episode = show_data["season_one_episodes"][0]

    marked = await integration_client.post(
        f"/shows/{show.id}/seasons/{season_one.id}/episodes/{episode.id}/view",
        headers=viewer_headers,
    )
    assert marked.status_code == 200
    assert marked.json()["viewed"] is True

    viewer_state = await integration_client.get(
        f"/shows/{show.id}/seasons/{season_one.id}/episodes/{episode.id}/view",
        headers=viewer_headers,
    )
    assert viewer_state.status_code == 200
    assert viewer_state.json()["viewed"] is True

    admin_state = await integration_client.get(
        f"/shows/{show.id}/seasons/{season_one.id}/episodes/{episode.id}/view",
        headers=admin_headers,
    )
    assert admin_state.status_code == 200
    assert admin_state.json()["viewed"] is False
