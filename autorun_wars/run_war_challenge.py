import argparse
import os
import subprocess
import logging
import sqlite3

from typing import List, Tuple, Dict
from typing import List
from os import listdir

from website.settings import DATABASES

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DATABASE_ADDRESS = DATABASES["default"]

ENGINE_JAR = 'corewars8086-4.0.0-cli-support.jar'
AUTO_COREWARS_CLASS = 'il.co.codeguru.corewars8086.AutoCoreWars'


def parse_game_results(game_results: str) -> Dict[str, float]:
    """
    Extracts the relevant information out of the engine's output.

    @param game_results: The game results as the engine supplies them.
    @return: A dictionary containing the teams name and the result it scored.
    """
    result_lines = game_results.decode('ascii').split('\n')
    existing_result_lines = filter(lambda line: line != '', result_lines)
    team_to_total_score_tuples = map(log_and_parse_result_line, existing_result_lines)
    return {game_result[0]: game_result[1] for game_result in team_to_total_score_tuples}


def log_and_parse_result_line(result_line: str) -> Tuple[str, float]:
    """
    Parses the results of a single game while logging it to the console.

    @param result_line: The single line result representing the outcome of a game
    @return: The name of the team and the score as a tuple
    """
    logger.debug("Parsing: '{}'".format(result_line))
    return parse_result_line(result_line)


def parse_result_line(result_line: str) -> Tuple[str, float]:
    """
    Parses the result of the execution of a single game.
    Each result line starts like:
    ksdr,151.16666,ksdr1,151.16666,ksdr2,0.0

    @param result_line: The single line result representing the outcome of a game
    @return: The name of the team and the score as a tuple
    """
    team_info_results = result_line.split(',')
    if len(team_info_results) == 4:
        teamname, total_score, survivor1, survivor1_score = team_info_results
    elif len(team_info_results) == 6:
        teamname, total_score, survivor1, survivor1_score, survivor2, survivor2_score = team_info_results
    else:
        raise ValueError(f"Can't parse result '{result_line}'")
    return teamname, total_score


def insert_games_results_to_db(team_scores: Dict[str, float]) -> None:
    """
    Updates the matching profile's scores according to the games results.

    @param team_scores: The score of each team, by the teams name.
    """
    connection = sqlite3.connect(DATABASE_ADDRESS["NAME"])
    cursor = connection.cursor()
    for team_name, game_score in team_scores:
        update_query = "UPDATE codeguru_profile SET score = score + ? WHERE group = ?"
        cursor.execute(update_query, (game_score, team_name))
    connection.commit()


def get_survivor_name(survivordir):
    survivors_in_dir = listdir(survivordir)
    # Survivors in a directory have this pattern:
    #   Must have 1 or 2 survivors only
    #   if 2 survivors - the are named "teamname1" and "teamname2"
    if len(survivors_in_dir) == 1:
        return survivors_in_dir[0]
    elif len(survivors_in_dir) == 2:
        survivor1, survivor2 = survivors_in_dir
        return survivor1[:-1]
    else:
        raise ValueError(
            "Dir has {} survivors which is not supported".format(len(survivors_in_dir)))


def run_game(survivors_dirs: List[str], system_survivors_dir: str, num_wars: int):
    if not os.path.exists('./survivors'):
        os.mkdir('./survivors') # ./survivors dir must exist else the engine won't run
    engine_flags = []
    for surv_dir in survivors_dirs:
        engine_flags.append('-add {}'.format(surv_dir))
    engine_flags.append('-add {}'.format(system_survivors_dir))
    engine_flags.append('-wars {}'.format(num_wars))
    command = "echo '{flags} \\n'| java -cp {engine} {runclass}".format(
        flags=' \\n '.join(engine_flags), engine=ENGINE_JAR, runclass=AUTO_COREWARS_CLASS)
    logger.info("Running {}".format(command))
    game_results = subprocess.check_output(
        command, shell=True, stderr=subprocess.DEVNULL)
    logger.debug("Results: {}".format(game_results))
    teamscores = parse_game_results(game_results)
    logger.debug(teamscores)
    return teamscores


def main(survivors_dirs: List[str], system_survivors_dir: str, num_wars: int,  update_db: bool):
    # For each survivor we got, we want to run against the system survivors,
    # And print the result
    for survivors_dir in survivors_dirs:
        survivor_name = get_survivor_name(survivors_dir)
        logging.debug(f"Running game for '{survivor_name}")
        team_scores = run_game([survivors_dir], system_survivors_dir, num_wars)
        if update_db:
            insert_games_results_to_db(team_scores)
        print("{}: {}".format(survivor_name, team_scores[survivor_name]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--survivor-dir', type=str, nargs='+',
                        help='Survivor dirs to run against. For each dir run a seperate competition against the system.', required=True)
    parser.add_argument('--system-survivors-dir', type=str,
                        help='System survivors that will participate in every game', required=True)
    parser.add_argument('--wars', type=int,
                        help='Number of wars to run in each competition', required=False, default=500)
    parser.add_argument('--update-db', action="store_true",
                        help='Whether to update the results in the profiles in the databse. ', required=False)

    args = parser.parse_args()
    main(args.survivor_dir, args.system_survivors_dir, args.wars, args.update_db)
