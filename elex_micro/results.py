#!/usr/bin/env python

import argparse
import cProfile

import ujson

import utils


def main():
    parser = argparse.ArgumentParser(description='Return AP Election data')
    parser.add_argument('-d', '--file', action='store')
    parser.add_argument('--races', action='store')
    parser.add_argument('-o', '--output', action='store')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--csv', action='store_true')
    parser.add_argument('--tsv', action='store_true')

    args = parser.parse_args()

    if args.file:

        race_ids = None
        if args.races:
            race_ids = args.races.split(',')

        electiondate, races = utils.open_file(args.file, race_ids)
        payload = utils.load_results(electiondate, races)

        if args.json:
            utils.output_json(payload)

        elif args.output and args.output == 'json':
            utils.output_json(payload)

        elif args.output and args.output == 'tsv':
            utils.output_tsv(payload)

        else:
            utils.output_csv(payload)

    else:
        print """Please specify a data file with -d '/path/to/json/file.json'"""

if __name__ == "__main__":
    # cProfile.run('main()')
    main()
