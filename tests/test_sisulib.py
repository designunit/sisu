import os
import sys

sys.path.append(os.path.abspath('./tests/'))
from sisulib import create_color, get_related_layers, read_sisufile

PATH_TO_CONFIG_FILE = 'sisufile.json'


class TestCreateColorFunc:
    def test_with_string_numbers(self):
        assert [128, 128, 128] == create_color('128, 128, 128')

    def test_with_letters(self):
        assert [0, 0, 0] == create_color('128, 12a, 128')

    def test_with_less_len_list(self):
        assert [0, 0, 0] == create_color('135, 125')


class TestGetRelatedLayersFunc:
    def test_get_derived_only(self):
        json = {u'version': u'0', u'data': [
            {u'layer': [u'Default', {u'color': [255, 0, 0], u'lineWeight': 1, u'lineType': u'continuous'}],
             u'code': u'X', u'options': {}, u'properties': {u'patternBasePoint': [0, 0, 0], u'patternRotation': 0},
             u'view': [{u'render': [u'hatch',
                                    {u'color': [10, 190, 10], u'pattern': u'Solid', u'scale': 1, u'lineWeight': 0.13}],
                        u'layerSuffix': u'_SOLID'}, {u'render': [u'hatch', {u'color': [0, 255, 0], u'pattern': u'Grid',
                                                                            u'scale': 1, u'lineWeight': 0.1}],
                                                     u'layerSuffix': u'_HATCH'}]}]}

        related_layers = get_related_layers(json)
        assert [u'Default', 'Default::Default_SOLID',
                'Default::Default_HATCH'] == related_layers
