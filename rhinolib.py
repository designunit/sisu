import rhinoscriptsyntax as rs
import scriptcontext as sc
import sync

SISUFILE_KEY = 'sisuSyncFile'


def get_sisufile():
    f = rs.GetDocumentUserText(SISUFILE_KEY)
    if not f:
        f = str(rs.DocumentPath() + 'sisufile.json')
    return sync.read_sisufile(f)


def link_sisufile(filepath):
    config = sync.read_sisufile(filepath)
    if not config:
        return False

    rs.SetDocumentUserText(SISUFILE_KEY, filepath)
    return True


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
