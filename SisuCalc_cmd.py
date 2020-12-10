# -*- coding: utf-8 -*-

import rhinoscriptsyntax as rs
import scriptcontext as sc
import json
import csv
import Rhino
from collections import Counter

sisu_layer = 'SISU'

def save_sisu_calc_report(report, filename):
    fields = ['code', 'name', 'value', 'units']
    # open in wb mode to ignore windows line endings
    with open(filename, 'wb') as f:
        w = csv.DictWriter(f, delimiter=',', fieldnames=fields)
        w.writeheader()
        for code, x in report.items():
            name, value, units = x
            w.writerow({
                'code': code,
                'value': value,
                'units': units,
                'name': name,
            })


def get_dc(filepath):
    with open(filepath, 'r') as f:
        r = csv.DictReader(f)
        return [x
            for x in r
            if x.get('code') != ''
        ]


def is_hatch(obj):
#    print(obj)
    return type(obj).__name__ == 'HatchObject'


def get_objects(layer):
    objects = sc.doc.Objects.FindByLayer(layer)
    if not objects:
        objects = []
    return objects


def type_filter(t):
    return lambda x: type(x).__name__ == t


def geometry_filter(t):
    return lambda x: type(x.Geometry).__name__ == t


def any_filter(filters):
    def f(x):
        for f in filters:
            if f(x):
                return True
        return False
    return f


def filter_objects(layer, filter_fn):
    xs = sc.doc.Objects.FindByLayer(layer)
    if not xs:
        return []
    return [x for x in xs if filter_fn(x)]


def get_hatches(layer):
    return [x
        for x in get_objects(layer)
        if is_hatch(x)
    ]


def create_hatches(curves):
    """
    curves is o.Geometry items
    """
    scale = 1
    rotation = 0
    pattern = 'Solid'
    pattern_index = sc.doc.HatchPatterns.Find(pattern, True)
    if pattern_index < 0:
        print('Hatch pattern does not exist')
        return None

    return Rhino.Geometry.Hatch.Create(curves, pattern_index, rotation, scale)


def get_blocks(layer):
    return [x
        for x in get_objects(layer)
        if type(x).__name__ == 'InstanceObject'
    ]


def get_curve_length(curve):
    return curve.GetLength()


def is_linear(code):
    """
    should be defined as M for units and has a fill pattern in DC 
    """
    is_m = code['units'] == 'm'
    has_pattern = 'pattern' in code
    return is_m and has_pattern


def is_simple_linear(code):
    return not is_linear(code)


def calc_simple_linear_size(obj):
    """
    simple linear size is just a length of a curve
    """
    return get_curve_length(obj.Geometry)


def calc_linear_size(obj):
    """
    split closed curve to two segments by shortest parts
    linear size is a half of sum of length of this two segments
    """
    curve = obj.Geometry
    pieces = curve.DuplicateSegments() # same as Explode in rhino
    pieces = sorted(pieces, key=get_curve_length)
    pieces = pieces[2:] # skip two smallest parts

    t = sum([get_curve_length(x)
        for x in pieces
    ])
    return t / 2

#    curves = [rhutil.coercecurve(id, -1, True) for id in object_ids]
#    if tolerance is None:
#        tolerance = 2.1 * scriptcontext.doc.ModelAbsoluteTolerance
#    newcurves = Rhino.Geometry.Curve.JoinCurves(curves, tolerance)


#layers = [x
#    for x in rs.LayerNames()
#    if rs.IsLayerChildOf(sisu_layer, x)
#]


#dc = get_dc('C:/Users/tmshv/Desktop/Projects/dc-data/DC-DERBENT-OUT.csv')
#dc = get_dc('C:/Users/tmshv/Desktop/Projects/UNIT/Derbent/DERBENT-DC.csv')
dc = get_dc('C:/Users/tmshv/Desktop/Projects/UNIT/Derbent/20201018-derbent_dc.csv')
out = []
failed_objects = []
result = {}
for item in dc:
    name = item.get('name', '')
    code = item.get('code')
    if not code:
        print('failed to process item: code not found')
    units = item.get('units')
    if not units:
        print('failed to process dc item: units not specified')

#     layer_name = 'SISU::'+code
    layer_name = code

    if units == 'pcs':
        blocks = get_blocks(code)
        block_names = [b.InstanceDefinition.Name for b in blocks]
        c = Counter(block_names)
        for n, v in c.items():
            result[n] = (name, v, units)
        print(code, units, len(blocks), c.items())

    if units == 'm2':
        objs = filter_objects(code, any_filter([
            geometry_filter('PolylineCurve'),
            geometry_filter('PolyCurve'),
            geometry_filter('NurbsCurve'),
        ]))
        print(code, 'curves', len(objs))
        hatches = create_hatches([o.Geometry for o in objs])
        total_area = 0
        geometry = [o.Geometry for o in objs]
        geometry = hatches
        for g in geometry:
            try:
                amp = Rhino.Geometry.AreaMassProperties.Compute(g)
                a = amp.Area
                total_area += a
            except Exception as e:
                print('failed to calculate area of', g, e)
#                failed_objects.append(o)
        print(code, units, 'area:', total_area)
        result[code] = (name, total_area, units)

    if units == 'm':
#        objs = filter_objects(code, type_filter('CurveObject'))
        objs = filter_objects(code, any_filter([
            geometry_filter('PolylineCurve'),
            geometry_filter('PolyCurve'),
            geometry_filter('NurbsCurve'),
        ]))
        total_length = 0
        if is_simple_linear(item):
            print('use simple linear calc', code)
            total_length = sum([calc_simple_linear_size(o)
                for o in objs
            ])
        elif is_linear(item):
            print('use linear calc for objects with area', code)
            for o in objs:
                if not o.Geometry.IsClosed:
                    print('failed to calculate linear dimension: geometry is not closed')
                    failed_objects.append(o)
                    continue
                l = calc_linear_size(o)
                total_length += l
        else:
            print('cannot calc length: dc is not configured properly', code)
        print(code, units, 'length:', total_length)
        result[code] = (name, total_length, units)
#    l = rs.LayerId(layer_name)
#    print(code, l)

if len(failed_objects) > 0:
    print('failed to calc. need some work')
    rs.SelectObjects([x.Id for x in failed_objects])
#    for obj in failed_objects:
#        rs.ObjectName(obj.Id, 'failed')
else:
    print('saving to file...')
    save_sisu_calc_report(result, 'C:/Users/tmshv/Desktop/Projects/UNIT/Derbent/20201018-DERBENT_CALC.csv')
#    try:
#        conf = get_layer_config(code)
#        conf.update(item)
#        out.append(conf)
#    except Exception as e:
#        print('DC failed. Fill defaults', code, e)
##        conf.update(default_config)
