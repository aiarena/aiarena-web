import argparse
import logging
import multiprocessing
import sys
from multiprocessing import Process
from time import sleep

from aiarena.api.arenaclient.integration_tests.mock_ac import MockArenaClient


logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def retrieve_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--num_acs", type=int, default=10)
    arg_parser.add_argument("--num_matches_to_run", type=int, default=1000)
    arg_parser.add_argument("--api_url", type=str, default="http://127.0.0.1:8000")
    arg_parser.add_argument("--ac_sleep_time", type=float, default=0.0)
    return arg_parser.parse_args()


def run_ac(ac_id, num_matches, lock, total_matches_to_run, api_url, ac_sleep_time):
    ac_id = str(ac_id)
    ac_token = ac_id

    logger.info(f"AC {ac_id} - Starting")
    ac = MockArenaClient(ac_id=ac_id, webserver_url=api_url, api_token=ac_token, working_dir=f"./tmp/{ac_id}/")

    while True:
        with lock:  # reserve a match for this AC if there are any left to play
            if num_matches.value >= total_matches_to_run:
                logger.info(f"AC {ac_id} - Exiting: no more matches to run.")
                break

            num_matches.value += 1
            logger.info(f"AC {ac_id} - Starting match {num_matches.value}")
            logger.info(f"AC {ac_id} - {total_matches_to_run - num_matches.value} matches left to run")

        # don't quit until this match is run
        while not ac.run_a_match():
            logger.debug(f"AC {ac_id} is sleeping")
            sleep(ac_sleep_time)


if __name__ == "__main__":
    args = retrieve_args()
    processes = []
    matches_played_count = multiprocessing.Value("i", 0)
    lock = multiprocessing.Lock()

    for ac_id in range(args.num_acs):
        processes.append(
            Process(
                target=run_ac,
                args=(ac_id, matches_played_count, lock, args.num_matches_to_run, args.api_url, args.ac_sleep_time),
            )
        )

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    logger.info(f"Total matches played: {matches_played_count.value}")
