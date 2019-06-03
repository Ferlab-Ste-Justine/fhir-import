import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Import data to postgres')
    parser.add_argument('-u', '--user', help='Postgres user', default='postgres')
    parser.add_argument('-p', '--password', help='Postgres password', default='postgres')
    parser.add_argument('-H', '--host', help='Postgres host', default='127.0.0.1')
    parser.add_argument('-P', '--port', help='Postgres port', default='5492')
    parser.add_argument('-s', '--schema', help='Postgres schema', default='clin_fhir')

    return parser.parse_args()
