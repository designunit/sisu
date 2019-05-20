
import scriptcontext as sc
import rhinoscriptsyntax as rs
import System
import Rhino

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

#layer_index = sc.doc.Layers.Add(layer_name, System.Drawing.Color.Black)
#layer = sc.doc.Layers.Find(layer_name, True)

#layer = sc.doc.Layers.Item[0]

#for x in dir(rs):
#    print(x)

#print(dir(Rhino.DocObjects.Tables))
#hpt = Rhino.DocObjects.Tables.HatchPatternTable
#print(dir(hpt))
#print(hpt.Item[0])
#for x in xrange(hpt.Count)):
#    print(x)


#doc.HatchPatterns.Find(hatch_name, True)
#for x in sc.doc.HatchPatterns:
#    print(x)

#f = 'C:\\Users\\tmshv\\Downloads\\hatchpatterns_1033.pat'
#xs = rs.AddHatchPatterns(f)
#print(xs)
#for x in xs:
#    print(x)
#print(rs.AddHatchPatterns())

def setup_layer(name, options):
    parent = options.get('parent', None)
    locked = options.get('locked', False)

    if not rs.IsLayer(name):
        layer = rs.AddLayer(name=name, parent=parent, locked=locked)
    else:
        layer = rs.LayerName(name)

    color = options.get('color', (0, 0, 0))
    print_width = options.get('lineWeight', 0)
    linetype = options.get('lineType', 'Continuous')

    rs.LayerColor(name, color)
    rs.LayerPrintWidth(name, print_width)
    rs.LayerLinetype(name, linetype)
    
    return layer

    #print(type(main_layer))
    #x = sc.doc.Layers.FindIndex(1)
    #print(x)


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

#        print(options)
#        print('type', type(x).__name__)
#        print('ObjectType', x.ObjectType)
#        print('GeometryType', type(x.Geometry).__name__)
#        print('')

        pattern = options['pattern']
        scale = options['scale']
        hatch_guid = rs.AddHatch(x.Id, pattern, scale=scale, rotation=rotation)
        rs.ObjectLayer(hatch_guid, to_layer)

        hatch = sc.doc.Objects.Find(hatch_guid)
        hatch.Attributes.DisplayOrder = draw_order
        hatch.CommitChanges()

#import rhinoscriptsyntax as rs
# |   curves = rs.GetObjects("Select closed planar curves", rs.filter.curve)
# |        if curves:
# |                if rs.IsHatchPattern("Grid"):
# |                    rs.AddHatches( curves, "Grid" )
# |                else:
# |                    rs.AddHatches( curves, rs.CurrentHatchPattern() )

#import rhinoscriptsyntax as rs
# |            circle = rs.AddCircle(rs.WorldXYPlane(), 10.0)
# |            if rs.IsHatchPattern("Grid"):
# |                rs.AddHatch( circle, "Grid" )
# |            else:
# |                rs.AddHatch( circle, rs.CurrentHatchPattern() )


#import Rhino
# 
#if (curve and curve.IsClosed and curve.IsPlanar()):
#    hatches = Rhino.Geometry.Hatch.Create(curve, 0, 0, 1)
#    
# for hatch in hatches:
#         scriptcontext.doc.Objects.AddHatch(hatch)

def set_layer_draw_order(layer_name, value):
#    m_line_objects[1].Attributes.DisplayOrder = 1
#    m_line_objects[1].CommitChanges()
#    doc.Views.Redraw()
#    Pause("Second (blue) line now in front.  Any key to continue ...")

    xs = sc.doc.Objects.FindByLayer(layer_name)
    print(layer_name, xs)
#    for obj in xs:
#        print(obj, value)
#        guid = doc.Objects.AddLine(from_pt, to_pt)
#        obj = doc.Objects.Find(guid)
#        obj.Attributes.DisplayOrder = value
#        obj.Attributes.ObjectColor = color
#        obj.Attributes.ColorSource = ObjectColorSource.ColorFromObject
#        obj.CommitChanges()

#    for i in range(1, m_line_objects.Count):
#        m_line_objects[i].Attributes.DisplayOrder = i
#        m_line_objects[i].CommitChanges()
#
#    doc.Views.Redraw()


def sync_code(code_def, sync_options):
    layer_name, layer_options = code_def['layer']
    setup_layer(layer_name, layer_options)

    current_view_layers = rs.LayerChildren(layer_name)
    for x in current_view_layers:
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
        bake_layer(layer_name, view_layer_name, bake_options)
        
#        set_layer_draw_order(view_layer_name, draw_order)
        draw_order += 1
        
    rs.ExpandLayer(layer_name, False)
    
def get_sisufile():
    import json
    f = 'C:/Users/tmshv/Desktop/Projects/SisuSync/sisufile.json'
    return json.load(open(f, 'r'))

if __name__ == '__main__':
    load_system_hatch_patterns()
#    print('Patterns:')
#    for x in rs.HatchPatternNames():
#        print(x)
#
#    print('rs.CurrentHatchPattern()', rs.CurrentHatchPattern())
#    print('rs.IsHatchPattern("Grid")', rs.IsHatchPattern("Grid"))
    
    config = get_sisufile()
    codes = config['code']

    options = {}
    add_code = True
    for code in codes:
        layer_name, layer_options = code['layer']
        if not rs.IsLayer(layer_name) and not add_code:
            continue
        sync_code(code, options)
