import csv
import json
import re
import os


def read_sisufile(filepath):
    if not os.path.isfile(filepath):
        return None

    if filepath.endswith('.json'):
        return read_sisufile_json(filepath)
    if filepath.endswith('.csv'):
        return read_sisufile_csv(filepath)

    return None


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
    print(value)
    if re.match(r'[a-zA-Z]+', value):
        return [0, 0, 0]
    color_list = value.split(',')
    return [int(channel) for channel in color_list]


if __name__ == '__main__':
    filepath = 'sisufile.csv'
    filepath = 'DU4_OFFICE.csv'
    print(json.dumps(read_sisufile(filepath), indent=4))
