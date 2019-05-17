import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
import System.Guid, System.Drawing.Color
import json


def get_sync_options():
    gp = Rhino.Input.Custom.GetOption()
    gp.SetCommandPrompt('CodeSync')

    # set up the options
#    intOption = Rhino.Input.Custom.OptionInteger(1, 1, 99)
#    dblOption = Rhino.Input.Custom.OptionDouble(2.2, 0, 99.9)
    boolOption = Rhino.Input.Custom.OptionToggle(True, "No", "Yes")
#    listValues = "Item0", "Item1", "Item2", "Item3", "Item4"

#    gp.AddOptionInteger("Integer", intOption)
#    gp.AddOptionDouble("Double", dblOption)
    gp.AddOptionToggle("Add", boolOption)
#    listIndex = 3
#    opList = gp.AddOptionList("List", listValues, listIndex)
#    while True:
    # perform the get operation. This will prompt the user to
    # input a point, but also allow for command line options
    # defined above
    get_rc = gp.Get()
    
    if gp.CommandResult() != Rhino.Commands.Result.Success:
        return None, gp.CommandResult()

#        print " Integer =", intOption.CurrentValue
#        print " Double =", dblOption.CurrentValue

    options = {
        'add_layer': boolOption.CurrentValue,
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


def create_color(value):
    c = lambda x: x if x < 256 else 255
    if isinstance(value, str):
        if ',' in value:
            xs = value.split(',')
            xs = [c(int(x)) for x in xs]
            return tuple(xs)
        return value
    return (0, 0, 0)

def create_linetype(value):
    return value

def create_print_width(value):
    return value
#    return None

def get_code():
    import os
    import urllib2
    import ssl
    
#    a = rs.GetDocumentUserText('code_url')
#    try:
#    #    x = ssl.SSLContext()  # Only for gangstars
#        x = ssl._create_unverified_context()
#        request = urllib2.Request(a)
#        response = urllib2.urlopen(request, context=x)
#        print(response.read())
#    except urllib2.URLError as e:
#        print(e)

    d = os.path.dirname(__file__)
    f = os.path.join(d, 'file.json')
    return json.load(open(f, 'r'))


def setup_layer(layer_name, code):
    color = create_color(code['cad_color'])
    print_width = create_print_width(code['cad_lineweight'])
    linetype = create_linetype(code['cad_linetype'])

    rs.LayerColor(layer_name, color)
    rs.LayerPrintWidth(layer_name, print_width)
    rs.LayerLinetype(layer_name, linetype)


def sync_layer(layer_name, code, add_layer=False):
#    # Cook up an unused layer name
#    unused_name = scriptcontext.doc.Layers.GetUnusedLayerName(False)

#    # Prompt the user to enter a layer name
#    gs = Rhino.Input.Custom.GetString()
#    gs.SetCommandPrompt("Name of layer to add")
#    gs.SetDefaultString(unused_name)
#    gs.AcceptNothing(True)
#    gs.Get()
#    if gs.CommandResult()!=Rhino.Commands.Result.Success:
#        return gs.CommandResult()
#
#    # Was a layer named entered?
#    layer_name = gs.StringResult().Trim()
#    if not layer_name:
#        print "Layer name cannot be blank."
#        return Rhino.Commands.Result.Cancel

    # Is the layer name valid?
    if not Rhino.DocObjects.Layer.IsValidName(layer_name):
        print layer_name, "is not a valid layer name."
        return Rhino.Commands.Result.Cancel

    # Does a layer with the same name already exist?
    layer_index = sc.doc.Layers.Find(layer_name, True)
    layer_exist = layer_index >= 0
    if not layer_exist and not add_layer:
        print('Skip layer %s' % layer_name)
        return
    elif not layer_exist:
        layer_index = sc.doc.Layers.Add(layer_name, System.Drawing.Color.Black)

    print('Setup layer %s' % layer_name)
    setup_layer(layer_name, code)

#        if layer_index < 0:
#            print "Unable to add", layer_name, "layer."
#            return Rhino.Commands.Result.Failure
#        return Rhino.Commands.Result.Cancel
#    layer = sc.doc.Layers.FindIndex(layer_index)
#    print(layer.Color)
#    print(type(layer.Color))
#    print(dir(layer.Color))

def main():
    sync_options, sync_res = get_sync_options()
#    print(sync_res)
#    return
    if sync_res != Rhino.Commands.Result.Success:
        return sync_res

    code = get_code()
#    code = code[:10]
    for x in code:
        layer_name = x['code']
        sync_layer(layer_name, x, **sync_options)


if __name__=="__main__":
    main()