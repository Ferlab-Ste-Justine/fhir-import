import copy
import json
import logging

import requests

# If modifying these scopes, delete the file token.pickle.
from argsutil import parse_args_aidbox
from row_parser import RowParser
from spreadsheet import spreadsheet

from error_handling import handle_aidbox_response
import fhir_model

LOGGER = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_RANGE_NAME = 'practitionerRole!A:F'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        practitioner_model = fhir_model.get('practitionerRole.json')
        row_parser = RowParser(values[0][0:6])

        for row in values[1:]:
            practitioner_role_row = row_parser.as_dict(row[0:6])
            practitioner_role = copy.deepcopy(practitioner_model)

            practitioner_role['id'] = practitioner_role_row['id']
            practitioner_role['practitioner']['reference'] = \
                f"Practitioner/{practitioner_role_row['practitioner']}"
            practitioner_role['organization']['reference'] = \
                f"Organization/{practitioner_role_row['organization']}"
            code = practitioner_role['code'][0]
            code['coding'][0]['code'] = practitioner_role_row['code.coding.code']
            code['coding'][0]['display'] = practitioner_role_row['code.coding.display']
            code['text']=practitioner_role_row['code.text']
            practitioner_role_json = json.dumps(practitioner_role)
            response = requests.put(f"{args.url}/fhir/PractitionerRole/{practitioner_role['id']}", data=practitioner_role_json,
                                    headers={'Authorization': f"Basic {args.token}",
                                             "Content-Type": "application/json"})
            handle_aidbox_response(response, practitioner_role_json, LOGGER)


if __name__ == '__main__':
    main(parse_args_aidbox())
