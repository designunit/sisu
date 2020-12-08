import scriptcontext as sc
import rhinoscriptsyntax as rs
import System
import Rhino
import json
import math
from rhinolib import set_sisufile

__commandname__ = 'SisuSetup'


def RunCommand( is_interactive ):
    file = rs.OpenFileName(title='Select Sisufile', extension='.json')
    if not file:
        return None, Rhino.Commands.Result.Cancel

    set_sisufile(file)

    return file, Rhino.Commands.Result.Success


if __name__ == '__main__':
    RunCommand(None)
