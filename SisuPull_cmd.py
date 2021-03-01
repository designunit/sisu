import Rhino
from rhinolib import get_sisufile_path
from sisulib import sisufile_pull

__commandname__ = 'SisuPull'


def RunCommand( is_interactive ):
    path = get_sisufile_path()

    if not path:
        print('Sisufile not linked')
        return Rhino.Commands.Result.Failure

    try:
        sisufile_pull(path)
    except Exception as e:
        print('Something went wrong')
        return Rhino.Commands.Result.Failure

    return Rhino.Commands.Result.Success


if __name__ == '__main__':
    RunCommand(None)
