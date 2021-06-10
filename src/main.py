from ruamel.yaml import YAML
from zipfile import ZipFile
import case_study_brxm_yaml_decorator as case_study_decorator
import case_study_extractor as extractor
import case_study_value_list_brxm_yaml_decorator as case_study_value_list_decorator
import os
import shutil


# OUTPUTS
OUTPUT_BRXM_CASE_STUDY_REGIONS_YAML_FILE_NAME_WITHOUT_EXTN = 'brxm-case-study-regions'
OUTPUT_BRXM_CASE_STUDY_SECTORS_YAML_FILE_NAME_WITHOUT_EXTN = 'brxm-case-study-sectors'
OUTPUT_BRXM_CASE_STUDY_IMPACT_GROUPS_YAML_FILE_NAME_WITHOUT_EXTN = 'brxm-case-study-impact-groups'
OUTPUT_BRXM_CASE_STUDY_IMPACT_TYPES_YAML_FILE_NAME_WITHOUT_EXTN = 'brxm-case-study-impact-types'
OUTPUT_BRXM_CASE_STUDIES_YAML_FILE_NAME_WITHOUT_EXTN = 'brxm-case-studies'


def archive_brxm_yaml_file(yaml_file_path, archive_file_path):
    with ZipFile(archive_file_path, 'w') as zipObj:
        zipObj.write(yaml_file_path, os.path.basename(yaml_file_path))

def archive_brxm_files(yaml_file_path, output_directory, documents_directory, archive_file_path):
    with ZipFile(archive_file_path, 'w') as zipObj:
        zipObj.write(yaml_file_path, os.path.basename(yaml_file_path))
        for folderName, subfolders, filenames in os.walk(documents_directory):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                zipObj.write(filePath, filePath.replace(output_directory, ''))

def dump_brxm_yaml_file(decorated_yaml_object, yaml_file_path):
    yaml = YAML()
    yaml.indent(offset = 2)
    yaml.representer.ignore_aliases = lambda *data: True

    with open(yaml_file_path, 'w') as file:
        yaml.dump(decorated_yaml_object, file)

def delete_directory_content(directory_path):
    # Gather directory contents
    dir_contents = [os.path.join(directory_path, f) for f in os.listdir(directory_path)]

    # Iterate and remove each item in the appropriate manner
    [os.remove(f) if os.path.isfile(f) or os.path.islink(f) else shutil.rmtree(f) for f in dir_contents]

def dump_yaml_and_archive(object_plural_name, decorated_object, output_yaml_file_path_without_extn):
    # Dump decorated object as yaml file
    output_yaml_file_path = f'{output_yaml_file_path_without_extn}.yaml'
    output_archive_yaml_file_path = f'{output_yaml_file_path_without_extn}.zip'
    dump_brxm_yaml_file(decorated_object, output_yaml_file_path)
    print(f'brXM migrated case study {object_plural_name} yaml file {output_yaml_file_path} has successfully been generated')

    # Archive yaml file
    archive_brxm_yaml_file(output_yaml_file_path, output_archive_yaml_file_path)
    print(f'brXM migrated case study {object_plural_name} yaml file {output_yaml_file_path} has successfully been archived as {output_archive_yaml_file_path}')

def main():
    # ENVIRONMENT VARIABLES
    INPUT_CASE_STUDIES_JSON_FILE_PATH = os.getenv('INPUT_CASE_STUDIES_JSON_FILE_PATH')
    OUTPUT_DIRECTORY = os.getenv('OUTPUT_DIRECTORY')
    DEBUG = eval(os.getenv('DEBUG'))

    case_studies, region_dict, sector_dict, impact_group_dict, impact_type_dict = extractor.extract_case_studies_with_value_lists(INPUT_CASE_STUDIES_JSON_FILE_PATH, DEBUG)

    if DEBUG:
        print(f'Extracted & Formatted Regions = {region_dict}')
        print(f'Extracted & Formatted Sectors = {sector_dict}')
        print(f'Extracted & Formatted Impact Groups = {impact_group_dict}')
        print(f'Extracted & Formatted Impact Types = {impact_type_dict}')
        print(f'Extracted Case Studies = {case_studies}')

    # Cleanup existing/old output directory content
    delete_directory_content(OUTPUT_DIRECTORY)

    # REGIONS
    # Decorate regions for brXM import
    decorated_regions = case_study_value_list_decorator.get_decorated_value_list_handle(region_dict, 'regions', 'Regions')
    if DEBUG:
        print(f'Decorated Regions = {decorated_regions}')

    dump_yaml_and_archive(
        'regions',
        decorated_regions,
        f'{OUTPUT_DIRECTORY}{OUTPUT_BRXM_CASE_STUDY_REGIONS_YAML_FILE_NAME_WITHOUT_EXTN}')


    # SECTORS
    # Decorate sectors for brXM import
    decorated_sectors = case_study_value_list_decorator.get_decorated_value_list_handle(sector_dict, 'casestudysectors', 'CaseStudySectors')
    if DEBUG:
        print(f'Decorated Sectors = {decorated_sectors}')

    dump_yaml_and_archive(
        'sectors',
        decorated_sectors,
        f'{OUTPUT_DIRECTORY}{OUTPUT_BRXM_CASE_STUDY_SECTORS_YAML_FILE_NAME_WITHOUT_EXTN}')


    # IMPACT GROUPS
    # Decorate impact groups for brXM import
    decorated_impact_groups = case_study_value_list_decorator.get_decorated_value_list_handle(impact_group_dict, 'casestudyimpactgroups', 'CaseStudyImpactGroups')
    if DEBUG:
        print(f'Decorated Sectors = {decorated_sectors}')

    dump_yaml_and_archive(
        'impact groups',
        decorated_impact_groups,
        f'{OUTPUT_DIRECTORY}{OUTPUT_BRXM_CASE_STUDY_IMPACT_GROUPS_YAML_FILE_NAME_WITHOUT_EXTN}')


    # IMPACT TYPES
    # Decorate impact types for brXM import
    decorated_impact_types = case_study_value_list_decorator.get_decorated_value_list_handle(impact_type_dict, 'casestudyimpacttypes', 'CaseStudyImpactTypes')
    if DEBUG:
        print(f'Decorated Impact Types = {decorated_impact_types}')

    dump_yaml_and_archive(
        'impact types',
        decorated_impact_types,
        f'{OUTPUT_DIRECTORY}{OUTPUT_BRXM_CASE_STUDY_IMPACT_TYPES_YAML_FILE_NAME_WITHOUT_EXTN}')


    # CASE STUDIES
    # Decorate migrated case studies for brXM import
    # NOTE that it also downloads the associated case study documents
    # along with text extracted from PDF files as a binary resource
    decorated_case_studies = case_study_decorator.get_decorated_migrated_case_studies_folder(case_studies, OUTPUT_DIRECTORY)
    if DEBUG:
        print(f'Decorated Case Studies = {decorated_case_studies}')

    # Dump decorated migrated case studies as yaml file
    output_case_studies_file_path = f'{OUTPUT_DIRECTORY}{OUTPUT_BRXM_CASE_STUDIES_YAML_FILE_NAME_WITHOUT_EXTN}'
    output_case_studies_yaml_file_path = f'{output_case_studies_file_path}.yaml'
    output_case_studies_archive_yaml_file_path = f'{output_case_studies_file_path}.zip'
    output_case_studies_documents_file_path = f'{OUTPUT_DIRECTORY}documents'
    dump_brxm_yaml_file(decorated_case_studies, output_case_studies_yaml_file_path)
    print(f'brXM migrated case study yaml file {output_case_studies_yaml_file_path} has successfully been generated')

    # Archive case studies yaml file and its associated documents
    archive_brxm_files(
        output_case_studies_yaml_file_path,
        OUTPUT_DIRECTORY,
        output_case_studies_documents_file_path,
        output_case_studies_archive_yaml_file_path)
    print(f'Both brXM migrated case studies yaml file {output_case_studies_yaml_file_path} and its associated documents (available under {output_case_studies_documents_file_path}) has successfully been archived as {output_case_studies_archive_yaml_file_path}')

if __name__ == '__main__':
    main()