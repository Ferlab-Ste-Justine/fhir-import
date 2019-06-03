import copy
import json

import requests

# If modifying these scopes, delete the file token.pickle.
from argsutil import parse_args
from db import db_transaction, get_connection
from row_parser import RowParser
from spreadsheet import spreadsheet

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_RANGE_NAME = 'practitioner!A1:F34'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        practitioner_model = requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/practitioner.json').json()
        row_parser = RowParser(values[0][0:6])
        connection = get_connection(args)
        with db_transaction(connection):
            for row in values[1:]:
                practitioner_row = row_parser.as_dict(row[0:6])
                practitioner = copy.deepcopy(practitioner_model)

                practitioner['id'] = practitioner_row['id']
                name = practitioner['name'][0]
                name['family'] = practitioner_row['name.family']
                name['prefix'] = [practitioner_row['name.prefix']]
                md = practitioner_row['MD']
                if md != 'null':
                    practitioner['identifier'][0]['value'] = md
                else:
                    practitioner['identifier'].pop(0)
                practitioner_json = json.dumps(practitioner, ensure_ascii=False)
                cursor = connection.cursor()
                insert_query = "insert into practitioner (id, txid, resource, status) values (%s, 0, %s, 'created')"
                cursor.execute(insert_query, (practitioner['id'], practitioner_json))


if __name__ == '__main__':
    main(parse_args())
