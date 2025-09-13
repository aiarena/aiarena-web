import json
import os

import requests


# Download
bot_id = 0  # insert bot id
token = ""  # insert token you received from admin
file_path = "./replays/"  # insert file path
auth = {"Authorization": f"Token {token}"}

# requests.get(url).text returns a dictionary formatted as a string and we need dictionaries
response = requests.get(f"https://aiarena.net/api/match-participations/?bot={bot_id}", headers=auth)
assert response.status_code == 200, "Unexpected status_code returned from match-participations"
participation = json.loads(response.text)
for i in range(len(participation["results"])):
    print(f"Downloading match {participation['results'][i]['match']}")
    response = requests.get(
        f"https://aiarena.net/api/results/?match={participation['results'][i]['match']}", headers=auth
    )
    assert response.status_code == 200, "Unexpected status_code returned from results"
    match_details = json.loads(response.text)
    replay_file = match_details["results"][0]["replay_file"]
    if replay_file not in (None, "null"):
        replay = requests.get(replay_file, headers=auth)
        with open(os.path.join(file_path, str(participation["results"][i]["match"]) + ".SC2Replay"), "wb") as f:
            f.write(replay.content)
