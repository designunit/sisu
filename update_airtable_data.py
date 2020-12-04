import json
import requests


# нужно для тестирования. на данном этапе инфа загружается из файла
def unpack_file(filepath):
    file = json.load(open(filepath, 'r'))

    token = file.get('options').get('provider').get('apiKey')
    id = file.get('options').get('provider').get('baseId')
    table_name = file.get('options').get('provider').get('table')

    return token, id, table_name


def get_row_id(table_dict, code):
    for value in table_dict['records']:
        if value['fields']['code'] == '%s' % code:
            return value['id']


def update_airtable(airtable_token, airtable_id, airtable_name, line_id, column_name, cell_value):
    headers = {
        'Authorization': '%s' % airtable_token,
        'Content-Type': 'application/json',
    }

    data = {
        "records": [
            {
                "id": "%s" % line_id,
                "fields": {
                    "%s" % column_name: "%s" % cell_value,
                }
            }
        ]
    }

    requests.patch('https://api.airtable.com/v0/%s/%s' % (airtable_id, airtable_name), headers=headers,
                   data=json.dumps(data))


def get_data_from_airtable(airtable_token, airtable_id, airtable_name):
    headers = {
        'Authorization': '%s' % airtable_token,
    }

    response = requests.get('https://api.airtable.com/v0/%s/%s' % (airtable_id, airtable_name), headers=headers)
    return response.json()


list_of_changes = [
    {
        'code': 'B_BKb',
        'column': 'name',
        'change': 'fsjadhfas'
    },
    {
        'code': 'B_BKp',
        'column': 'name',
        'change': '34534'
    }

]

token, table_id, table_name = unpack_file('update_airtable.json')

for element in list_of_changes:
    table_data = get_data(token, table_id, table_name)
    id = get_row_id(table_data, element['code'])
    update_airtable(token, table_id, table_name, id, element['column'], element['change'])
