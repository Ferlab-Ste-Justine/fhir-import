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
SAMPLE_RANGE_NAME = 'specimen!A:F'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        specimen_model = requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/specimen.json').json()
        specimen_model.pop('parent')
        row_parser = RowParser(values[0])
        for row in values[1:]:
            specimen_row = row_parser.as_dict(row)
            specimen = copy.deepcopy(specimen_model)

            specimen['id'] = specimen_row['id']
            specimen['status'] = specimen_row['status']

            specimen['subject']['reference'] = f"Patient/{specimen_row['subject']}"
            specimen['request'][0]['reference'] = f"ServiceRequest/{specimen_row['request']}"
            specimen['container'][0]['identifier'][0]['value'] = specimen_row['container.identifier.value']

            specimen_json = json.dumps(specimen)
            response = requests.put(f"{args.url}/fhir/Specimen/{specimen['id']}", data=specimen_json,
                         headers={'Authorization': f"Basic {args.token}", "Content-Type": "application/json"})
            if response.status_code not in (201, 200):
                raise Exception(f'Aidobox did not return status code 201, status={response.status_code} \ntext={response.text} \nspecimen={specimen_json}')

if __name__ == '__main__':
    main(parse_args_aidbox())
