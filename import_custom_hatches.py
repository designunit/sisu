import rhinoscriptsyntax as rs
import csv
from rhinolib import get_sisufile


# parse all hatch paths
hatches_paths_all_mac = []
with open('/Volumes/UNIT4/#Uspace/MLA_SISU_DEMO/custom_hatches_paths_mac_all.csv') as csvfile:
    hatches_reader = csv.reader(csvfile, delimiter=',')
    for list_of_hatch_paths in hatches_reader:
        for hatch_path in list_of_hatch_paths:
            # print(hatch_path)
            hatches_paths_all_mac.append(hatch_path)


# import all hatches
'''
for path in hatches_paths_all_mac:
    filename = path
    if filename:
        patterns = rs.AddHatchPatterns(filename)
        if patterns:
            for pattern in patterns: print pattern
'''

# import hatches needed
custom_hatches_needed = []
config = get_sisufile()
for code in config['data']:
    custom_hatches_needed.append(code['view'][1]['render'][1]['pattern'])
    
for hatch_needed in custom_hatches_needed:
    for path in hatches_paths_all_mac:
        filename = path
        if filename and hatch_needed in filename:
            patterns = rs.AddHatchPatterns(filename)
            if patterns:
                for pattern in patterns: print pattern