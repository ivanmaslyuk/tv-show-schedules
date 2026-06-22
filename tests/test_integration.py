import pytest


pytestmark = pytest.mark.integration


async def test_signup_first_user_becomes_admin(integration_client):
    response = await integration_client.post(
        "/auth/signup", json={"email": "admin@example.com", "password": "secret123"}
    )
    assert response.status_code == 201
    assert response.json()["is_admin"] is True


async def test_admin_can_create_show_with_a_season_and_an_episode(integration_client, admin_headers):
    headers = admin_headers

    show_response = await integration_client.post(
        "/shows",
        headers=headers,
        json={"title": "New Show", "release_date": "2026-06-20"},
    )
    assert show_response.status_code == 201
    show = show_response.json()

    season_response = await integration_client.post(
        f"/shows/{show['id']}/seasons",
        headers=headers,
        json={"number": 1, "release_date": "2026-06-21"},
    )
    assert season_response.status_code == 201
    assert season_response.json()["show_id"] == show["id"]
    season = season_response.json()

    episode_response = await integration_client.post(
        f"/shows/{show['id']}/seasons/{season['id']}/episodes",
        headers=headers,
        json={"title": "Pilot", "number": 1, "release_date": "2026-06-22"},
    )
    assert episode_response.status_code == 201
    assert episode_response.json()["season_id"] == season["id"]


async def test_viewer_cant_create_show(integration_client, viewer_headers):
    response = await integration_client.post(
        "/shows",
        headers=viewer_headers,
        json={"title": "Denied Show", "release_date": "2026-06-20"},
    )
    assert response.status_code == 403


async def test_viewer_cant_add_a_season_to_an_existing_show(integration_client, viewer_headers, show_data):
    show = show_data["show"]

    response = await integration_client.post(
        f"/shows/{show.id}/seasons",
        headers=viewer_headers,
        json={"number": show_data["seasons"] + 1, "release_date": "2026-03-01"},
    )
    assert response.status_code == 403


async def test_viewer_cant_add_an_episode_to_an_existing_season(integration_client, viewer_headers, show_data):
    show = show_data["show"]
    season_one = show_data["seasons_one"]

    response = await integration_client.post(
        f"/shows/{show.id}/seasons/{season_one.id}/episodes",
        headers=viewer_headers,
        json={
            "title": "Denied Episode",
            "number": len(show_data["season_one_episodes"]) + 1,
            "release_date": "2026-03-02",
        },
    )
    assert response.status_code == 403


async def test_anonymous_user_cant_watch_a_show(integration_client, show_data):
    show = show_data["show"]

    response = await integration_client.post(f"/shows/{show.id}/watch")
    assert response.status_code == 401


async def test_viewer_user_can_watch_and_unwatch_a_show(integration_client, viewer_headers, show_data):
    show = show_data["show"]

    watched = await integration_client.post(f"/shows/{show.id}/watch", headers=viewer_headers)
    assert watched.status_code == 200
    assert watched.json() == {"watching": True}

    watched_state = await integration_client.get(f"/shows/{show.id}/watch", headers=viewer_headers)
    assert watched_state.status_code == 200
    assert watched_state.json() == {"watching": True}

    unwatched = await integration_client.delete(f"/shows/{show.id}/watch", headers=viewer_headers)
    assert unwatched.status_code == 200
    assert unwatched.json() == {"watching": False}

    unwatched_state = await integration_client.get(f"/shows/{show.id}/watch", headers=viewer_headers)
    assert unwatched_state.status_code == 200
    assert unwatched_state.json() == {"watching": False}


async def test_show_watch_state_is_user_specific(integration_client, admin_headers, viewer_headers, show_data):
    show = show_data["show"]

    watched = await integration_client.post(f"/shows/{show.id}/watch", headers=viewer_headers)
    assert watched.status_code == 200
    assert watched.json()["watching"] is True

    viewer_state = await integration_client.get(f"/shows/{show.id}/watch", headers=viewer_headers)
    assert viewer_state.status_code == 200
    assert viewer_state.json()["watching"] is True

    admin_state = await integration_client.get(f"/shows/{show.id}/watch", headers=admin_headers)
    assert admin_state.status_code == 200
    assert admin_state.json()["watching"] is False


async def test_anonymous_user_cant_list_upcoming_episodes(integration_client):
    response = await integration_client.get("/shows/upcoming")
    assert response.status_code == 401


async def test_upcoming_episodes_are_watched_user_specific_and_ordered(
    integration_client, viewer_headers, upcoming_show_data
):
    watched_soonest = upcoming_show_data["watched_soonest"]
    watched_after_past = upcoming_show_data["watched_after_past"]
    watched_later = upcoming_show_data["watched_later"]
    unwatched = upcoming_show_data["unwatched"]

    for watched_show in [watched_later, watched_soonest, watched_after_past]:
        response = await integration_client.post(f"/shows/{watched_show['show'].id}/watch", headers=viewer_headers)
        assert response.status_code == 200
        assert response.json()["watching"] is True

    upcoming = await integration_client.get("/shows/upcoming", headers=viewer_headers)
    assert upcoming.status_code == 200
    assert upcoming.json() == [
        {
            "show": {
                "id": watched_soonest["show"].id,
                "title": watched_soonest["show"].title,
                "release_date": watched_soonest["show"].release_date.isoformat(),
            },
            "upcoming_episode": {
                "id": watched_soonest["episodes"][0].id,
                "season_id": watched_soonest["season"].id,
                "title": watched_soonest["episodes"][0].title,
                "number": watched_soonest["episodes"][0].number,
                "release_date": watched_soonest["episodes"][0].release_date.isoformat(),
            },
        },
        {
            "show": {
                "id": watched_after_past["show"].id,
                "title": watched_after_past["show"].title,
                "release_date": watched_after_past["show"].release_date.isoformat(),
            },
            "upcoming_episode": {
                "id": watched_after_past["episodes"][1].id,
                "season_id": watched_after_past["season"].id,
                "title": watched_after_past["episodes"][1].title,
                "number": watched_after_past["episodes"][1].number,
                "release_date": watched_after_past["episodes"][1].release_date.isoformat(),
            },
        },
        {
            "show": {
                "id": watched_later["show"].id,
                "title": watched_later["show"].title,
                "release_date": watched_later["show"].release_date.isoformat(),
            },
            "upcoming_episode": {
                "id": watched_later["episodes"][0].id,
                "season_id": watched_later["season"].id,
                "title": watched_later["episodes"][0].title,
                "number": watched_later["episodes"][0].number,
                "release_date": watched_later["episodes"][0].release_date.isoformat(),
            },
        },
    ]
    assert all(item["show"]["id"] != unwatched["show"].id for item in upcoming.json())


async def test_anonymous_user_cant_view_an_episode(integration_client, show_data):
    show = show_data["show"]
    season_one = show_data["seasons_one"]
    episode = show_data["season_one_episodes"][0]

    response = await integration_client.post(
        f"/shows/{show.id}/seasons/{season_one.id}/episodes/{episode.id}/view",
    )
    assert response.status_code == 401


async def test_viewer_user_can_view_an_episode(integration_client, viewer_headers, show_data):
    show = show_data["show"]
    season_one = show_data["seasons_one"]
    episode = show_data["season_one_episodes"][0]

    response = await integration_client.post(
        f"/shows/{show.id}/seasons/{season_one.id}/episodes/{episode.id}/view",
        headers=viewer_headers,
    )
    assert response.status_code == 200
    assert response.json()["viewed"] is True


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
