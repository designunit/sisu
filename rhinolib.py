import rhinoscriptsyntax as rs
import sync

SISUFILE_KEY = 'sisuSyncFile'


def get_sisufile():
    f = rs.GetDocumentUserText(SISUFILE_KEY)
    if not f:
        return None
    return sync.read_sisufile(f)


def set_sisufile(f):
    rs.SetDocumentUserText(SISUFILE_KEY, f)
