Run
=====
0. Prerequisite
Do the Step 1 of the google documentation : https://developers.google.com/sheets/api/quickstart/python

1. Install requirement

``pip install -r requirements.txt``

2. Run scripts 

```python patient.py -u db_user -p db_password -P db_port -H db_host -s db_schema```


The first time it should open a new tab in your browaser to authorize the application to read your google spreadsheets.

NOTE : FOr the first time, the appliction will start a server on the port 8080