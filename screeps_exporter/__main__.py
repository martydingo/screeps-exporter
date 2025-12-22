from screeps_exporter import screeps_exporter
import argparse

argSetup = argparse.ArgumentParser()

argSetup.add_argument(
    "-c", "--config", required=True, help="The path to the yaml configuration file"
)

args = argSetup.parse_args()

screeps_exporter(configPath=args.config)
