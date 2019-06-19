import Rhino
import rhinoscriptsyntax as rs
from rhinolib import get_sisufile
from sisulib import get_related_layers

__commandname__ = 'SisuClean'


def RunCommand( is_interactive ):
    config = get_sisufile()
    if not config:
        print('Sisufile not configured')
        return Rhino.Commands.Result.Failure

    layers = get_related_layers(config, derived_only=True)
    for layer in layers:
        if rs.IsLayerCurrent(layer):
            parent = rs.ParentLayer(layer)
            rs.CurrentLayer(parent)
        rs.PurgeLayer(layer)

    return Rhino.Commands.Result.Success


if __name__ == '__main__':
    RunCommand(None)
