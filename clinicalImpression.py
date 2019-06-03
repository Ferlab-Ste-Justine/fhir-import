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
SAMPLE_RANGE_NAME = 'clinicalImpression!A:J'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        clinical_impression_model = requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/clinicalImpression.json').json()
        row_parser = RowParser(values[0])
        connection = get_connection(args)
        with db_transaction(connection):
            for row in values[1:]:
                clinical_impression_row = row_parser.as_dict(row)
                clinical_impression = copy.deepcopy(clinical_impression_model)

                clinical_impression['id'] = clinical_impression_row['id']
                clinical_impression['status'] = clinical_impression_row['status']
                clinical_impression['effectiveDateTime'] = clinical_impression_row['effectiveDateTime']
                clinical_impression['subject']['reference'] = f"Patient/{clinical_impression_row['subject']}"
                clinical_impression['assessor']['reference'] = f"PractitionerRole/{clinical_impression_row['assessor']}"
                clinical_impression['extension'][0]['valueAge']['value'] = clinical_impression_row['valueAge']
                clinical_impression['investigation'][0]['item'] = []
                for r in row[5:9]:
                    clinical_impression['investigation'][0]['item'].extend([{'reference': r}])

                clinical_impression_json = json.dumps(clinical_impression, ensure_ascii=False)
                cursor = connection.cursor()
                insert_query = "insert into clinicalImpression (id, txid, resource, status) values (%s, 0, %s, 'created')"
                cursor.execute(insert_query, (clinical_impression['id'], clinical_impression_json))


if __name__ == '__main__':
    main(parse_args())
