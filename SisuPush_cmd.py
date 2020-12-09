# -*- coding: utf-8 -*-

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
from rhinolib import get_sisufile, get_sisufile_path
from sisulib import get_related_layers
from sync import sisufile_update_data
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
    r = '#%02.x%02.x%02.x' % (c.R, c.G, c.B)
    return r
    # return [c.R, c.G, c.B]


def get_layer_config(layer_name):
    print_color = rs.LayerPrintColor(layer_name)
    print_width = rs.LayerPrintWidth(layer_name)
    line_type = rs.LayerLinetype(layer_name)

    conf = {
        'code': layer_name,
        'color': get_color(print_color),
        # 'lineWeight': '%.2f' % print_width,
        'lineWeight': print_width,
        'lineType': line_type.lower(),
    }
    hs = get_hatches(layer_name)
    if len(hs) > 0:
        h = hs[0]
        pattern = rs.HatchPattern(h.Id)
        is_solid = pattern == 'SOLID'
        if is_solid:
            conf['solidColor'] = get_color(print_color)
        else:
            conf['pattern'] = pattern
            conf['patternScale'] = 1
            conf['patternColor'] = get_color(print_color)
            # conf['patternLineWeight'] = '%.2f' % print_width
            conf['patternLineWeight'] = print_width
    return conf


def get_solid_view_config(layer_name):
    print_color = rs.LayerPrintColor(layer_name)
    conf = {
        'solidColor': get_color(print_color),
    }
    return conf


def get_pattern_view_config(layer_name):
    print_color = rs.LayerPrintColor(layer_name)
    print_width = rs.LayerPrintWidth(layer_name)
    conf = {}
    hs = get_hatches(layer_name)
    if len(hs) > 0:
        h = hs[0]
        pattern = rs.HatchPattern(h.Id)
        scale = rs.HatchScale(h.Id)
        conf['pattern'] = pattern
        conf['patternScale'] = scale
        conf['patternColor'] = get_color(print_color)
        conf['patternLineWeight'] = '%.2f' % print_width
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

    # default_config = {
    #     'color': '#000000',
    #     'lineWeight': '0.18',
    #     'lineType': 'continuous',
    # }

    out = [] 
    for code in codes:
        conf = {}
        layer_name, layer_options = code['layer']
        if not rs.IsLayer(layer_name):
            continue

        try:
            layer_conf = get_layer_config(layer_name)
            conf.update(layer_conf)
        except Exception:
            print('Failed to dump layer %s', layer_name)

        for view in code['view']:
            view_layer_name = layer_name + view['layerSuffix']
            if is_solid_view(view):
                solid_conf = get_solid_view_config(view_layer_name)
                conf.update(solid_conf)
            else:
                pattern_conf = get_pattern_view_config(view_layer_name)
                conf.update(pattern_conf)

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
