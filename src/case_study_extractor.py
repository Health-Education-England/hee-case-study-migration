from sortedcontainers import SortedDict
import json
import re


def get_cleaned_up_url(document_url):
    if document_url.endswith(', '):
        return document_url[0:len(document_url) - 2]

    return document_url

def get_dict(s):
    d = {}

    # Uses underscore formatted element and element as the key and the value
    for e in s:
        d.update({re.sub(r'\s+', '_', re.sub(r'[^A-Za-z0-9 _-]+', '', e)).lower():e})

    return SortedDict(d)

def redecorate_case_studies(case_studies, region_dict, sector_dict, impact_group_dict, impact_type_dict):
    for case_study in case_studies:
        case_study['region'] = [k for k, v in region_dict.items() if v in case_study['region']][0]
        case_study['sector'] = [k for k, v in sector_dict.items() if v in case_study['sector']][0]
        case_study['impact_group'] = [k for k, v in impact_group_dict.items() if v in case_study['impact_group']][0]
        case_study['impact_types'] = [k for k, v in impact_type_dict.items() if v in case_study['impact_types']]

def extract_case_studies_with_value_lists(case_studies_json_data_file_path, debug):
    case_studies = []
    regions, sectors, impact_groups, impact_types = (set() for i in range(4))

    with open(case_studies_json_data_file_path) as f:
        case_study_json = json.load(f)

        if debug:
            print(f'Raw Extracted Case Study Data = {case_study_json["data"]}')

        # Loop starting from the second element of the array
        # as the first one contains field/column names
        for case_study in case_study_json['data'][1:]:
            current_case_study_impact_types = [category.strip() for category in case_study[4].split(',')]

            regions.add(case_study[1])
            sectors.add(case_study[2])
            impact_groups.add(case_study[3])
            impact_types.update(set(current_case_study_impact_types))

            case_studies.append({
                'title': case_study[0],
                'region': case_study[1],
                'sector': case_study[2],
                'impact_group': case_study[3],
                'impact_types': current_case_study_impact_types,
                'document_url': get_cleaned_up_url(case_study[5]),
            })

        # Convert set of regions, sectors, impact groups and types to dictionaries
        # with underscore decorated value as key
        region_dict = get_dict(regions)
        sector_dict = get_dict(sectors)
        impact_group_dict = get_dict(impact_groups)
        impact_type_dict = get_dict(impact_types)

        # Redecorates case studies with region, sector, impact group and type keys
        redecorate_case_studies(case_studies, region_dict, sector_dict, impact_group_dict, impact_type_dict)

    return case_studies, region_dict, sector_dict, impact_group_dict, impact_type_dict