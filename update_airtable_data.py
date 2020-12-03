import json
import requests
from airtable.airtable import Airtable


def unpack_file(filepath):
    file = json.load(open(filepath, 'r'))

    token = file.get('options').get('provider').get('apiKey')
    id = file.get('options').get('provider').get('baseId')
    table_name = file.get('options').get('provider').get('table')

    return token, id, table_name


def update_airtable(airtable_token, airtable_id, airtable_name, column_name, cell_value):
    # airtable = Airtable(airtable_id, airtable_name, airtable_token)
    # record = airtable.match('code', 'B_BKb')
    # fields = {column_name: cell_value}
    # airtable.update(record['id'], fields)
    # # print(airtable.get_all())

    headers = {
        'Authorization': '%s' % airtable_token,
        'Content-Type': 'application/json',
    }

    data = {
        "records": [
            {
                "id": "recbzCbB1csb82W4N",
                "fields": {
                    '%s' % column_name: '%s' % cell_value,
                    "name": "2134",
                    "units": "m",
                    "size": "Ш=200, В=min 300, Д=500-1000",
                    "description": "бордюр в плоскости мощения, гранит",
                    "color": "#78683d",
                    "lineWeight": 0.35,
                    "lineType": "continuous",
                    "img": [
                        {
                            "id": "attDJYI4TkrbtJkrV"
                        }
                    ],
                    "type": [
                        "border"
                    ],
                    "dc": [
                        "recJxp78T2qeIBX11"
                    ]
                }
            }
        ]
    }



    response = requests.patch('https://api.airtable.com/v0/appwLoUM2FeZap2P4/Pitkyaranta_test', headers=headers,
                              data=data)
    table_json = response.json()

token, id, name = unpack_file('update_airtable.json')
update_airtable(token, id, name, 'name', 'value')
