import copy
import json

import requests

# If modifying these scopes, delete the file token.pickle.
from argsutil import parse_args_aidbox
from spreadsheet import spreadsheet

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_RANGE_NAME = 'group!A2:K'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        group_model = requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/group.json').json()
        for row in values:
            group = copy.deepcopy(group_model)

            group['id'] = row[0]
            group['member'] = []
            for r in row[1:]:
                group['member'].extend([{'entity': {'reference': f"Patient/{r}"}}])

            group_json = json.dumps(group)
            response = requests.put(f"{args.url}/fhir/Group/{group['id']}", data=group_json,
                         headers={'Authorization': f"Basic {args.token}", "Content-Type": "application/json"})
            if response.status_code not in (201, 200):
                raise Exception(f'Aidobox did not return status code 201, status={response.status_code} \ntext={response.text} \ngroup={group_json}')


if __name__ == '__main__':
    main(parse_args_aidbox())
