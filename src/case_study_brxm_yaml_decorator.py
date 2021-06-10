from datetime import datetime, timezone
from pathlib import Path
from tika import parser
from unidecode import unidecode
import mimetypes
import os
import re
import requests
import tika
import unicodedata
import uuid

def get_current_utc():
    return datetime.now(timezone.utc)

def get_brxm_node_name(title):
    normalised_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()
    non_alpha_numeric_chars_stripped_title = re.sub(r'[^A-Za-z0-9 -]+', '', normalised_title)
    return non_alpha_numeric_chars_stripped_title[:50].lower().replace(' ', '-')

def get_decorated_document_handle_object(title):
    return {
        'jcr:primaryType': 'hippo:handle',
        'jcr:mixinTypes': ['hippo:named', 'hippo:versionInfo', 'mix:referenceable'],
        'hippo:name': f'{title}'
    }

def get_filename(document_url):
    filename = document_url[document_url.rfind("/") + 1:]

    # Strips out parenthesised numbers [e.g. CS60 Hirson Library Report of a case _study_VV (1).docx -> CS60 Hirson Library Report of a case _study_VV.docx]
    filename = re.sub(r'\s?\(\d\)', '', filename)

    # Replaces whitespaces with underscores
    filename = re.sub(r'\s+', '_', filename)

    return filename

def get_mime_type(filename):
    return mimetypes.types_map[os.path.splitext(filename)[1]]

def generate_text_version_of_pdf(pdf_file_path, output_file_path):
    with open(output_file_path, 'w') as f:
        f.write(parser.from_file(pdf_file_path)['content'])

def download_document(document_url, output_file_path):
    # Makes output file directories if not already exists
    output_file_directory = Path(os.path.dirname(output_file_path))
    output_file_directory.mkdir(parents = True, exist_ok = True)

    r = requests.get(document_url.replace(' ', '%20'), allow_redirects = True)

    with open(output_file_path, 'wb') as f:
        f.write(r.content)

def get_document_node(case_study_node_name, document_url, output_directory):
    filename = get_filename(document_url)

    relative_output_file_path = f'documents/{case_study_node_name}/{filename}'

    download_document(document_url, f'{output_directory}{relative_output_file_path}')

    mime_type = get_mime_type(filename)

    document_node = {
        'jcr:primaryType': 'hippo:resource',
        'hippo:filename': filename,
        'jcr:encoding': 'UTF-8',
        'jcr:lastModified': get_current_utc(),
        'jcr:mimeType': mime_type,
        'jcr:data': {
            'type': 'binary',
            'resource': relative_output_file_path
        }
    }

    if mime_type == 'application/pdf':
        splitted_file_name = os.path.splitext(filename)
        relative_output_text_file_path = f'documents/{case_study_node_name}/{splitted_file_name[0]}_text{splitted_file_name[1]}'

        generate_text_version_of_pdf(f'{output_directory}{relative_output_file_path}', f'{output_directory}{relative_output_text_file_path}')

        document_node['hippo:text'] = {
            'type': 'binary',
            'resource': relative_output_text_file_path
        }

    return document_node

def get_decorated_migrated_case_studies_folder_object():
    return {
        "jcr:primaryType": "hippostd:folder",
        "jcr:mixinTypes": ["hippo:named", "hippotranslation:translated", "mix:versionable"],
        "hippo:name": "Migrated Case Studies",
        "hippostd:foldertype": ["new-caseStudy-folder", "new-caseStudy-document"],
        "hippotranslation:id": str(uuid.uuid4()),
        "hippotranslation:locale": "en"
    }

def get_decorated_case_study_object(case_study, case_study_node_name, state, availability, translation_uuid, output_directory):
    decorated_case_study = {}

    # Add meta data
    decorated_case_study['jcr:primaryType'] = 'hee:caseStudy'
    decorated_case_study['jcr:mixinTypes'] = ['mix:referenceable', 'mix:versionable']
    decorated_case_study['hippo:availability'] = availability
    decorated_case_study['hippostd:retainable'] = False
    decorated_case_study['hippostd:state'] = state
    decorated_case_study['hippostdpubwf:createdBy'] = 'admin'
    decorated_case_study['hippostdpubwf:lastModifiedBy'] = 'admin'
    decorated_case_study['hippostdpubwf:creationDate'] = get_current_utc()
    decorated_case_study['hippostdpubwf:lastModificationDate'] = get_current_utc()
    decorated_case_study['hippotranslation:id'] = translation_uuid
    decorated_case_study['hippotranslation:locale'] = 'en'

    # Add CaseStudy data
    decorated_case_study['hee:title'] = f'{unidecode(case_study["title"])}'
    decorated_case_study['hee:region'] = f'{case_study["region"]}'
    decorated_case_study['hee:sector'] = f'{case_study["sector"]}'
    decorated_case_study['hee:impactGroup'] = f'{case_study["impact_group"]}'
    decorated_case_study['hee:impactTypes'] = case_study["impact_types"]

    decorated_case_study['/hee:document'] = get_document_node(case_study_node_name, case_study['document_url'], output_directory)

    return decorated_case_study

def get_decorated_migrated_case_studies_folder(case_studies, output_directory):
    # Initialising mimetypes and tika modules
    mimetypes.init()
    tika.initVM()

    decorated_migrated_case_studies_folder = {}

    # Build migrated-case-studies folder node
    decorated_migrated_case_studies_folder['/migrated-case-studies'] = get_decorated_migrated_case_studies_folder_object()

    for case_study in case_studies:
        case_study_node_name = get_brxm_node_name(case_study['title'])

        # Build hee:caseStudy handle node
        decorated_migrated_case_studies_folder['/migrated-case-studies']['/' + case_study_node_name] = get_decorated_document_handle_object(case_study['title'])

        translation_uuid = str(uuid.uuid4())

        # Build hee:caseStudy node for draft version
        decorated_migrated_case_studies_folder['/migrated-case-studies']['/' + case_study_node_name]['/' + case_study_node_name + '[1]'] = get_decorated_case_study_object(case_study, case_study_node_name, 'draft', [], translation_uuid, output_directory)

        # Build hee:caseStudy node for unpublished version
        decorated_migrated_case_studies_folder['/migrated-case-studies']['/' + case_study_node_name]['/' + case_study_node_name + '[2]'] = get_decorated_case_study_object(case_study, case_study_node_name, 'unpublished', ['preview'], translation_uuid, output_directory)

    return decorated_migrated_case_studies_folder
