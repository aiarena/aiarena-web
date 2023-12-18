import requests


my_bot_id = 1  # You can obtain this from the URL of your bot's page: https://aiarena.net/bots/<bot_id>/
token = "<token here>"  # insert the token you received from your token page: https://aiarena.net/profile/token/
my_bot_zip_file = "./bot_zip.zip"  # the file path to your bot zip
my_bot_data_zip_file = "./bot_data.zip"  # the file path to your bot's new data zip
my_bot_article_content = """  
    # My bot
    This is my bot. It is very good.
"""  # this content appears on your bot's page, under the "Biography" header
my_bot_zip_publicly_downloadable = True  # setting this to False will stop other users downloading your bot zip
my_bot_data_publicly_downloadable = True  # setting this to False will stop other users downloading your bot data


auth = {"Authorization": f"Token {token}"}
with open(my_bot_zip_file, "rb") as bot_zip, open(my_bot_data_zip_file, "rb") as bot_data:
    response = requests.patch(
        f"https://aiarena.net/api/bots/{my_bot_id}/",
        headers=auth,
        data={
            "bot_zip_publicly_downloadable": my_bot_zip_publicly_downloadable,
            "bot_data_publicly_downloadable": my_bot_data_publicly_downloadable,
            "wiki_article_content": my_bot_article_content,
        },
        files={
            "bot_zip": bot_zip,
            "bot_data": bot_data,
        },
    )
    print(response.json())
