docker build -t fhir-import:latest .;
docker run -it --rm --network aidbox -e "AIDBOX_URL=http://devbox:8888" -e "AIDBOX_AUTH_TOKEN=cm9vdDpzZWNyZXQ=" fhir-import:latest bash;