import screeps_exporter, argparse

inputArgs = argparse.ArgumentParser()
inputArgs.add_argument(
    "--config", "-c", help="Path to config file", default="config.yml"
)
args = inputArgs.parse_args()
screeps_exporter.screeps_exporter(args.config)
