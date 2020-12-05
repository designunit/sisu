import json
import urllib2


# need for testing. in this stage info load from file
def unpack_file(filepath):
    file = json.load(open(filepath, 'r'))

    token = file.get('options').get('provider').get('apiKey')
    id = file.get('options').get('provider').get('baseId')
    table_name = file.get('options').get('provider').get('table')

    return token, id, table_name


def get_row_id(table_dict, code):
    for value in table_dict['records']:
        if value['fields']['code'] == code:
            return value['id']


def get_data_from_airtable(airtable_token, airtable_id, airtable_name):
    headers = {
        'Authorization': '%s' % airtable_token,
    }
    request = urllib2.Request('https://api.airtable.com/v0/%s/%s' % (airtable_id, airtable_name), headers=headers)
    response = urllib2.urlopen(request).read()
    return json.loads(response)


def create_patch(id, partial_dict):
    dict = {
        "id": id,
        "fields": {
            "code": partial_dict['code'],
            "color": partial_dict['color'],
            'pattern': partial_dict['pattern'],
        }
    }

    return dict


def update_airtable(airtable_token, airtable_id, airtable_name, patch):
    headers = {
        'Authorization': airtable_token,
        'Content-Type': 'application/json',
    }

    request = urllib2.Request('https://api.airtable.com/v0/%s/%s' % (airtable_id, airtable_name), headers=headers,
                              data=json.dumps(patch))
    request.get_method = lambda: 'PATCH'
    resp = urllib2.urlopen(request)

if __name__ == '__main__':
    token, table_id, table_name = unpack_file('update_airtable.json')

    data_list = [
        {
            'code': 'B_BKb',
            'color': 'color changed',
            'pattern': 'test hash',
        },
        {
            'code': 'B_BKp',
            'color': 'that color is changed too',
            'pattern': 'another hash',
        }

    ]

    data = {
        'records': []
    }

    for partial in data_list:
        table = get_data_from_airtable(token, table_id, table_name)
        row_id = get_row_id(table, partial['code'])
        data['records'].append(create_patch(row_id, partial))

    update_airtable(token, table_id, table_name, data)
