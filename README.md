About
=====

This project is used to import dummy Fhir data from an external spreadsheet to an Aidbox system.

Usage
=====

You can build an image that is composable at runtime from the Dockerfile.

For local troubleshooting, you can do the following:

1. Go into the **aidbox** directory and enter your license key and id in the **.env** file.

2. Still from the **aidbox** directory, launch a local instance of the aidbox system by typing:

```
docker-compose up -d
```

2. Going back to the root directory of this repo, run a shell in a container setup to interact with your local aidbox by typing:

```
./devbash.sh
```

3. Inside the container, perform the update on your aidbox by typing:

```
./upsert.sh
```

As indicated by the script's name, the script is idempotent and will both insert the update the data.

Alternatively, you can copy and run individual lines in the upsert script to only insert/update certain tables, but keep in mind that there are foreign key dependencies between tables and thing might not update/insert properly if the dependency chain is not followed.