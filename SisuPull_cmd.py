import json
import Rhino
import rhinoscriptsyntax as rs
from rhinolib import get_sisufile
from sisulib import get_related_layers
from sync import read_sisufile

__commandname__ = 'SisuPull'


def RunCommand( is_interactive ):

    config = get_sisufile()

    if not config:
        print('Sisufile not configured')
        return Rhino.Commands.Result.Failure

    try:
        json.dumps(read_sisufile(config), indent=4)
    except Exception:
        return Rhino.Commands.Result.Failure


    return Rhino.Commands.Result.Success


if __name__ == '__main__':
    RunCommand(None)
