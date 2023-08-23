import requests

bot_id = 1  # insert bot id
token = "<token here>"  # insert token you received from admin
auth = {"Authorization": f"Token {token}"}

if __name__ == "__main__":
    with open("./my_bot.zip", "rb") as f:
        response = requests.patch(
            f"https://aiarena.net/api/bots/{bot_id}/",
            headers=auth,
            data={
                "bot_zip_publicly_downloadable": False,
                "bot_data_publicly_downloadable": False,
            },
            files={
                "bot_zip": f,
            },
        )
        print(response.json())
