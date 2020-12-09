import scriptcontext as sc
import rhinoscriptsyntax as rs
import System
import Rhino
import json
import math
from rhinolib import get_sisufile, get_user_text, find_layer_objects

__commandname__ = 'SisuSync'
system_hatch_pattern_names = [
    'Dash',
    'Grid',
    'Grid60',
    'Hatch1',
    'Hatch2',
    'Hatch3',
    'Plus',
    'Solid',
    'Squares',
]

KEY_ORIGIN = 'originId'
KEY_ROT = 'patternRotation'
KEY_BASEPOINT = 'patternBasePoint'


class HatchProxy:
    def __init__(self, hatch):
        self.hatch = hatch
        self.hash = None
        self.origin = None

    def set_origin(self, obj):
        self.origin = obj

    def apply_options(self, defaults):
        rotation = get_user_text(self.origin, KEY_ROT, None, float)
        if rotation:
            self.hatch.PatternRotation = math.radians(rotation)

        basepoint = get_user_text(self.origin, KEY_BASEPOINT, None, rs.coerce3dpoint)
        if basepoint:
            self.hatch.BasePoint = basepoint

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


def is_match_for_hatch_source(x):
    if x.ObjectType != Rhino.DocObjects.ObjectType.Curve:
        return False
    if not x.Geometry.IsClosed:
        return False
    if not x.Geometry.IsPlanar():
        return False
    return True


def is_hatch_pattern(x):
    is_hatch_object = x.ObjectType == Rhino.DocObjects.ObjectType.Hatch
    is_solid = rs.HatchPattern(x) == 'Solid'

    return is_hatch_object and not is_solid


def normalize_objects(objects):
    source = {
        'by_layer': 0,
        'by_object': 1,
        'by_parent': 3,
    }

    # Fix source layer objects
    for x in objects:
        rs.ObjectLinetypeSource(x.Id, source['by_layer'])
        rs.ObjectColorSource(x.Id, source['by_layer'])
        rs.ObjectPrintWidthSource(x.Id, source['by_layer'])


def get_modified_hatches(layer_name, defaults):
    rotation = defaults.get(KEY_ROT)
    base_point = defaults.get(KEY_BASEPOINT)
    base_point = point3d(base_point)
    objects = find_layer_objects(is_hatch_pattern, layer_name)
    result = []
    for obj in objects:
        hatch = obj.Geometry
        r = hatch.PatternRotation
        bp = hatch.BasePoint

        rotation_modified = r != rotation
        basepoint_modified = bp != base_point

        if rotation_modified or basepoint_modified:
            result.append(obj)
    return result


def save_hatch_options(obj, defaults):
    curve_id = rs.GetUserText(obj, KEY_ORIGIN)
    curve_id = rs.coerceguid(curve_id)
    curve_obj = sc.doc.Objects.FindId(curve_id)
    hatch = obj.Geometry

    rotation = math.degrees(hatch.PatternRotation)
    default_rotation = defaults.get(KEY_ROT)
    if rotation != default_rotation:
        rs.SetUserText(curve_id, KEY_ROT, rotation)

    basepoint = hatch.BasePoint
    default_basepoint = rs.coerce3dpoint(defaults.get(KEY_BASEPOINT))
    if basepoint != default_basepoint:
       rs.SetUserText(curve_id, KEY_BASEPOINT, basepoint.ToString())


def bake_layer(from_layer, to_layer, options):
    default_rotation = options[KEY_ROT]
    scale = options['scale']
    draw_order = options['drawOrder']
    pattern = options['pattern']
    target_layer_index = sc.doc.Layers.FindByFullPath(to_layer, True)
    pattern_index = sc.doc.HatchPatterns.Find(pattern, True)
    if pattern_index < 0:
        print('Hatch pattern %s does not exist' % pattern)
        return

    source_objects = find_layer_objects(is_match_for_hatch_source, from_layer)
    if len(source_objects) == 0:
        print('Layer %s has no objects to bake' % from_layer)
        return

    normalize_objects(source_objects)
    custom_hatch_objects = get_modified_hatches(to_layer, options)
    for h in custom_hatch_objects:
        save_hatch_options(h, options)
    rs.PurgeLayer(to_layer)

    curves = [x.Geometry for x in source_objects]
    tolerance = sc.doc.ModelAbsoluteTolerance
    hatches = Rhino.Geometry.Hatch.Create(curves, pattern_index, default_rotation, scale, tolerance)
    proxies = [HatchProxy(x) for x in hatches]

    # bind main curve to created hatch
    for obj in source_objects:
        hp = find_by_bounding_box(proxies, obj.Geometry.GetBoundingBox(True))
        if not hp:
            continue
        hp.set_origin(obj)

    # Add created hatches to rhino doc + set attributes
    for hp in proxies:
        hp.apply_options(defaults=options)
        
        hatch = hp.hatch
        hatch_guid = sc.doc.Objects.AddHatch(hatch)
        hatch_obj = sc.doc.Objects.Find(hatch_guid)

        # save origin curve in hatch user text
        rs.SetUserText(hatch_obj, KEY_ORIGIN, hp.origin.Id)

        hatch_obj.Attributes.LayerIndex = target_layer_index
        hatch_obj.Attributes.DisplayOrder = draw_order
        hatch_obj.CommitChanges()


def sync_code(code_def, sync_options):
    layer_name, layer_options = code_def['layer']
    setup_layer(layer_name, layer_options)

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


def get_sync_options(modes):
    gp = Rhino.Input.Custom.GetOption()
    gp.SetCommandPrompt(__commandname__)
    gp.AcceptNothing(True)

    mode_index = 0
    mode_op = gp.AddOptionList('Mode', modes, mode_index)

    while True:
        result = gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return None, gp.CommandResult()

        i = gp.OptionIndex()
        if i == -1:
            break
        elif i == mode_op:
            mode_index = gp.Option().CurrentListOptionIndex
            continue

    options = {
        'mode': modes[mode_index],
    }
    return options, Rhino.Commands.Result.Success


def RunCommand( is_interactive ):
    load_system_hatch_patterns()
    config = get_sisufile()
    if not config:
        print('Sisufile not configured')
        return Rhino.Commands.Result.Failure
    codes = config['data']

    mode_full = 'Full'
    mode_existing = 'Existing'
    mode_current = 'Current'
    modes = (mode_existing, mode_current, mode_full)

    user_options, status = get_sync_options(modes)
    if status != Rhino.Commands.Result.Success:
        return status

    add_layer_enabled = user_options['mode'] == mode_full
    layer_scope = []
    if user_options['mode'] == mode_current:
        layer_scope = [rs.CurrentLayer()]
    else:
        layer_scope = rs.LayerNames()
    
    options = {}
    rs.EnableRedraw(False)
    for code in codes:
        layer_name, layer_options = code['layer']
        layer_exists = rs.IsLayer(layer_name)
        valid_layer = (layer_name in layer_scope) or (not layer_exists and add_layer_enabled)
        if not valid_layer:
            continue

        try:
            sync_code(code, options)
        except Exception as e:
            print('failed to sync %s: %s' % (code['code'], e))

    rs.EnableRedraw(True)
    sc.doc.Views.Redraw()

    return Rhino.Commands.Result.Success


if __name__ == '__main__':
    RunCommand(None)
