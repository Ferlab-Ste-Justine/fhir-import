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
SAMPLE_SPREADSHEET_ID = '1JFkgwUatREiqXL_XRtchUC6LK7kYP7fG9_u4c8L61cI'
SAMPLE_RANGE_NAME = 'FMH!A:E'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        fmh_model = fhir_model.get('familyMemberHistory.json')
        row_parser = RowParser(values[0])
        for row in values[1:]:
            fmh_row = row_parser.as_dict(row)
            fmh = copy.deepcopy(fmh_model)

            fmh['id'] = fmh_row['id']
            fmh['status'] = fmh_row['status']
            fmh['patient']['reference'] = f"Patient/{fmh_row['patient']}"
            fmh['date'] = fmh_row['date']
            fmh['note'][0]['text'] = fmh_row['note']

            fmh_json = json.dumps(fmh)
            response = requests.put(f"{args.url}/fhir/FamilyMemberHistory/{fmh['id']}", data=fmh_json,
                         headers={'Authorization': f"Basic {args.token}", "Content-Type": "application/json"})
            if response.status_code not in (201, 200):
                raise Exception(f'Aidobox did not return status code 201, status={response.status_code} \ntext={response.text} \nfmh={fmh_json}')

if __name__ == '__main__':
    main(parse_args_aidbox())
