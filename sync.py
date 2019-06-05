import csv
import json
import re

filepath = 'sisufile.json'


def read_sisufile(filepath):
    if filepath.endswith('.json'):
        return read_sisufile_json(filepath)
    if filepath.endswith('.csv'):
        return read_sisufile_csv(filepath)
    return None


def read_sisufile_json(filepath):
    return json.load(open(filepath, 'r'))


def read_sisufile_csv(filepath):
    def row(x):
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
            'view': [
                {
                    'layerSuffix': '_SOLID',
                    'render': ['hatch', {
                        'pattern': 'Solid',
                        'scale': 1,
                        'color': create_color(x['solid_color']),
                        'lineWeight': 0.1
                    }]
                },
                {
                    'layerSuffix': '_HATCH',
                    'render': ['hatch', {
                        'pattern': x['PAT_name'],
                        'scale': x['PAT_scale'],
                        'color': create_color(x['PAT_color']),
                        'lineWeight': float(x['PAT_lineweight'])
                    }],
                }
             ],
            'options': {}
        }


    reader = csv.DictReader(open(filepath, 'r'))

    return [row(x) for x in reader]


def create_color(value):
    if re.match(r'\w+', value):
        return [0, 0, 0]
    color_list = value.split(',')
    return [int(channel) for channel in color_list]


if __name__ == '__main__':
    color_red = 'black 123'

    print (create_color(color_red))
    print(read_sisufile(filepath))
