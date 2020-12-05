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

# main func for update airtable data
def update_airtable(airtable_token, airtable_id, airtable_name, patch):
    headers = {
        'Authorization': airtable_token,
        'Content-Type': 'application/json',
    }

    request = urllib2.Request('https://api.airtable.com/v0/%s/%s' % (airtable_id, airtable_name), headers=headers,
                              data=json.dumps(patch))
    request.get_method = lambda: 'PATCH'
    urllib2.urlopen(request)