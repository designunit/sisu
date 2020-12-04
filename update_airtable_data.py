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


def get_data_from_airtable(airtable_token, airtable_id, airtable_name):
    headers = {
        'Authorization': '%s' % airtable_token,
    }

    response = requests.get('https://api.airtable.com/v0/%s/%s' % (airtable_id, airtable_name), headers=headers)
    return response.json()


def render_patch_dict(data_dict, row_dict):
    data_dict['records'].append(
        {
            "id": "%s" % row_dict['id'],
            "fields": {
                "code": "%s" % row_dict['code'],
                "color": "%s" % row_dict['color'],
                'pattern': row_dict['pattern'],
            }
        }
    )
    return data_dict


def update_airtable(airtable_token, airtable_id, airtable_name, patch):
    headers = {
        'Authorization': '%s' % airtable_token,
        'Content-Type': 'application/json',
    }

    requests.patch('https://api.airtable.com/v0/%s/%s' % (airtable_id, airtable_name), headers=headers,
                   data=json.dumps(patch))


token, table_id, table_name = unpack_file('update_airtable.json')

if __name__ == '__main__':
    patch = {

        'records': []
    }

    data_list = [
        {
            'code': 'B_BKb',
            'color': 'цвет изменен',
            'pattern': 'хач 43671',
        },
        {
            'code': 'B_BKp',
            'color': 'цвет изменен еще раз',
            'pattern': 'хач 3',
        }

    ]

    for element in data_list:
        table_data = get_data_from_airtable(token, table_id, table_name)
        element['id'] = get_row_id(table_data, element['code'])
        data_dict = render_patch_dict(patch, element)

    update_airtable(token, table_id, table_name, patch)
