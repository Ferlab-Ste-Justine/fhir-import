import copy
import json
from datetime import datetime

import requests

# If modifying these scopes, delete the file token.pickle.
from argsutil import parse_args
from db import db_transaction, get_connection
from row_parser import RowParser
from spreadsheet import spreadsheet

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1jAP_jpsGA6GS_qFcYwt6TdppW4QU4qCxKocOiZ8Up8g'
SAMPLE_RANGE_NAME = 'patient!B1:V53'


def main(args):
    with spreadsheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME) as values:
        patient_mother = requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/patient_exemple_mother.json').json()
        patient_proband = requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/master/patient_exemple_proband.json').json()
        patient_proband['link'].pop(2)  # No brothers or sisters
        row_parser = RowParser(values[0][0:19])
        connection = get_connection(args)
        with db_transaction(connection):
            for row in values[1:]:
                participant_row = row_parser.as_dict(row[0:19])
                is_proband = participant_row['isProband'] == 'true'
                participant = copy.deepcopy(patient_proband) if is_proband else copy.deepcopy(patient_mother)

                participant['id'] = participant_row['id']
                for identifier in participant['identifier']:
                    if identifier['type']['coding'][0]['code'] == 'MR':
                        identifier['value'] = participant_row['MR']
                    if identifier['type']['coding'][0]['code'] == 'JHN':
                        identifier['value'] = participant_row['JHN']
                birth_date = datetime.strptime(participant_row['birthdate'], '%y-%m-%d')
                participant['birthDate'] = birth_date.strftime('%Y-%m-%d')

                participant['active'] = participant_row['active']
                participant['gender'] = participant_row['gender']

                participant['name']['use'] = participant_row['name.use']
                participant['name']['family'] = participant_row['name.family']
                participant['name']['given'] = [participant_row['name.given']]
                participant['managingOrganization']['reference'] = \
                    f"Organization/{participant_row['managingOrganization']}"
                participant['generalPractitioner'][0]['reference'] = \
                    f"PractitionerRole/{participant_row['generalPractitioner']}"

                for extension in participant['extension'][0]['extension']:
                    if extension['url'] == 'familyId':
                        extension['valueId'] = participant_row['familyId']
                    if extension['url'] == 'ethnicity':
                        extension['valueCode'] = participant_row['ethnicity']
                    if extension['url'] == 'familyComposition':
                        extension['valueCode'] = participant_row['familyComposition']
                    if extension['url'] == 'isProband':
                        extension['valueBoolean'] = participant_row['isProband']

                if is_proband:
                    father = participant['link'][0]
                    mother = participant['link'][1]
                    if participant_row['FTH']:
                        father['other']['reference'] = f"Patient/{participant_row['FTH']}"
                    else:
                        participant['link'].remove(father)
                    if participant_row['MTH']:
                        mother['other']['reference'] = f"Patient/{participant_row['MTH']}"
                    else:
                        participant['link'].remove(mother)
                participant_json = json.dumps(participant, ensure_ascii=False)
                cursor = connection.cursor()
                insert_query = "insert into patient (id, txid, resource, status) values (%s, 0, %s, 'created')"
                cursor.execute(insert_query, (participant['id'], participant_json))


if __name__ == '__main__':
    main(parse_args())
