import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
from rhinolib import get_sisufile
from sisulib import get_related_layers
import math
import json

__commandname__ = 'SisuCopyHatch'


def RunCommand( is_interactive ):
    hatch_guid = rs.GetObject('Select Hatch', rs.filter.hatch)
    if not hatch_guid:
        return Rhino.Commands.Result.Failure

    target_guid = rs.GetObject('Select Target', rs.filter.curve)
    if not target_guid:
        return Rhino.Commands.Result.Failure

    hatch = sc.doc.Objects.Find(hatch_guid)

    rotation = hatch.HatchGeometry.PatternRotation
    rotation = str(math.degrees(rotation))
    base = hatch.HatchGeometry.BasePoint
    base = list(base)
    base = json.dumps(base)

    rs.SetUserText(target_guid, 'patternRotation', rotation)
    rs.SetUserText(target_guid, 'patternBasePoint', base)

    return Rhino.Commands.Result.Success


if __name__ == '__main__':
    RunCommand(None)
