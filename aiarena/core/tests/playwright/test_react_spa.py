import pytest
from playwright.sync_api import FilePayload, Page, expect

from ..base import BrowserHelper


pytestmark = [pytest.mark.playwright]


def test_spa_redirect_to_django_login_if_no_user(page: Page, bh: BrowserHelper):
    page.goto(bh.reverse("dashboard_bots"))
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def test_spa(page: Page, bh: BrowserHelper):
    page.goto(bh.live_server.url)
    expect(page.locator("text=Welcome to AI Arena!")).to_be_visible()


def test_spa_userbots_shows_create_bot(page: Page, bh: BrowserHelper, user, admin_user, all_bot_races):
    bh.log_in(user, page)

    page.goto(bh.reverse("dashboard_bots"))
    expect(page.get_by_role("button", name="Upload Bot")).to_be_visible()


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
    expect(page.get_by_role("button", name="Upload Bot")).to_be_visible()
    page.get_by_role("button", name="Upload Bot").click()

    # Fill in the form
    page.get_by_label("Name:").fill("robo-her0")
    expect(page.get_by_label("Name:")).to_have_value("robo-her0")

    page.get_by_label("Bot ZIP:").set_input_files(
        FilePayload(
            name=generated_python_file.name,
            mimeType=generated_python_file.content_type,
            buffer=generated_python_file.read(),
        )
    )
    page.get_by_label("Bot Data:").check()
    expect(page.get_by_label("Bot Data:")).to_be_checked()

    page.get_by_label("Plays Race:").select_option("Protoss")
    expect(page.get_by_label("Plays Race:")).to_have_value("P")

    page.get_by_label("Type:").select_option("python")
    expect(page.get_by_label("Type:")).to_have_value("python")

    page.locator("form").get_by_role("button", name="Upload Bot").click()

    expect(page.locator("form").get_by_role("button", name="Upload Bot")).not_to_be_visible()
    expect(page.get_by_text("Bot Uploaded Successfully!")).to_be_visible()
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

    page.locator("#bot-name").click()
    page.get_by_role("option", name=bot.name, exact=True).click()

    page.locator("#opponent-name").click()
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

    # Test updating the list
    row = page.get_by_role("row").filter(has_text="In Queue").first
    started_cell = row.get_by_role("cell", name="In Queue").first
    result_cell = row.get_by_role("cell", name="In Queue").nth(1)

    expect(started_cell).to_be_visible()
    expect(result_cell).to_be_visible()
    expect(row.get_by_text(bot.name, exact=True)).to_be_visible()
    expect(row.get_by_text(other_bot.name, exact=True)).to_be_visible()
    expect(row.get_by_text(map.name, exact=True)).to_be_visible()
