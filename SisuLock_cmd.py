import Rhino
import rhinoscriptsyntax as rs
from rhinolib import get_sisufile
from sisulib import get_related_layers

__commandname__ = 'SisuLock'


def RunCommand( is_interactive ):
    config = get_sisufile()
    if not config:
        print('Sisufile not configured')
        return Rhino.Commands.Result.Failure

    layers = get_related_layers(config, derived_only=True)
    for layer in layers:
        rs.LayerLocked(layer, True)
        parent = rs.ParentLayer(layer)
        rs.ExpandLayer(parent, False) # collapse parend layer

    return Rhino.Commands.Result.Success


if __name__ == '__main__':
    RunCommand(None)
