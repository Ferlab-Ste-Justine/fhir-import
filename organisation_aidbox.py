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
SAMPLE_RANGE_NAME = 'organisation!B:D'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        organization_model = fhir_model.get('organization.json')
        row_parser = RowParser(values[0])

        for row in values[1:]:
            organization_row = row_parser.as_dict(row)
            organization = copy.deepcopy(organization_model)

            organization['id'] = organization_row['id']
            organization['name'] = organization_row['name']
            organization['alias'] = [organization_row['alias']]

            organization_json = json.dumps(organization)
            response = requests.put(f"{args.url}/fhir/Organization/{organization['id']}", data=organization_json,
                                    headers={'Authorization': f"Basic {args.token}",
                                             "Content-Type": "application/json"})
            handle_aidbox_response(response, organization_json, LOGGER)


if __name__ == '__main__':
    main(parse_args_aidbox())
