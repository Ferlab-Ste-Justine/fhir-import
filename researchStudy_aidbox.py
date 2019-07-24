import copy
import json

import requests

# If modifying these scopes, delete the file token.pickle.
from argsutil import parse_args_aidbox
from spreadsheet import spreadsheet

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_RANGE_NAME = 'researchStudy!A:M'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        study_model = requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/researchStudy.json').json()
        for row in values[1:]:
            study = copy.deepcopy(study_model)

            study['id'] = row[0]
            study['status'] = row[1]
            study['title'] = row[2]
            study['description'] = row[3]

            study['sponsor']['reference'] = f"Organization/{row[6]}"
            study['principalInvestigator']['reference'] = f"Practitioner/{row[7]}"
            study['enrollment'] = []
            for r in row[8:13]:
                study['enrollment'].extend([{'reference': f"Group/{r}"}])
            study['period']['start'] = row[4]
            study['period']['end'] = row[5]

            study_json = json.dumps(study)
            response = requests.put(f"{args.url}/fhir/ResearchStudy/{row[0]}", data=study_json,
                         headers={'Authorization': f"Basic {args.token}", "Content-Type": "application/json"})
            if response.status_code not in (201, 200):
                raise Exception(f'Aidobox did not return status code 201, status={response.status_code} \ntext={response.text} \nstudy={study_json}')


if __name__ == '__main__':
    main(parse_args_aidbox())
