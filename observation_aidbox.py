import copy
import json

import requests

from argsutil import parse_args_aidbox
# If modifying these scopes, delete the file token.pickle.
from row_parser import RowParser
from spreadsheet import spreadsheet

import fhir_model

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
#SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_SPREADSHEET_ID = '1JFkgwUatREiqXL_XRtchUC6LK7kYP7fG9_u4c8L61cI'
SAMPLE_RANGE_NAME = 'observation!A:K'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        observation_pheno = fhir_model.get('observation_exemple_de_pheno.json')
        observation_notes = fhir_model.get('observation_exemple_de_notes.json')
        # observation_exemple_indications.json
        observation_indication = fhir_model.get('observation_exemple_indications.json')
        row_parser = RowParser(values[0])
        for row in values[1:]:
            observation_row = row_parser.as_dict(row)
            is_pheno = observation_row['code.text'] == 'phenotype observation'
            is_indication = observation_row['code.text'] == 'Indications'
            if is_pheno:
                observation = copy.deepcopy(observation_pheno)
            elif is_indication:
                observation = copy.deepcopy(observation_indication)
            else:
                observation = copy.deepcopy(observation_notes)

            observation['id'] = observation_row['id']
            observation['effectiveDateTime'] = observation_row['effectiveDateTime']
            observation['subject']['reference'] = f"Patient/{observation_row['subject']}"
            observation['performer'][0]['reference'] = f"Practitioner/{observation_row['performer']}"

            row_note = observation_row.get('note')
            if row_note:
                observation['note'][0]['text'] = row_note
            else:
                observation.pop('note')

            if is_pheno:
                (code, display) = observation_row['valueCodeableConcept.code et  .display'].split(', ')
                coding = observation['valueCodeableConcept']['coding'][0]
                coding['code'] = code
                coding['display'] = display
                coding['system'] = observation_row['valueCodableConcept.coding.system']

                interpretation_coding = observation['interpretation'][0]['coding'][0]
                interpretation_coding['code'] = observation_row['interpretation.coding.code']
                interpretation_coding['display'] = observation_row['interpretation.coding.display']
                observation['interpretation'][0]['text'] = observation_row['interpretation.text']

            observation_json = json.dumps(observation)
            response = requests.put(f"{args.url}/fhir/Observation/{observation['id']}", data=observation_json,
                         headers={'Authorization': f"Basic {args.token}", "Content-Type": "application/json"})
            if response.status_code not in (201, 200):
                raise Exception(f'Aidobox did not return status code 201, status={response.status_code} \ntext={response.text} \nobservation={observation_json}')

if __name__ == '__main__':
    main(parse_args_aidbox())
