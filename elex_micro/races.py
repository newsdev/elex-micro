#!/usr/bin/env python

import argparse

import ujson

import utils


def main():
    parser = argparse.ArgumentParser(description='Return AP Election data')
    parser.add_argument('-d', '--file', action='store')
    parser.add_argument('--races', action='store')
    parser.add_argument('-o', '--output', action='store')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--csv', action='store_true')

    args = parser.parse_args()

    if args.file:

        race_ids = None
        if args.races:
            race_ids = args.races.split(',')

        with open(args.file, 'r') as readfile:
            if race_ids:
                races = [r for r in ujson.loads(readfile.read())['races'] if r in race_ids]
            else:
                races = ujson.loads(readfile.read())['races']

        payload = utils.load_races(races)

        if args.json:
            utils.output_json(payload)

        elif args.output and args.output == 'json':
                utils.output_json(payload)
        else:
            utils.output_csv(payload)

    else:
        print """Please specify a data file with -d '/path/to/json/file.json'"""

if __name__ == "__main__":
    main()
