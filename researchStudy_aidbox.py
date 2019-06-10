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
SAMPLE_RANGE_NAME = 'researchStudy!A:I'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        study_model = requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/researchStudy.json').json()
        row_parser = RowParser(values[0])
        for row in values[1:]:
            study_row = row_parser.as_dict(row)
            study = copy.deepcopy(study_model)

            study['id'] = study_row['id']
            study['status'] = study_row['status']
            study['title'] = study_row['title']
            study['description'] = study_row['description']

            study['sponsor']['reference'] = f"Organization/{study_row['sponsor']}"
            study['principalInvestigator']['reference'] = f"Practitioner/{study_row['principalInvestigator']}"
            study['enrollment'][0]['reference'] = f"Group/{study_row['enrolement']}"
            study['period']['start'] = study_row['period.start']
            study['period']['end'] = study_row['period.end']

            study_json = json.dumps(study)
            response = requests.put(f"{args.url}/fhir/ResearchStudy/{study['id']}", data=study_json,
                         headers={'Authorization': f"Basic {args.token}", "Content-Type": "application/json"})
            if response.status_code not in (201, 200):
                raise Exception(f'Aidobox did not return status code 201, status={response.status_code} \ntext={response.text} \nstudy={study_json}')


if __name__ == '__main__':
    main(parse_args_aidbox())
