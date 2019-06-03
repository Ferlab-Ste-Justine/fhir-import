import copy
import json

import requests

from argsutil import parse_args
from db import db_transaction, get_connection
# If modifying these scopes, delete the file token.pickle.
from row_parser import RowParser
from spreadsheet import spreadsheet

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_RANGE_NAME = 'serviceRequest!A1:H90'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        service_request_model = requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/serviceRequest.json').json()
        row_parser = RowParser(values[0])
        connection = get_connection(args)
        with db_transaction(connection):
            for row in values[1:]:
                service_request_row = row_parser.as_dict(row)
                service_request = copy.deepcopy(service_request_model)

                service_request['id'] = service_request_row['id']
                service_request['status'] = service_request_row['status']
                service_request['authoredOn'] = service_request_row['authoredOn']
                service_request['code']['text'] = service_request_row['code.text']
                service_request['subject']['reference'] = f"Patient/{service_request_row['subject']}"
                service_request['requester']['reference'] = f"PractitionerRole/{service_request_row['requester']}"
                service_request['specimen'][0]['reference'] = f"Specimen/{service_request_row['specimen']}"
                service_request['extension'][0]['valueReference']['reference'] = \
                    f"ClinicalImpression/{service_request_row['extension.valueReference']}"

                service_request_json = json.dumps(service_request, ensure_ascii=False)
                cursor = connection.cursor()
                insert_query = "insert into servicerequest (id, txid, resource, status) values (%s, 0, %s, 'created')"
                cursor.execute(insert_query, (service_request['id'], service_request_json))


if __name__ == '__main__':
    main(parse_args())
