import json
import re
import os
import airtable
import csv


def get_related_layers(config, derived_only=False):
    def full_layer_name(layer, parent):
        return '{parent}::{layer}'.format(layer=layer, parent=parent)

    names = []
    for x in config['data']:
        name = x['layer'][0]
        if not derived_only:
            names.append(name)
        for view in x['view']:
            view_name = name + view['layerSuffix']
            names.append(full_layer_name(view_name, name))
    return names


def read_sisufile(filepath):
    if not os.path.isfile(filepath):
        return None
    if filepath.endswith('.json'):
        return read_sisufile_json(filepath)
    if filepath.endswith('.csv'):
        return read_sisufile_csv(filepath)
    return None


def sisufile_pull(filepath):
    sisufile = read_sisufile(filepath)
    if not sisufile:
        return False
    
    provider = get_provider(sisufile)
    if not provider:
        return False
    
    try:
        data = provider.get_data()

        with open(filepath, 'r') as f:
            config = json.load(f)
            config['data'] = data

        with open(filepath, 'w') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

        return True
    except Exception:
        return False


def sisufile_update_data(filepath, new_data):
    import tempfile
    import os

    with open(filepath, 'r') as f:
        config = json.load(f)
        config['data'] = new_data

    tmp, tmp_path = tempfile.mkstemp()    
    with os.fdopen(tmp, 'w') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

    os.rename(tmp_path, filepath)

    # with open(filepath, 'r+') as f:
    #     config = json.load(f)
    #     config['data'] = new_data

    #     f.seek(0)
    #     json.dump(config, f, ensure_ascii=False, indent=4)
    #     f.truncate()



def read_sisufile_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

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


def get_provider(config):
    if config['version'] != '0.1':
        return None

    if not config.get('options', {}).get('provider'):
        return None

    provider_type = config.get('options', {}).get('provider', {}).get('type')
    if provider_type == 'airtable':
        options = config.get('options', {}).get('provider', {})
        return airtable.AirtableProvider(options)

    return None
