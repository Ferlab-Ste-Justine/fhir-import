import copy
import json
import logging

import requests

# If modifying these scopes, delete the file token.pickle.
from argsutil import parse_args_aidbox
from spreadsheet import spreadsheet

from error_handling import handle_aidbox_response
import fhir_model

LOGGER = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
#SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_SPREADSHEET_ID = '1JFkgwUatREiqXL_XRtchUC6LK7kYP7fG9_u4c8L61cI'
SAMPLE_RANGE_NAME = 'group!A2:P'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        group_model = fhir_model.get('group.json')
        for row in values:
            group = copy.deepcopy(group_model)

            group['id'] = row[0]
            group['member'] = []
            for r in row[1:]:
                group['member'].extend([{'entity': {'reference': f"Patient/{r}"}}])

            group_json = json.dumps(group)
            response = requests.put(f"{args.url}/fhir/Group/{group['id']}", data=group_json,
                         headers={'Authorization': f"Basic {args.token}", "Content-Type": "application/json"})
            handle_aidbox_response(response, group_json, LOGGER)


if __name__ == '__main__':
    main(parse_args_aidbox())
