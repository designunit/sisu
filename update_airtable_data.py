import json
import urllib2


# need for testing. in this stage info load from file
def unpack_file(filepath):
    settings_file = json.load(open(filepath, 'r'))

    token_from_file = settings_file.get('options').get('provider').get('apiKey')
    id_from_file = settings_file.get('options').get('provider').get('baseId')
    table_name_from_file = settings_file.get('options').get('provider').get('table')

    return token_from_file, id_from_file, table_name_from_file


def get_row_id(table_dict, code):
    for value in table_dict['records']:
        if value['fields']['code'] == code:
            return value['id']


def get_data_from_airtable(airtable_token, airtable_id, airtable_name):
    headers = {
        'Authorization': 'Bearer %s' % airtable_token,
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


def send_patch_request(airtable_token, airtable_id, airtable_name, patch):
    headers = {
        'Authorization': 'Bearer %s' % airtable_token,
        'Content-Type': 'application/json',
    }

    request = urllib2.Request('https://api.airtable.com/v0/%s/%s' % (airtable_id, airtable_name), headers=headers,
                              data=json.dumps(patch))
    request.get_method = lambda: 'PATCH'
    response = urllib2.urlopen(request)

    return response.read()

def update_airtable_data(token, table_id, table_name):

    data_list = [
        {
            'code': 'B_BKb',
            'color': 'look at me',
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

    return send_patch_request(token, table_id, table_name, data)
