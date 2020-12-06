import csv
import json
import re
import os
from get_airtable_data import get_data_from_airtable
from update_airtable_data import update_airtable_data

def read_sisufile(filepath):
    if not os.path.isfile(filepath):
        return None

    if filepath.endswith('.json'):
        json_file = json.load(open(filepath, 'r'))
        if json_file['version'] == '0.1':
            if json_file.get('options').get('provider'):
                return get_airtable_data(json_file)
        else:
            return read_sisufile_json(filepath)
    if filepath.endswith('.csv'):
        return read_sisufile_csv(filepath)

    return None

def get_airtable_data(file):

    table_token = file['options']['provider']['apiKey']
    table_id = file['options']['provider']['baseId']
    table_name = file['options']['provider']['table']
    return get_data_from_airtable(table_token, table_id, table_name)

def update_data(file):
    json_file = json.load(open(file, 'r'))
    if json_file['version'] == '0.1':
        if json_file.get('options').get('provider'):

            table_token = json_file['options']['provider']['apiKey']
            table_id = json_file['options']['provider']['baseId']
            table_name = json_file['options']['provider']['table']

            return update_airtable_data(table_token, table_id, table_name)


def read_sisufile_json(filepath):
    return json.load(open(filepath, 'r'))


def read_sisufile_csv(filepath):
    def row(x):
        view = []
        if x['solid_color'] != '':
            view.append({
                'layerSuffix': '_SOLID',
                'render': ['hatch', {
                    'pattern': 'Solid',
                    'scale': 1,
                    'color': create_color(x['solid_color']),
                    'lineWeight': 0.1
                }]
            })

        if x['pattern_color'] != '':
            view.append({
                'layerSuffix': '_HATCH',
                'render': ['hatch', {
                    'pattern': x['pattern_name'],
                    'scale': float(x['pattern_scale']),
                    'color': create_color(x['pattern_color']),
                    'lineWeight': float(x['pattern_lineweight'])
                }],
            })

        return {
            'layer': [x['layer'], {
                'color': create_color(x['color']),
                'lineType': x['linetype'],
                'lineWeight': float(x['lineweight']),
            }],
            'code': x['code'],
            'properties': {
                'patternRotation': 0,
                'patternBasePoint': [0, 0, 0]
            },
            'view': view,
            'options': {}
        }

    reader = csv.DictReader(open(filepath, 'r'))
    return {
        'version': '0',
        'data': [row(x) for x in reader],
    }


def create_color(value):
    if re.match(r'[a-zA-Z]+', value):
        return [0, 0, 0]
    color_list = value.split(',')
    return [int(channel) for channel in color_list]


if __name__ == '__main__':
    # filepath = 'sisufile.csv'
    # filepath = 'DU4_OFFICE.csv'
    filepath = 'update_airtable.json'
    print(json.dumps(read_sisufile(filepath), indent=4))
    print(json.dumps(update_data(filepath), indent=4))
