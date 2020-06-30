import copy
import json

import requests

# If modifying these scopes, delete the file token.pickle.
from argsutil import parse_args_aidbox
from row_parser import RowParser
from spreadsheet import spreadsheet

import fhir_model

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_RANGE_NAME = 'practitioner!A1:G34'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        practitioner_model = fhir_model.get('practitioner.json')
        row_parser = RowParser(values[0][0:7])

        for row in values[1:]:
            practitioner_row = row_parser.as_dict(row)
            practitioner = copy.deepcopy(practitioner_model)

            practitioner['id'] = practitioner_row['id']
            name = practitioner['name'][0]
            name['family'] = practitioner_row['name.family']
            # name['prefix'] = [practitioner_row['name.prefix']]
            name['given'] = [practitioner_row['name.given']]
            md = practitioner_row['MD']
            if md != 'null':
                practitioner['identifier'][0]['value'] = md
            else:
                practitioner['identifier'].pop(0)

            prefix = practitioner_row['name.prefix']
            if prefix != 'null':
                name['prefix'] = [prefix]
            else:
                del name['prefix']

            suffix = practitioner_row['name.suffix']
            if suffix != 'null':
                name['suffix'] = [suffix]
            else:
                del name['suffix']

            practitioner_json = json.dumps(practitioner)
            response = requests.put(f"{args.url}/fhir/Practitioner/{practitioner['id']}", data=practitioner_json,
                         headers={'Authorization': f"Basic {args.token}", "Content-Type": "application/json"})
            if response.status_code not in (201, 200):
                raise Exception(f'Aidobox did not return status code 201, status={response.status_code} \ntext={response.text} \nparticipant={practitioner_json}')

if __name__ == '__main__':
    main(parse_args_aidbox())
