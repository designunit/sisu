import rhinoscriptsyntax as rs
import scriptcontext as sc
import sync

SISUFILE_KEY = 'sisuSyncFile'


def get_sisufile():
    f = rs.GetDocumentUserText(SISUFILE_KEY)
    if not f:
        f = str(rs.DocumentPath() + 'sisufile.json')
    return sync.read_sisufile(f)



def set_sisufile(f):
    rs.SetDocumentUserText(SISUFILE_KEY, f)


def get_user_text(obj, key, default_value=None, fn=None):
    val = rs.GetUserText(obj.Id, key)
    if not val:
        return default_value
    if not fn:
        return val
    return fn(val)


def find_layer_objects(match_fn, layer_name):
    xs = sc.doc.Objects.FindByLayer(layer_name)

    return [x for x in xs if match_fn(x)]
