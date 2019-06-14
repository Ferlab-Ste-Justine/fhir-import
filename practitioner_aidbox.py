import copy
import json

import requests

# If modifying these scopes, delete the file token.pickle.
from argsutil import parse_args_aidbox
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
            practitioner_json = json.dumps(practitioner)
            response = requests.put(f"{args.url}/fhir/Practitioner/{practitioner['id']}", data=practitioner_json,
                         headers={'Authorization': f"Basic {args.token}", "Content-Type": "application/json"})
            if response.status_code not in (201, 200):
                raise Exception(f'Aidobox did not return status code 201, status={response.status_code} \ntext={response.text} \nparticipant={practitioner_json}')

if __name__ == '__main__':
    main(parse_args_aidbox())
