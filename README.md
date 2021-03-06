# HEE Case Study Migration

This project will be used to migrate the existing HEE case studies onto brXM (Bloomreach Experience Manager) platform.

The project essentially extracts case study data from the given JSON file and builds YAML files for case studies along with its associated value-lists which can readily be imported to brXM.

## Pre Requisites
In order to develop and run on this platform you will need to have the `Docker` installed.

## Run with Docker Compose
Execute the following command to run the script:

```
>> docker-compose up --build
```

Make sure to update the following volumes and environment variables before running the script:

- Volumes
  - /input: The volume under which the case study JSON data file should be placed.
  - /output: The volume under which the outputs will be stored. The migration script produced the following outputs:
    - `brxm-case-study-impact-groups.zip`: An export of case study impact groups which could readily be imported onto brXM as `//content/documents/administration/valuelists/kls/casestudyimpactgroups` value-list.
    - `brxm-case-study-impact-types.zip`: An export of case study impact types which could readily be imported onto brXM as `//content/documents/administration/valuelists/kls/casestudyimpacttypes` value-list.
    - `brxm-case-study-regions.zip`: An export of case study regions which could readily be imported onto brXM as `//content/documents/administration/valuelists/kls/regions` value-list.
    - `brxm-case-study-sectors.zip`: An export of case study sectors which could readily be imported onto brXM as `//content/documents/administration/valuelists/kls/sectors` value-list.
    - `brxm-case-studies.zip`: An export of case studies with associated documents which could readily be imported onto brXM as `hee:caseStudy` documents under `Migrated Case Studies` folder.
- Environment Variables
  - INPUT_CASE_STUDIES_JSON_FILE_PATH: Input case studies JSON file path. Refer `HEE-251` for the format of the JSON.
  - OUTPUT_DIRECTORY: The output directory wherein the output archives will be stored. Note that the path must end with a trailig slash.
  - DEBUG: A (python) Boolean [True/False] indicating whether DEBUG is enabled or not.

## Importing outputs onto brXM
- Login to the brXM console (`/cms/console`) of the environment wherein the case studies along with its associated value-lists needs to be imported (with `xm.console.user` privilege).
- Import `brxm-case-study-impact-groups.zip` under `/content/documents/administration/valuelists/kls` node in order to import the case study impact groups.
- Import `brxm-case-study-impact-types.zip` under `/content/documents/administration/valuelists/kls` node in order to import the case study impact types.
- Import `brxm-case-study-regions.zip` under `/content/documents/administration/valuelists/kls` node in order to import the case study regions.
- Import `brxm-case-study-sectors.zip` under `/content/documents/administration/valuelists/kls` node in order to import the case study sectors.
- Import `brxm-case-studies.zip` under `/content/documents/lks` node in order to import case studies under `Migrated Case Studies` folder.
- Login to brXM CMS (`/cms`) of the environment wherein the case studies have been imported (with privilege to edit documents of `hee:caseStudy` type) and publish them all by choosing `Publish all in folder...` on `Migrated Case Studies` folder.
