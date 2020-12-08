import rhinoscriptsyntax as rs
import scriptcontext as sc
from sync import read_sisufile
import os.path
from airtable import get_sisufile_info, get_data_from_airtable

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
    f = rs.GetDocumentUserText(SISUFILE_KEY)
    if not f:
        f = str(rs.DocumentPath() + 'sisufile.json')
    return read_sisufile(f)

def update_sisufile():
    path = get_sisufile_path()
    sisufile = read_sisufile(path)

    if sisufile:
        keys_airtable_dict = get_sisufile_info(sisufile) # need for None check
        if keys_airtable_dict:
            return get_data_from_airtable(keys_airtable_dict)

    return None


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

