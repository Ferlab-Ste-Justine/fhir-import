import copy
import json

import requests

from argsutil import parse_args_aidbox
# If modifying these scopes, delete the file token.pickle.
from row_parser import RowParser
from spreadsheet import spreadsheet

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_RANGE_NAME = 'observation!A:K'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        observation_pheno = requests.get('https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/observation_exemple_de_pheno.json').json()
        observation_notes = requests.get('https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/observation_exemple_de_notes.json').json()
        row_parser = RowParser(values[0])
        for row in values[1:]:
            observation_row = row_parser.as_dict(row)
            is_pheno = observation_row['code.text'] == 'phenotype observation'
            observation = copy.deepcopy(observation_pheno) if is_pheno else copy.deepcopy(observation_notes)

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
