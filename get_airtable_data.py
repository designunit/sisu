import requests
import json

# TODO: Переформатировать цвета

headers = {
    'Authorization': 'Bearer key0YA6rgADmbxx61',
}

response = requests.get('https://api.airtable.com/v0/appwLoUM2FeZap2P4/Derbent/', headers=headers)

print(response)
table_json = response.json()

with open('test_response.json', 'w', encoding='utf-8') as test_response_file:
    json.dump(table_json, test_response_file, ensure_ascii=False)

print(f'ответ airtable: {table_json}')

layers_properties_dict = {
    "version": "0",
    "data": []
    }

def check_field_is_not_empty(record_value, column_name):
    if column_name in record_value['fields']:
        return True
    else:
        return False


def hex_to_rgb(record_value, column_name):
    if check_field_is_not_empty(record_value, column_name):
        hex = record_value['fields'].get(column_name)
        hex = hex.lstrip('#')
        hlen = len(hex)
        return tuple(int(hex[i:i + hlen // 3], 16) for i in range(0, hlen, hlen // 3))
    else:
        return None

def render_view(record_value):
    if check_field_is_not_empty(record_value, 'solidColor'):
        solid_dict = render_solid_dict(record_value)
        if check_field_is_not_empty(record_value, 'pattern'):
            hatch_dict = render_hatch_dict(record_value)
            return [solid_dict, hatch_dict]
        else:
            return [solid_dict]
    elif check_field_is_not_empty(record_value, 'pattern'):
        hatch_dict = render_hatch_dict(record_value)
        return [hatch_dict]
    else:
        return []


def render_solid_dict(record_value):
    solid_dict = {
                     "layerSuffix": "_SOLID",
                     "render": ["hatch", {
                         "pattern": "Solid",
                         "scale": 1,
                         "color": hex_to_rgb(record_value, 'solidColor'),
                         "lineWeight": 0.13
                     }, ]
                 },

    return solid_dict

def render_hatch_dict(record_value):
    hatch_dict = {
        "layerSuffix": "_HATCH",
        "render": ["hatch", {
            "pattern": record_value['fields'].get('pattern'),
            "scale": record_value['fields'].get('patternScale'),
            "color": hex_to_rgb(record_value, 'patternColor'),
            "lineWeight": record_value['fields'].get('patternLineWeight'),
        }]
    }

    return hatch_dict

for record in table_json['records']:
    layers_properties_dict['data'].append({
        "layer":
            [record['fields']['code'],
             {
                 'color': hex_to_rgb(record, 'color'),
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
with open('airtable.json', 'w', encoding='utf-8') as airtable_file:
    json.dump(layers_properties_dict, airtable_file, ensure_ascii=False)