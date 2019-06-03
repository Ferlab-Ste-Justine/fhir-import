import copy
import json

import requests

# If modifying these scopes, delete the file token.pickle.
from argsutil import parse_args
from db import db_transaction, get_connection
from spreadsheet import spreadsheet

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_RANGE_NAME = 'group!A2:K'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        group_model = requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/group.json').json()
        connection = get_connection(args)
        with db_transaction(connection):
            for row in values[1:]:
                group = copy.deepcopy(group_model)

                group['id'] = row[0]
                group['member'] = []
                for r in row[1:]:
                    group['member'].extend([{'entity': {'reference': f"Patient/{r}"}}])

                group_json = json.dumps(group, ensure_ascii=False)
                cursor = connection.cursor()
                insert_query = 'insert into "group" (id, txid, resource, status) values (%s, 0, %s, \'created\')'
                cursor.execute(insert_query, (group['id'], group_json))


if __name__ == '__main__':
    main(parse_args())
