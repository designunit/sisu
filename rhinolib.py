import rhinoscriptsyntax as rs
import scriptcontext as sc
from sisulib import read_sisufile, get_related_layers
import os.path

SISUFILE_KEY = 'sisuSyncFile'


def get_sisufile_path():
    f = rs.GetDocumentUserText(SISUFILE_KEY)
    if f:
        return f
    doc_path = rs.DocumentPath()
    if not doc_path:
        return None
    return os.path.join(doc_path, 'sisufile.json')


def get_sisufile():
    f = get_sisufile_path()
    if not f:
        return None
    return read_sisufile(f)


def link_sisufile(filepath):
    config = read_sisufile(filepath)
    if not config:
        return False

    rs.SetDocumentUserText(SISUFILE_KEY, filepath)
    return True


def get_user_text(obj, key, default_value=None, fn=None):
    if not obj:
        return default_value
    val = rs.GetUserText(obj.Id, key)
    if not val:
        return default_value
    if not fn:
        return val
    return fn(val)


def find_layer_objects(match_fn, layer_name):
    layer_index = sc.doc.Layers.FindByFullPath(layer_name, True)
    layer = sc.doc.Layers.FindIndex(layer_index)
    # layer_id = rs.LayerId(layer_name)
    # xs = sc.doc.Objects.FindByLayer(layer_name)
    xs = sc.doc.Objects.FindByLayer(layer)
    if not xs:
        return []

    return [x for x in xs if match_fn(x)]


def get_sisu_layers(config, derived_only=False):
    rhino_layer_names = rs.LayerNames()
    layers = get_related_layers(config, derived_only)
    names = []
    for layer in layers:
        if layer in rhino_layer_names:
            names.append(layer)
    return names

