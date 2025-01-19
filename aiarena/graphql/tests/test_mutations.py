from aiarena.core.models import Bot, WebsiteUser
from aiarena.core.models.bot_race import BotRace

"""
Example test cases for mutations.
Please update as needed.
"""

def test_update_bot_success():
    """
    Test updating a bot with all fields set to True.
    """
    # Create required objects
    user = WebsiteUser.objects.create_user(username="test_user", password="test123")
    BotRace.create_all_races()
    bot = Bot.objects.create(
        user=user,
        name="My Bot",
        bot_zip_publicly_downloadable=False,  # Should change False -> True in this test
        bot_data_enabled=False,               # Should change False -> True in this test
        bot_data_publicly_downloadable=False, # Should change False -> True in this test
        plays_race=BotRace.terran()
    )
    
    # TODO: Prepare and submit mutation under user's credentials
    
    # TODO: assert no errors occurred
    
    # Verify bot was updated correctly
    bot.refresh_from_db()
    assert bot.bot_zip_publicly_downloadable == True
    assert bot.bot_data_enabled == True
    assert bot.bot_data_publicly_downloadable == True



def test_update_bot_unauthorized():
    """
    Test updating a bot that does not belong to the user.
    """
    # Create required objects
    owner = WebsiteUser.objects.create_user(username="owner", password="test123")
    other_user = WebsiteUser.objects.create_user(username="other", password="test123")
    BotRace.create_all_races()
    bot = Bot.objects.create(
        user=owner,
        name="My Bot",
        bot_zip_publicly_downloadable=False, # Should NOT change False -> True in this test
        plays_race=BotRace.terran()
    )
    
    # TODO: Prepare and submit mutation under other_user's credentials with bot.bot_zip_publicly_downloadable == True
    
    # todo: Assert error was returned - "This is not your bot"
    
    # Optionally, verify bot was not updated
    bot.refresh_from_db()
    assert bot.bot_zip_publicly_downloadable == False

def test_update_bot_unauthenticated():
    """
    Test updating a bot without being authenticated.
    """
    # Create test user and bot
    user = WebsiteUser.objects.create_user(username="test_user", password="test123")
    BotRace.create_all_races()
    bot = Bot.objects.create(
        user=user,
        name="My Bot",
        bot_zip_publicly_downloadable=False, # Should NOT change False -> True in this test
        plays_race=BotRace.terran()
    )
    
    # TODO: Prepare and submit unauthenticated mutation with bot.bot_zip_publicly_downloadable == True

    # todo: Assert error was returned - "You are not signed in"
    
    # Optionally, verify bot was not updated
    bot.refresh_from_db()
    assert bot.bot_zip_publicly_downloadable == False
