import logging
import multiprocessing
import sys
from time import sleep

from aiarena.api.arenaclient.integration_tests.mock_ac import MockArenaClient

from multiprocessing import Process

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

NUM_ACS = 10
NUM_MATCHES_TO_RUN = 100
API_URL = "http://127.0.0.1:8000"
AC_SLEEP_TIME = 0.1

def run_ac(ac_id, num_matches, lock):
    ac_id = str(ac_id)
    ac_token = ac_id

    logger.info(f"Creating AC {ac_id}")
    ac = MockArenaClient(ac_id=ac_id, webserver_url=API_URL, api_token=ac_token, working_dir=f"./{ac_id}/")

    while True:
        with lock: # reserve a match for this AC if there are any left to play
            if num_matches.value >= NUM_MATCHES_TO_RUN:
                break
            num_matches.value += 1
            logger.info(f"Starting match {num_matches.value} using AC {ac_id}")

        # don't quit until this match is run
        while not ac.run_a_match():
            logger.debug(f"AC {ac_id} is sleeping")
            sleep(AC_SLEEP_TIME)


if __name__ == '__main__':
    processes = []
    num_matches = multiprocessing.Value('i', 0)
    lock = multiprocessing.Lock()

    for ac_id in range(NUM_ACS):
        processes.append(Process(target=run_ac, args=(ac_id, num_matches, lock)))

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    logger.info(f"Total matches played: {num_matches.value}")

