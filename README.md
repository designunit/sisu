# SISU Sync for Rhino plugin

## Installation

0. Удалить предыдущую версию плагина в папке `%AppData%\Roaming\McNeel\Rhinoceros\6.0\Plug-ins\PythonPlugins`
1. Запустить `rhi`-файл
2. Перезапустить Райно
3. Выполнить команду `EditPythonScript`. Откроется окно с редактором. Его надо закрыть

## Commands

### `SisuSetup`

Привязывает `sisufile` к текущему файлу

### `SisuSync`

Cинхронизирует файл в соответствии с настройкой в привязаном `sisufile`

### `SisuClean`

Удаляет все производные слои

### `SisuLock`

Lock all derived sisu layers. Collapse layer tree. 

### `SisuUnlock`

Unlock all derived sisu layers.

### `SisuHide`

Скрывает все производные слои

### `SisuShow`

Включает все производные слои

`HatchRotation` - привязывает к контуру свойства создаваемой в нём штриховки (поворот, точку привязки)
`ExportLayers` - сохраняет свойства слоёв файла в формате csv

## Sisufile file format specification

### Sisufile version 0

```json
{
    "version": "0",
    "data": [
        {
            "layer": [
                "Default",
                {
                    "color": [255, 0, 0],
                    "lineType": "continuous",
                    "lineWeight": 1
                }
            ],
            "code": "X",
            "properties": {
                "patternRotation": 0,
                "patternBasePoint": [0, 0, 0]
            },
            "view": [
                {
                    "layerSuffix": "_SOLID",
                    "render": [
                        "hatch",
                        {
                            "pattern": "Solid",
                            "scale": 1,
                            "color": [10, 190, 10],
                            "lineWeight": 0.13
                        }
                    ]
                },
                {
                    "layerSuffix": "_HATCH",
                    "render": [
                        "hatch",
                        {
                            "pattern": "Grid",
                            "scale": 1,
                            "color": [0, 255, 0],
                            "lineWeight": 0.1
                        }
                    ]
                }
            ],
            "options": {}
        }
    ]
}
```

### Sisufile version 0.1

```json5
{
    "version": "0.1",

    // data is optional. skip if options.provider is exist and take data from data provider
    "data": [
        {
            "layer": ["Default", {
                "color": [255, 0, 0],
                "lineType": "continuous",
                "lineWeight": 1
            }],
            "code": "X",
            "properties": {
                "patternRotation": 0,
                "patternBasePoint": [0, 0, 0]
            },
            "view": [
                {
                    "layerSuffix": "_SOLID",
                    "render": ["hatch", {
                        "pattern": "Solid",
                        "scale": 1,
                        "color": [10, 190, 10],
                        "lineWeight": 0.13
                    }]
                },
                {
                    "layerSuffix": "_HATCH",
                    "render": ["hatch", {
                        "pattern": "Grid",
                        "scale": 1,
                        "color": [0, 255, 0],
                        "lineWeight": 0.1
                    }]
                }
            ],
            "options": {}
        }
    ],

    "options": {
        "provider": {
            "type": "airtable",
            "baseId": "<airtable_base_id>",
            "apiKey": "<airtable_api_key>",
            "table": "<airtable_table>",
            "columns": {
                "layer": "code",
                "code": "code",
                "color": "color",
                "lineWeight": "lineWeight",
                "lineType": "lineType",
                "solidColor": "solidColor",
                "pattern": "pattern",
                "patternScale": "patternScale",
                "patternColor": "patternColor",
                "patternLineWeight": "pattern"
            }
        }
    }
}
```

## Default colors

| Color       | Red | Green | Blue |
|-------------|-----|-------|------|
| Black       | 0	| 0 	| 0    |
| White       | 255	| 255 	| 255  |
| Medium Gray | 128	| 128 	| 128  |
| Aqua        | 0	| 128 	| 128  |
| Navy Blue   | 0	| 0 	| 128  |
| Green       | 0	| 255 	| 0    |
| Orange      | 255	| 165 	| 0    |
| Yellow      | 255	| 255 	| 0    |
