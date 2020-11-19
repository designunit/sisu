import requests

def hex_to_rgb(hex_code):
    hex = hex_code.lstrip('#')
    hlen = len(hex)
    return tuple(int(hex[i:i + hlen // 3], 16) for i in range(0, hlen, hlen // 3))

def render_view(record_value):
    view_list = []
    if 'solidColor' in record_value['fields']:
        view_list.append(record_value['fields'].get('solidColor'))
    if 'pattern' in record_value['fields']:
        view_list.append(record_value['fields'].get('pattern'))
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

def render_hatch_dict(record_value):
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



# TODO: Переформатировать цвета

airtable_token = 'Bearer <strong_key>'

headers = {
    'Authorization': '%s' % airtable_token,
}

response = requests.get('https://api.airtable.com/v0/appwLoUM2FeZap2P4/Derbent/', headers=headers)

table_json = response.json()

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

print(layers_properties_dict)