import json
import urllib2


class AirtableProvider():
    def __init__(self, config):
        self.token = config['apiKey']
        self.table_id = config['baseId']
        self.table_name = config['table']

    def get_data(self):
        return get_data_from_airtable(self.token, self.table_id, self.table_name)


def hex_to_rgb(hex_value):
    if not is_hex_color(hex_value):
        return None
    hex_value = hex_value.strip().lstrip('#')
    hlen = len(hex_value)
    s = 2
    return tuple(
        int(hex_value[i:i+s], 16)
        for i in range(0, hlen, s)
    )


def is_hex_color(value):
    if hex_value == None:
        return False
    m = re.match('^#[0-9a-f]{6}$', value)
    if not m:
        return False
    return True


def create_views(record):
    views = []
    if 'solidColor' in record:
        v = create_solid_view(record)
        if v:
            views.append(v)
    if 'pattern' in record:
        v = create_hatch_view(record)
        if v:
            views.append(v)
        views.append(v)
    return views


def create_solid_view(record):
    color = hex_to_rgb(record.get('solidColor', '#000000'))
    if not color:
        return None

    return {
        "layerSuffix": "_SOLID",
        "render": ["hatch", {
            "pattern": "Solid",
            "scale": 1,
            "color": color,
            "lineWeight": 0.13
        }, ]
    }


def create_hatch_view(record):
    color = hex_to_rgb(record.get('patternColor', '#000000'))
    if not color:
        return None
    hatch_dict = {
        "layerSuffix": "_HATCH",
        "render": ["hatch", {
            "pattern": record.get('pattern', 'Grid'),
            "scale": float(record.get('patternScale', 1)),
            "color": color,
            "lineWeight": float(record.get('patternLineWeight', 0.13)),
        }]
    }
    return hatch_dict


def airtable_get(token, base_id, table_name):
    headers = {
        'Authorization': 'Bearer %s' % token,
    }
    request = urllib2.Request('https://api.airtable.com/v0/%s/%s/' % (base_id, table_name), headers=headers)
    response = urllib2.urlopen(request).read()
    return json.loads(response)


def get_data_from_airtable(token, base_id, table_name):
    table = airtable_get(token, base_id, table_name)

    collected_codes = set()
    layers = []
    for record in table['records']:
        f = record['fields']
        code = f.get('code')
        units = f.get('units')
        if not code or not units:
            continue
        if code in collected_codes:
            continue
        collected_codes.add(code)
        color = hex_to_rgb(f.get('color', '#000000')
        if not color:
            continue
        layers.append({
            'layer':
                [code, {
                    'color': color,
                    'lineType': f.get('lineType', 'continuous'),
                    'lineWeight': f.get('lineWeight', 1)
                }],
            'code': {
                'id': code,
                'units': units,
                'name': f.get('name'),
                'description': f.get('description'),
            },
            'properties': {
                'patternRotation': 0,
                'patternBasePoint': [0, 0, 0]
            },
            'view': create_views(f)
        })

    return layers


if __name__ == '__main__':
    print('runned from terminal')
