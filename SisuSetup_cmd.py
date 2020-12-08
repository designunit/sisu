import scriptcontext as sc
import rhinoscriptsyntax as rs
import System
import Rhino
import json
import math
from rhinolib import link_sisufile

__commandname__ = 'SisuSetup'


def RunCommand( is_interactive ):
    file = rs.OpenFileName(title='Select Sisufile')
    if not file:
        return None, Rhino.Commands.Result.Cancel

    status = link_sisufile(file)
    if not status:
        rs.MessageBox('Something went wrong with this sisufile. Try another file')
        return None, Rhino.Commands.Result.Failure

    return file, Rhino.Commands.Result.Success


if __name__ == '__main__':
    RunCommand(None)
