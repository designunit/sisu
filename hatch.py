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


class HatchProxy:
    def __init__(self, hatch):
        self.hatch = hatch
        self.hash = None

    def get_hash(self):
        if not self.hash:
            self.hash = get_bounding_box_hash(self.hatch.GetBoundingBox(True))
        return self.hash


def load_system_hatch_patterns():
    for name in system_hatch_pattern_names:
        hatch_pattern = sc.doc.HatchPatterns.FindName(name)
        if not hatch_pattern:
            pattern = getattr(Rhino.DocObjects.HatchPattern.Defaults, name)
            hatch_pattern_index = sc.doc.HatchPatterns.Add(pattern)
            hatch_pattern = sc.doc.HatchPatterns.FindIndex(hatch_pattern_index)


def point3d(param):
    return Rhino.Geometry.Point3d(param[0], param[1], param[2])


def get_bounding_box_hash(bb):
    n = 10
    ns = [
        bb.Min.X, bb.Min.Y, bb.Min.Z,
        bb.Max.X, bb.Max.Y, bb.Max.Z,
        bb.Area,
    ]
    return '+'.join([str(round(x, n)) for x in ns])


def find_by_bounding_box(items, bb):
    hash = get_bounding_box_hash(bb)
    for x in items:
        if hash == x.get_hash():
            return x
    return None


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


def get_layer_objects(layer_name, match_fn):
    xs = sc.doc.Objects.FindByLayer(layer_name)
    return [x for x in xs if match_fn(x)]


def is_match_for_hatch_source(x):
    if x.ObjectType != Rhino.DocObjects.ObjectType.Curve:
        return False
    if not x.Geometry.IsClosed:
        return False
    if not x.Geometry.IsPlanar():
        return False
    return True


def get_custom_objects(objects, options):
    default_rotation = options['patternRotation']
    default_base_point = point3d(options['patternBasePoint'])
    result = []
    for x in objects:
        attrs = {}
        rotation = get_user_text(x, 'patternRotation', None, float)
        if rotation or rotation == default_rotation:
            attrs['patternRotation'] = math.radians(rotation)
        base_point = get_user_text(x, 'patternBasePoint', None, json.loads)
        if base_point and base_point != default_base_point:
            attrs['patternBasePoint'] = point3d(base_point)
        if attrs:
            result.append((x, attrs))
    return result


def bake_layer(from_layer, to_layer, options):
#    print('baking %s to %s' % (from_layer, to_layer))
    source_by_layer = 0
#    0 = By Layer
#    1 = By Object
#    3 = By Parent

    default_rotation = options['patternRotation']
    scale = options['scale']
    draw_order = options['drawOrder']
    pattern = options['pattern']
    target_layer_index = sc.doc.Layers.FindByFullPath(to_layer, True)
    pattern_index = sc.doc.HatchPatterns.Find(pattern, True)
    if pattern_index < 0:
        print('Hatch pattern does not exist')
        return

    source_objects = get_layer_objects(from_layer, is_match_for_hatch_source)

    # Fix source layer objects
    for x in source_objects:
        rs.ObjectLinetypeSource(x.Id, source_by_layer)
        rs.ObjectColorSource(x.Id, source_by_layer)
        rs.ObjectPrintWidthSource(x.Id, source_by_layer)

    curves = [x.Geometry for x in source_objects]
    hatches = Rhino.Geometry.Hatch.Create(curves, pattern_index, default_rotation, scale)

    custom_objects = get_custom_objects(source_objects, options)
    proxies = [HatchProxy(x) for x in hatches]
    for x, attrs in custom_objects:
        rotation = attrs.get('patternRotation')
        base_point = attrs.get('patternBasePoint')
        target = find_by_bounding_box(proxies, x.Geometry.GetBoundingBox(True))
        print('find hatch', attrs, target is not None)

        if not target:
            continue

        if rotation:
            target.hatch.PatternRotation = rotation
        if base_point:
            target.hatch.BasePoint = base_point

    # Add created hatches to rhino doc + set attributes
    for hatch in hatches:
        hatch_guid = sc.doc.Objects.AddHatch(hatch)
        hatch_obj = sc.doc.Objects.Find(hatch_guid)
        hatch_obj.Attributes.LayerIndex = target_layer_index
        hatch_obj.Attributes.DisplayOrder = draw_order
        hatch_obj.CommitChanges()


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
        bake_options.update(code_def['properties'])
        bake_options['drawOrder'] = draw_order
        objects = bake_layer(layer_name, view_layer_name, bake_options)

        draw_order += 1

    rs.ExpandLayer(layer_name, False)


def get_sync_options():
    return {
        'add_layer': True,
    }, Rhino.Commands.Result.Success


    gp = Rhino.Input.Custom.GetOption()
    gp.SetCommandPrompt('SisuSync')

#    intOption = Rhino.Input.Custom.OptionInteger(1, 1, 99)
#    dblOption = Rhino.Input.Custom.OptionDouble(2.2, 0, 99.9)
    add_missing_layer = Rhino.Input.Custom.OptionToggle(True, 'Yes', 'No')
#    listValues = "Item0", "Item1", "Item2", "Item3", "Item4"

#    gp.AddOptionInteger("Integer", intOption)
#    gp.AddOptionDouble("Double", dblOption)
    gp.AddOptionToggle('Add', add_missing_layer)
#    listIndex = 3
#    opList = gp.AddOptionList("List", listValues, listIndex)
#    while True:
    # perform the get operation. This will prompt the user to
    # input a point, but also allow for command line options
    # defined above
    result = gp.Get()

    if gp.CommandResult() != Rhino.Commands.Result.Success:
        return None, gp.CommandResult()

#        print " Integer =", intOption.CurrentValue
#        print " Double =", dblOption.CurrentValue

    options = {
        'add_layer': add_missing_layer.CurrentValue,
    }

#        print " List =", listValues[listIndex]
#        if get_rc==Rhino.Input.GetResult.Point:
#            point = gp.Point()
#            scriptcontext.doc.Objects.AddPoint(point)
#            scriptcontext.doc.Views.Redraw()
#            print "Command line option values are"
#            print " Integer =", intOption.CurrentValue
#            print " Double =", dblOption.CurrentValue
#            print " Boolean =", boolOption.CurrentValue
#            print " List =", listValues[listIndex]
#        elif get_rc==Rhino.Input.GetResult.Option:
#            if gp.OptionIndex()==opList:
#              listIndex = gp.Option().CurrentListOptionIndex
#            continue
#        break
    return options, Rhino.Commands.Result.Success


def get_sisufile():
    f = 'C:/Users/tmshv/Desktop/Projects/SisuSync/sisufile.json'
    return json.load(open(f, 'r'))


def main():
    load_system_hatch_patterns()

    config = get_sisufile()
    codes = config['code']

    user_options, status = get_sync_options()
    print(user_options, status)

    if status != Rhino.Commands.Result.Success:
        return

    options = {}
    for code in codes:
        layer_name, layer_options = code['layer']
        if not rs.IsLayer(layer_name) and not user_options['add_layer']:
            continue
        sync_code(code, options)
    sc.doc.Views.Redraw()


if __name__ == '__main__':
    main()