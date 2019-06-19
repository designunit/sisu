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

### `SisuHide`

Скрывает все производные слои

### `SisuShow`

Включает все производные слои

`HatchRotation` - привязывает к контуру свойства создаваемой в нём штриховки (поворот, точку привязки)
`ExportLayers` - сохраняет свойства слоёв файла в формате csv

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
