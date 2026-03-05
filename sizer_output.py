#!/usr/bin/env python3

# ACC Sizer Companion CLI - output module
################################################################################
### Copyright 2023 VMware, Inc.
### SPDX-License-Identifier: MIT License
################################################################################

import json
import pandas as pd
from prettytable import PrettyTable
import time

def generate_table(results):
    """Generates a 'prettytable' using a JSON payload; automatically uses the dictionary keys in the payload as column headers."""
    # if type(results) is list:
    if type(results) is list:
        keyslist = list(results[0].keys())
    elif type(results) is dict:
        keyslist = list(results.keys())
    else:
            return False

    table = PrettyTable(keyslist)
    for dct in results:
        table.add_row([dct.get(c, "") for c in keyslist])
    return table


def terminal_output(**kwargs):
    calcs = kwargs['calcs']
    assumps = kwargs['assumps']
    logs = kwargs['cl']
    overview = kwargs['recommendation']['overview']
    ext_storage = kwargs['recommendation']['ext_storage']
    cluster_json =  kwargs['recommendation']['cluster_json']
    vm_json =  kwargs['recommendation']['vm_json']
    vm_exceptions = kwargs['recommendation']['vm_exceptions']
    limited_compat = kwargs['recommendation']['limited_compat']

    print()
    print(overview)

    for id, cluster in cluster_json.items():
        print(f'\n\n{id}\n', cluster)

    for cluster, vm_list in vm_json.items():
        print(f'\n\n{cluster} virtual machines:\n', vm_list)

    try:
        print('\nExternal Storage Capacity:\n')
        print(ext_storage)
    except:
        print("There is no external storage.")

    try:
        vm_exceptions
        print('\nVM exceptions:\n')
        table = generate_table(vm_exceptions)
        print(table.get_string(fields=['vmName', 'exceptionReason', 'unsupportedResourceTypes', 'preferredHostType', 'chosenHostType']))
    except:
        print("There are no VM exceptions.")

    try:
        limited_compat
        print('\nHost incompatibilities:\n')
        table = generate_table(limited_compat)
        print(table.get_string(fields=['vmName', 'exceptionReason', 'unsupportedResourceTypes', 'preferredHostType', 'chosenHostType']))
    except:
        print("There are no host incompatibilities.")

    print()
    print("Assumptions:")
    for i in assumps:
        print(f'  * {i}')

    # print calculation logs if user desires
    if logs is True:
        print(calcs)
    
    print("\nAll output files are saved in the '/output' directory.")

