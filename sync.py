import csv
import json


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
                'lineWeight': float(x['lineWeight']),
            }],
            'code': x['code'],
            'properties': {
                'patternRotation': 0,
                'patternBasePoint': [0, 0, 0]
            },
            'view': [
            ],
            'options': {}
        }

    reader = csv.DictReader(open(filepath, 'r'))
    return [row(x) for x in reader]


def create_color(value):
    return [0, 0, 0]
