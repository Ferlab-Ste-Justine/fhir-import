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
SAMPLE_RANGE_NAME = 'FMH!A:E'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        fmh_model = requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/familyMemberHistory.json').json()
        row_parser = RowParser(values[0])
        connection = get_connection(args)
        with db_transaction(connection):
            for row in values[1:]:
                fmh_row = row_parser.as_dict(row)
                fmh = copy.deepcopy(fmh_model)

                fmh['id'] = fmh_row['id']
                fmh['status'] = fmh_row['status']
                fmh['patient']['reference'] = f"Patient/{fmh_row['patient']}"
                fmh['date'] = fmh_row['date']
                fmh['note'][0]['text'] = fmh_row['note']

                fmh_json = json.dumps(fmh, ensure_ascii=False)
                cursor = connection.cursor()
                insert_query = "insert into familymemberhistory (id, txid, resource, status) values (%s, 0, %s, 'created')"
                cursor.execute(insert_query, (fmh['id'], fmh_json))


if __name__ == '__main__':
    main(parse_args())
