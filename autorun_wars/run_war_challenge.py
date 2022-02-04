import argparse
from os import listdir
import os
from re import sub
import subprocess
from typing import List
import logging
logging.basicConfig(level=logging.DEBUG)


logger = logging.getLogger(__name__)

ENGINE_JAR = 'corewars8086-4.0.0-cli-support.jar'
AUTO_COREWARS_CLASS = 'il.co.codeguru.corewars8086.AutoCoreWars'

def parse_game_results(game_results: str):
    team_to_total_score = dict()
    for line in game_results.decode('ascii').split('\n'):
        # each result line starts like:
        #   ksdr,151.16666,ksdr1,151.16666,ksdr2,0.0
        if line == '':
            continue
        logger.debug("Parsing: '{}'".format(line))
        team_info_results = line.split(',')
        if len(team_info_results) == 4:
            teamname, total_score, survivor1, survivor1_score = line.split(',')
        elif len(team_info_results) == 6:
            teamname, total_score, survivor1, survivor1_score, survivor2, survivor2_score = line.split(
                ',')
        else:
            raise ValueError(f"Can't parse result '{line}'")
        team_to_total_score[teamname] = float(total_score)
    return team_to_total_score


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


def main(survivors_dirs: List[str], system_survivors_dir: str, num_wars: int):
    # For each survivor we got, we want to run against the system survivors,
    # And print the result
    for survivors_dir in survivors_dirs:
        survivor_name = get_survivor_name(survivors_dir)
        logging.debug(f"Running game for '{survivor_name}")
        results = run_game([survivors_dir], system_survivors_dir, num_wars)
        print("{}: {}".format(survivor_name, results[survivor_name]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--survivor-dir', type=str, nargs='+',
                        help='Survivor dirs to run against. For each dir run a seperate competition against the system.', required=True)
    parser.add_argument('--system-survivors-dir', type=str,
                        help='System survivors that will participate in every game', required=True)
    parser.add_argument('--wars', type=int,
                        help='Number of wars to run in each competition', required=False, default=500)

    args = parser.parse_args()
    main(args.survivor_dir, args.system_survivors_dir, args.wars)
