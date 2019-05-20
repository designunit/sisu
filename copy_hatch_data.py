import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import math
import json

def copy_hatch_data():
    hatch_guid = rs.GetObject('Select Hatch', rs.filter.hatch)
    if not hatch_guid:
        return

    target_guid = rs.GetObject('Select Target', rs.filter.curve)
    if not target_guid:
        return

    hatch = sc.doc.Objects.Find(hatch_guid)

    rotation = hatch.HatchGeometry.PatternRotation
    base_point = hatch.HatchGeometry.BasePoint
    base = list(base_point)

    rs.SetUserText(target_guid, 'patternRotation', str(math.degrees(rotation)))
    rs.SetUserText(target_guid, 'patternBasePoint', json.dumps(base))


if __name__ == '__main__':
    copy_hatch_data()