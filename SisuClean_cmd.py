import Rhino
import rhinoscriptsyntax as rs
from rhinolib import get_sisufile, get_sisu_layers
#from sisulib import get_related_layers

__commandname__ = 'SisuClean'


def RunCommand( is_interactive ):
    config = get_sisufile()
    if not config:
        print('Sisufile not configured')
        return Rhino.Commands.Result.Failure

    layers = get_sisu_layers(config, derived_only=True)
    rhino_layer_names = rs.LayerNames()

#    if not set(layers) < set(rhino_layer_names):
#        print('File is alredy clean!')
#        return Rhino.Commands.Result.Success

    for layer in layers:
        if layer in rhino_layer_names:
            if rs.IsLayerCurrent(layer):
                parent = rs.ParentLayer(layer)
                rs.CurrentLayer(parent)
            rs.PurgeLayer(layer)
    print('Successfully cleaned')
    return Rhino.Commands.Result.Success


if __name__ == '__main__':
    RunCommand(None)
