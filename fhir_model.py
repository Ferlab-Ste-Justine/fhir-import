import os
import json

import requests

def get(model):
    return requests.get(
            'https://raw.githubusercontent.com/cr-ste-justine/clin-FHIR/{}/{}'.format(os.environ['MODEL_GIT_REFERENCE'], model)).json()