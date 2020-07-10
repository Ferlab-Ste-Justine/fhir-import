import os

FAULT_TOLERANT = os.environ.get('FAULT_TOLERANT') == "true"

def handle_aidbox_response(response, serialized_entity, logger, expected_codes=(201, 200)):
    if response.status_code not in expected_codes:
        error_msg = f'Aidobox did not return status code in {str(expected_codes)}, status={response.status_code} \ntext={response.text} \nobservation={serialized_entity}'
        if FAULT_TOLERANT:
            logger.error(error_msg)
            return
        raise Exception(error_msg)