# -*- coding: utf-8 -*-

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
from rhinolib import get_sisufile, get_sisufile_path
from sisulib import get_related_layers, sisufile_update_data
from update_airtable_data import airtable_push
import json
import csv


__commandname__ = 'SisuPush'


class ConfigBuilder:
    def __init__(self):
        pass

    def build(self, items):
        layers = []
        for f in items:
            code = f.get('code')
            if not code:
                continue
            layers.append({
                'layer':
                    [code, {
                        'color': f.get('color', [0, 0, 0]),
                        'lineType': f.get('lineType', 'continuous'),
                        'lineWeight': f.get('lineWeight', 1)
                    }],
                'code': code,
                'properties': {
                    'patternRotation': 0,
                    'patternBasePoint': [0, 0, 0]
                },
                'view': self.create_views(f)
            })
        return layers

    def create_views(self, record):
        views = []
        if 'solidColor' in record:
            views.append(self.create_solid_view(record))
        if 'pattern' in record:
            views.append(self.create_hatch_view(record))
        return views

    def create_solid_view(self, record):
        return {
            'layerSuffix': '_SOLID',
            'render': ['hatch', {
                'pattern': 'Solid',
                'scale': 1,
                'color': record.get('solidColor', [0, 0, 0]),
                'lineWeight': 0.13
            }, ]
        }

    def create_hatch_view(self, record):
        return {
            'layerSuffix': '_HATCH',
            'render': ['hatch', {
                'pattern': record.get('pattern', 'Grid'),
                'scale': float(record.get('patternScale', 1)),
                'color': record.get('patternColor', [0, 0, 0]),
                'lineWeight': float(record.get('patternLineWeight', 0.13)),
            }]
        }


def is_hatch(obj):
    return type(obj).__name__ == 'HatchObject'


def get_objects(layer):
    return sc.doc.Objects.FindByLayer(layer)


def get_hatches(layer):
    return [x
        for x in get_objects(layer)
        if is_hatch(x)
    ]


def get_color(c):
    if type(c) == list:
        rgb = tuple(c)
    else:
        rgb = (c.R, c.G, c.B)
    r = '#%02.x%02.x%02.x' % rgb
    return r
    # return [c.R, c.G, c.B]


def get_layer_config(layer_name, defaults):
    conf = {}

    print_color = rs.LayerPrintColor(layer_name)
    color = get_color(print_color)
    if color != get_color(defaults.get('color')):
        conf['color'] = color

    print_width = rs.LayerPrintWidth(layer_name)
    if print_width != defaults.get('lineWeight'):
        conf['lineWeight'] = print_width

    line_type = rs.LayerLinetype(layer_name).lower()
    if line_type != defaults.get('lineType'):
        conf['lineType'] = line_type

    return conf


def get_solid_view_config(layer_name, defaults):
    conf = {}

    print_color = rs.LayerPrintColor(layer_name)
    solid_color = get_color(print_color)
    if solid_color != get_color(defaults.get('color')):
        conf['solidColor'] = solid_color
    return conf


def get_pattern_view_config(layer_name, defaults):
    conf = {}

    print_color = rs.LayerPrintColor(layer_name)
    pattern_color = get_color(print_color)
    if pattern_color != get_color(defaults.get('color')):
        conf['patternColor'] = pattern_color

    print_width = rs.LayerPrintWidth(layer_name)
    if print_width != defaults.get('lineWeight'):
        conf['patternLineWeight'] = print_width

    hs = get_hatches(layer_name)
    if len(hs) > 0:
        h = hs[0]
        pattern = rs.HatchPattern(h.Id)
        if pattern != defaults.get('pattern'):
            conf['pattern'] = pattern

        scale = rs.HatchScale(h.Id)
        if scale != defaults.get('scale'):
            conf['patternScale'] = scale
    return conf


def is_solid_view(view):
    render_type, render_options = view['render']
    return render_type == 'hatch' and render_options['pattern'] == 'Solid'


def RunCommand( is_interactive ):
    config = get_sisufile()
    if not config:
        print('Sisufile not configured')
        return Rhino.Commands.Result.Failure
    codes = config['data']

    out = [] 
    for code in codes:
        conf = {}
        layer_name, layer_options = code['layer']
        if not rs.IsLayer(layer_name):
            continue

        try:
            layer_conf = get_layer_config(layer_name, layer_options)
            conf.update(layer_conf)
        except Exception as e:
            print('Failed to dump layer %s' % layer_name)
            print(e)

        for view in code['view']:
            view_layer_name = layer_name + view['layerSuffix']
            render_type, render_options = view['render']
            if is_solid_view(view):
                solid_conf = get_solid_view_config(view_layer_name, render_options)
                conf.update(solid_conf)
            else:
                pattern_conf = get_pattern_view_config(view_layer_name, render_options)
                conf.update(pattern_conf)

        if conf:
            conf['code'] = layer_name
            out.append(conf)

#    builder = ConfigBuilder()
#    new_data = builder.build(out)

#    sisu_path = get_sisufile_path()
#    sisufile_update_data(sisu_path, new_data)

    path = get_sisufile_path()
    airtable_push(path, out)

    return Rhino.Commands.Result.Success


if __name__ == '__main__':
    RunCommand(None)
