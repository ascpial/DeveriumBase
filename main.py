from __future__ import annotations
import argparse
import pathlib

from src import Configuration, DeveriumBot

def main():
    parser = argparse.ArgumentParser()
    # registering args
    parser.add_argument(
        '--instance', '-i',
        help="select the configuration you want to use",
    )
    parser.add_argument(
        '--configuration', '-c',
        help="select the configuration file location",
        type=pathlib.Path,
        default="./data/configuration.json",
    )
    args = parser.parse_args()
    
    # loading the configuration using the specified args
    config = Configuration(
        file=args.configuration,
        instance=args.instance,
    )
    
    # creating the instance of the bot
    bot = DeveriumBot(
        config,
    )
    
    # running the bot
    bot.run()

if __name__ == "__main__":
    main()