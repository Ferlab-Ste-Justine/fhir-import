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
#SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_SPREADSHEET_ID = '1JFkgwUatREiqXL_XRtchUC6LK7kYP7fG9_u4c8L61cI'
SAMPLE_RANGE_NAME = 'clinicalImpression!A:K'

def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        clinical_impression_model = fhir_model.get('clinicalImpression.json')
        clinical_impression_model.pop('meta')
        row_parser = RowParser(values[0])

        for row in values[1:]:
            clinical_impression_row = row_parser.as_dict(row)
            clinical_impression = copy.deepcopy(clinical_impression_model)

            clinical_impression['id'] = clinical_impression_row['id']

            clinical_impression['effectiveDateTime'] = clinical_impression_row['effectiveDateTime']
            clinical_impression['subject']['reference'] = f"Patient/{clinical_impression_row['subject']}"
            clinical_impression['assessor']['reference'] = f"PractitionerRole/{clinical_impression_row['assessor']}"
            clinical_impression['extension'][0]['valueAge']['value'] = int(clinical_impression_row['valueAge'])
            clinical_impression['investigation'][0]['item'] = []
            for r in row[5:10]:
                clinical_impression['investigation'][0]['item'].extend([{'reference': r}])

            clinical_impression_json = json.dumps(clinical_impression)
            response = requests.put(f"{args.url}/fhir/ClinicalImpression/{clinical_impression['id']}", data=clinical_impression_json,
                         headers={'Authorization': f"Basic {args.token}", "Content-Type": "application/json"})
            if response.status_code not in (201, 200):
                raise Exception(f'Aidobox did not return status code 201, status={response.status_code} \ntext={response.text} \nclinical_impression={clinical_impression_json}')


if __name__ == '__main__':
    main(parse_args_aidbox())
