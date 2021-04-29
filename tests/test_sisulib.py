from sisulib import create_color, get_related_layers, read_sisufile

PATH_TO_CONFIG_FILE = 'sisufile.json'


class TestCreateColorFunc:
    def test_with_string_numbers(self):
        assert [128, 128, 128] == create_color('128, 128, 128')

    def test_with_letters(self):
        assert [0, 0, 0] == create_color('128, 12a, 128')

    def test_with_less_len_list(self):
        assert [0, 0, 0] == create_color('135, 125')


class TestGetRelatedColorsFunc:
    def test_get_derived_only(self):
        related_layers = get_related_layers(read_sisufile(PATH_TO_CONFIG_FILE))
        assert [u'Default', 'Default::Default_SOLID',
                'Default::Default_HATCH'] == related_layers
