import Rhino
import rhinoscriptsyntax as rs
from rhinolib import get_sisufile, get_sisu_layers

__commandname__ = 'SisuShow'


def RunCommand( is_interactive ):
    config = get_sisufile()
    if not config:
        print('Sisufile not configured')
        return Rhino.Commands.Result.Failure

    layers = get_sisu_layers(config, derived_only=True)
    for layer in layers:
        rs.LayerVisible(layer, visible=True)

    print('Layers successfully shown!')
    return Rhino.Commands.Result.Success


if __name__ == '__main__':
    RunCommand(None)
