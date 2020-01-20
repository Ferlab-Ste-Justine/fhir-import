Run
=====
0. Prerequisite
Do the Step 1 of the google documentation : https://developers.google.com/sheets/api/quickstart/python

1. Install requirement

``pip install -r requirements.txt``

2. Run scripts 

```python patient.py -u db_user -p db_password -P db_port -H db_host -s db_schema```


The first time it should open a new tab in your browser to authorize the application to read your google spreadsheets.

NOTE : For the first time, the application will start a server on the port 8080


3. New stuffs

in aidbox (db console)
```
--delete from patient;
   --select * from observation;
   --delete from observation;
   --select * from clinicalImpression;
   --delete from clinicalImpression;
   
   --select * from serviceRequest;
   --delete from serviceRequest;
   select * from specimen;
   --delete from specimen;
   --select * from "group";
   --delete from "group";
```

```
sudo pip3 install -r requirements.txt
```

example run:
```
python3 patient_aidbox.py -u http://localhost:8888 -t Zmhpcl9pbXBvcnQ6MDFiOTlmMjgtMTMzMS00ZmVjLTkwM2ItYzJlODA0M2NlYzc3
```
the token -t jhkjhkj...  can be found with postman doinmg a GET to http://localhost:8888/Patient/PA00002
using basic auth fhir_import:01b99f28-1331-4fec-903b-c2e8043cec77 and preview the header 
Auth jhjhjhj....
or Base64 encode fhir_import:01b99f28-1331-4fec-903b-c2e8043cec77

```
#First, run with specimen_aidbox, commenting the line 35 ->   specimen.pop('request'); 
then run ServiceRequest_aidbox; 
then uncomment specimen.pop('request') and re-run specimen
```
