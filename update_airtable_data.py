import json
import urllib2
from airtable import airtable_get


def unpack_file(filepath):
    with open(filepath, 'r') as f:
        config = json.load(f)

    token_from_file = config.get('options').get('provider').get('apiKey')
    id_from_file = config.get('options').get('provider').get('baseId')
    table_name_from_file = config.get('options').get('provider').get('table')

    return token_from_file, id_from_file, table_name_from_file


def get_row_id(table_dict, code):
    for value in table_dict['records']:
        if value['fields']['code'] == code:
            return value['id']


def create_airtable_record(record_id, partial):
    dict = {
        'id': record_id,
        'fields': partial,
    }

    return dict


def send_patch_request(airtable_token, airtable_id, airtable_name, patch):
    url = 'https://api.airtable.com/v0/%s/%s' % (airtable_id, airtable_name)
    headers = {
        'Authorization': 'Bearer %s' % airtable_token,
        'Content-Type': 'application/json',
    }
    data = json.dumps(patch)
    request = urllib2.Request(url, headers=headers, data=data)
    request.get_method = lambda: 'PATCH'
    response = None
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        print(e.readlines())
        return None

    return response.read()


def airtable_push(sisupath, new_data):
    token, table_id, table_name = unpack_file(sisupath)
    table = airtable_get(token, table_id, table_name)
    data = {
        'records': []
    }

    print('pushing %s item(s)...' % len(new_data))
    for x in new_data:
        print(x)

    for partial in new_data:
        row_id = get_row_id(table, partial['code'])
        data['records'].append(create_airtable_record(row_id, partial))

    return send_patch_request(token, table_id, table_name, data)
