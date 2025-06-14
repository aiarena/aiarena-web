import pytest
from playwright.sync_api import FilePayload, Page, expect

from ..base import BrowserHelper


pytestmark = [pytest.mark.playwright]


def test_spa_redirect_to_django_login_if_no_user(page: Page, bh: BrowserHelper):
    page.goto(bh.reverse("dashboard_bots"))
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def test_spa_nav_to_django(page: Page, bh: BrowserHelper):
    page.goto(bh.reverse("dashboard_bots"))
    page.get_by_role("link", name="Home").click()
    expect(page.locator("text=Welcome to AI Arena!")).to_be_visible()


def test_spa_userbots_shows_create_bot(page: Page, bh: BrowserHelper, user, admin_user, all_bot_races):
    bh.log_in(user, page)

    page.goto(bh.reverse("dashboard_bots"))
    expect(page.get_by_role("button", name="Upload Agent")).to_be_visible()


def test_spa_userbots_shows_active_competition_participations(
    page: Page,
    bh: BrowserHelper,
    user,
    admin_user,
    python_zip_file,
    all_bot_races,
):
    generated_python_file = python_zip_file()
    bh.log_in(user, page)

    page.goto(bh.reverse("dashboard_bots"))
    expect(page.get_by_role("button", name="Upload Agent")).to_be_visible()
    page.get_by_role("button", name="Upload Agent").click()

    # Fill in the form
    page.get_by_label("Name:").fill("robo-her0")
    expect(page.get_by_label("Name:")).to_have_value("robo-her0")

    page.get_by_label("Agent ZIP:").set_input_files(
        FilePayload(
            name=generated_python_file.name,
            mimeType=generated_python_file.content_type,
            buffer=generated_python_file.read(),
        )
    )
    page.get_by_label("Agent Data:").check()
    expect(page.get_by_label("Agent Data:")).to_be_checked()

    page.get_by_label("Plays Race:").select_option("Protoss")
    expect(page.get_by_label("Plays Race:")).to_have_value("P")

    page.get_by_label("Type:").select_option("python")
    expect(page.get_by_label("Type:")).to_have_value("python")

    page.locator("form").get_by_role("button", name="Upload Agent").click()

    expect(page.locator("form").get_by_role("button", name="Upload Agent")).not_to_be_visible()
    expect(page.get_by_text("Agent Uploaded Successfully!")).to_be_visible()
    expect(page.get_by_text("robo-her0")).to_be_visible()


@pytest.mark.parametrize(
    "map_type",
    ["Specific Map", "Map Pool"],
)
def test_request_match_form(
    page: Page,
    bh: BrowserHelper,
    user,
    bot,
    other_bot,
    map,
    map_pool,
    map_type,
):
    bh.log_in(user, page)
    page.goto(bh.reverse("dashboard_match_requests"))

    page.get_by_role("button", name="Request New Match").click()

    page.locator("#agent1-name").click()
    page.get_by_role("option", name=bot.name, exact=True).click()

    page.locator("#agent2-name").click()
    page.get_by_role("option", name=other_bot.name, exact=True).click()

    # Mode switch button
    page.get_by_role("button", name=map_type).click()

    # Combobox
    page.get_by_label(map_type).click()
    page.get_by_role(
        "option",
        name=map.name if map_type == "Specific Map" else map_pool.name,
    ).click()

    page.get_by_role("button", name="Request Match").click()

    # Add when we get match request graphql update to work
    # match = page.get_by_role("listitem").filter(has_text="Queued")
    # expect(match).to_be_visible()
    # expect(match.get_by_role("cell", name="Match status: Queued")).to_be_visible()
    # expect(match.get_by_role("cell", name=f"View bot profile for {bot.name}")).to_be_visible()
    # expect(match.get_by_role("cell", name=f"View bot profile for {other_bot.name}")).to_be_visible()
    # expect(match.get_by_role("cell", name=f"Map: {map.name}")).to_be_visible()
