import json
import urllib2


def get_sisufile_info(file):
    if file['version'] == '0.1':
        if file.get('options').get('provider'):
            table_token = file['options']['provider']['apiKey']
            table_id = file['options']['provider']['baseId']
            table_name = file['options']['provider']['table']
            return { 'table_token': table_token, 'table_id': table_id, 'table_name': table_name }

    return None

def hex_to_rgb(hex_code):
    hex = hex_code.lstrip('#')
    hlen = len(hex)
    return tuple(int(hex[i:i + hlen / 3], 16) for i in range(0, hlen, hlen / 3))


def render_view(record_value):
    view_list = []
    if 'solidColor' in record_value['fields']:
        view_list.append(render_solid_dict(record_value))
        # view_list.append(record_value['fields'].get('solidColor'))
    if 'pattern' in record_value['fields']:
        view_list.append(render_hatch_dict(record_value))
        # view_list.append(record_value['fields'].get('pattern'))
    return view_list


def render_solid_dict(record_value):
    solid_dict = {
                     "layerSuffix": "_SOLID",
                     "render": ["hatch", {
                         "pattern": "Solid",
                         "scale": 1,
                         "color": hex_to_rgb(record_value['fields'].get('solidColor')),
                         "lineWeight": 0.13
                     }, ]
                 },

    return solid_dict


def render_hatch_dict(record_value): # what the fuck is this?
    hatch_dict = {
        "layerSuffix": "_HATCH",
        "render": ["hatch", {
            "pattern": record_value['fields'].get('pattern'),
            "scale": record_value['fields'].get('patternScale'),
            "color": hex_to_rgb(record_value['fields'].get('patternColor')),
            "lineWeight": record_value['fields'].get('patternLineWeight'),
        }]
    }

    return hatch_dict


def get_data_from_airtable(keys_airtable_dict):
    airtable_token =  keys_airtable_dict['table_token']
    airtable_id = keys_airtable_dict['table_id']
    airtable_name = keys_airtable_dict['table_name']

    headers = {
        'Authorization': 'Bearer %s' % airtable_token,
    }

    request = urllib2.Request('https://api.airtable.com/v0/%s/%s/' % (airtable_id, airtable_name), headers=headers)

    response = urllib2.urlopen(request).read()
    table_json = json.loads(response)

    layers_properties_dict = {
        "version": "0",
        "data": []
    }

    for record in table_json['records']:

        layers_properties_dict['data'].append({
            "layer":
                [record['fields']['code'],
                 {
                     'color': hex_to_rgb(record['fields'].get('color')),
                     'lineType': record['fields'].get('lineType', 'continuous'),
                     'lineWeight': record['fields'].get('lineWeight', 1)
                 }],
            "code": record['fields']['code'],
            "properties": {
                "patternRotation": 0,
                "patternBasePoint": [0, 0, 0]
            },
            'view': render_view(record)
        })

    with open('sisufile.json', 'r') as sisu_file:
        sisu_file_obj = json.load(sisu_file)
        sisu_file_obj['data'] = layers_properties_dict['data']

    with open('sisufile.json', 'w') as sisu_file:
        json.dump(sisu_file_obj, sisu_file, ensure_ascii=False, indent=2)

    return layers_properties_dict
