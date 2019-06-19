def get_related_layers(config, derived_only=False):
    def full_layer_name(layer, parent):
        return '{parent}::{layer}'.format(layer=layer, parent=parent)

    names = []
    for x in config['data']:
        name = x['layer'][0]
        if not derived_only:
            names.append(name)
        for view in x['view']:
            view_name = name + view['layerSuffix']
            names.append(full_layer_name(view_name, name))
    return names