import rhinoscriptsyntax as rs
import csv

def get_linetype(layer):
    linetype = rs.LayerLinetype(layer)
    return str(linetype)


def get_lineweight(layer):
    lineweight = rs.LayerPrintWidth(layer)
    return format(float(lineweight), '.2f')


def get_color(layer):
    color = rs.LayerColor(layer)
    return str(color)


def hatch_pattern(layer):
    return 'fsd'


def layer_objects_types(layer):
    object_types = []
    layer_objects = rs.ObjectsByLayer(layer)
    for object in layer_objects:
        object_type = rs.ObjectType(object)
        object_types.append(object_type)
    object_types = list(set(object_types))
    return object_types


if __name__ == '__main__':
    layer_names = rs.LayerNames()
#[10:20]
#    for layer in layer_names:
#        print(str(layer), '', get_linetype(layer), get_lineweight(layer), get_color(layer), layer_objects_types(layer))

for layer in layer_names:
    print(layer)