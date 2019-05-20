import scriptcontext as sc
import rhinoscriptsyntax as rs
import System
import Rhino
import json
import math


system_hatch_pattern_names = [
    'Dash',
    'Grid',
    'Grid60',
    'Hatch1',
    'Hatch2',
    'Hatch3',
    'Plus',
    'Solid',
    'Squares'
]


def load_system_hatch_patterns():
    for name in system_hatch_pattern_names:
        hatch_pattern = sc.doc.HatchPatterns.FindName(name)
        if not hatch_pattern:
            pattern = getattr(Rhino.DocObjects.HatchPattern.Defaults, name)
            hatch_pattern_index = sc.doc.HatchPatterns.Add(pattern)
            hatch_pattern = sc.doc.HatchPatterns.FindIndex(hatch_pattern_index)


def point3d(param):
    return Rhino.Geometry.Point3d(param[0], param[1], param[2])


def setup_layer(name, options):
    parent = options.get('parent', None)
    locked = options.get('locked', False)

    if not rs.IsLayer(name):
#        print('adding layer', parent, name)
        layer = rs.AddLayer(name=name, parent=parent, locked=locked)
    else:
        rs.ParentLayer(name, parent)
        layer = rs.LayerName(name)

    color = options.get('color', (0, 0, 0))
    print_width = options.get('lineWeight', 0)
    linetype = options.get('lineType', 'Continuous')

    rs.LayerColor(name, color)
    rs.LayerPrintWidth(name, print_width)
    rs.LayerLinetype(name, linetype)

    return layer


def get_user_text(obj, key, default_value=None, fn=None):
    val = rs.GetUserText(obj.Id, key)
    if not val:
        return default_value
    if not fn:
        return val
    return fn(val)


def bake_layer(from_layer, to_layer, options):
#    print('baking %s to %s' % (from_layer, to_layer))
    source_by_layer = 0
#    0 = By Layer
#    1 = By Object
#    3 = By Parent

    default_rotation = options['patternRotation']
    draw_order = options['drawOrder']

    xs = sc.doc.Objects.FindByLayer(from_layer)
    for x in xs:
        if x.ObjectType != Rhino.DocObjects.ObjectType.Curve:
            continue
            
        if not x.Geometry.IsClosed:
            continue

        if not x.Geometry.IsPlanar():
            continue

        rs.ObjectLinetypeSource(x.Id, source_by_layer)
        rs.ObjectColorSource(x.Id, source_by_layer)
        rs.ObjectPrintWidthSource(x.Id, source_by_layer)

        rotation = get_user_text(x, 'patternRotation', default_rotation, float)
        rotation = math.radians(rotation)
        base_point = get_user_text(x, 'patternBasePoint', None, json.loads)

        pattern = options['pattern']
        pattern_index = sc.doc.HatchPatterns.Find(pattern, True)
        scale = options['scale']
        target_layer_index = sc.doc.Layers.FindByFullPath(to_layer, True)

        hatches = Rhino.Geometry.Hatch.Create(x.Geometry, pattern_index, rotation, scale)
        for hatch in hatches:
            h = sc.doc.Objects.AddHatch(hatch)
            h = sc.doc.Objects.Find(h)
            h.Attributes.LayerIndex = target_layer_index
            h.Attributes.DisplayOrder = draw_order
            if base_point:
                h.HatchGeometry.BasePoint = point3d(base_point)
            h.CommitChanges()


def sync_code(code_def, sync_options):
    layer_name, layer_options = code_def['layer']
    setup_layer(layer_name, layer_options)

    current_view_layers = rs.LayerChildren(layer_name)
    for x in current_view_layers:
#        print('purging layer', x)
        rs.PurgeLayer(x)

    draw_order = 1
    for view in code_def['view']:
        view_layer_name = layer_name + view['layerSuffix']
        render_type, render_options = view['render']

        view_layer_options = {}
        view_layer_options.update(render_options)
        view_layer_options['parent'] = layer_name
        view_layer_options['locked'] = True
        view_layer_name = setup_layer(view_layer_name, view_layer_options)

        bake_options = {}
        bake_options.update(render_options)
        bake_options.update(code['properties'])
        bake_options['drawOrder'] = draw_order
        objects = bake_layer(layer_name, view_layer_name, bake_options)

        draw_order += 1

    rs.ExpandLayer(layer_name, False)


def get_sisufile():
    f = 'C:/Users/tmshv/Desktop/Projects/SisuSync/sisufile.json'
    return json.load(open(f, 'r'))

if __name__ == '__main__':
    load_system_hatch_patterns()

    config = get_sisufile()
    codes = config['code']

    options = {}
    add_code = True
    for code in codes:
        layer_name, layer_options = code['layer']
        if not rs.IsLayer(layer_name) and not add_code:
            continue
        sync_code(code, options)
    sc.doc.Views.Redraw()