import copy
import json
import logging

import requests

from argsutil import parse_args_aidbox
# If modifying these scopes, delete the file token.pickle.
from row_parser import RowParser
from spreadsheet import spreadsheet

from error_handling import handle_aidbox_response
import fhir_model

LOGGER = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
#SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_SPREADSHEET_ID = '1JFkgwUatREiqXL_XRtchUC6LK7kYP7fG9_u4c8L61cI'
#SAMPLE_RANGE_NAME = 'serviceRequest!A1:H151'
SAMPLE_RANGE_NAME = 'serviceRequest!A1:H50'

def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        service_request_model = fhir_model.get('serviceRequest.json')
        row_parser = RowParser(values[0])
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

            service_request_json = json.dumps(service_request)
            response = requests.put(f"{args.url}/fhir/ServiceRequest/{service_request['id']}", data=service_request_json,
                         headers={'Authorization': f"Basic {args.token}", "Content-Type": "application/json"})
            handle_aidbox_response(response, service_request_json, LOGGER)

if __name__ == '__main__':
    main(parse_args_aidbox())
