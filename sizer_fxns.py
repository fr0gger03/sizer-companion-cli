#!/usr/bin/env python3

# ACC Sizer Companion CLI - functions module
################################################################################
### Copyright 2023 VMware, Inc.
### SPDX-License-Identifier: MIT License
################################################################################

import sys
import json
from data_transform import data_describe, lova_conversion, rvtools_conversion, ps_filter, exclude_workloads, include_workloads, build_workload_profiles


def describe_import(**kwargs):
    '''Triggered when user selects "view_only"'''
    print("Getting overview of environment. Only file type, input path and input file name will be used.")
    input_path = kwargs['input_path']
    ft = kwargs['file_type']
    fn = kwargs['file_name']
    output_path = kwargs['output_path']

    view_params = {"input_path":input_path,"file_name":fn, "output_path":output_path}
    
    match ft:
        case 'live-optics':
            csv_file = lova_conversion(**view_params)
        case 'rv-tools':
            csv_file = rvtools_conversion(**view_params)

    if csv_file is not None:
        data_describe(output_path,csv_file)
    else:
        print()
        print("Something went wrong.  Please check your syntax and try again.")
        sys.exit(1)
    sys.exit(0)


def prepare_import(**kwargs):
    ft = kwargs['file_type']
    fn = kwargs['file_name']
    input_path = kwargs['input_path']
    output_path = kwargs['output_path']

    # the following parameters will be used to build the payload contained in the 
    storage_capacity = kwargs['storage_capacity']

    # build the payload parameter dictionary
    payload_params = {
        "output_path":output_path,
        "storage_capacity":storage_capacity,
        }

    # build the parameter dictionary for getting the recommendation
    options = ['output_format']
    rec_params = {}
    for i in options:
        if i in kwargs:
            option = kwargs[i]
        else:
            option = None
        rec_params[i] = option

    # instantiate a list to be used in the payload parameter dictionary
    wp_file_list = []

    ingest_params = {"file_type":ft, "input_path":input_path, "file_name":fn, "output_path":output_path}
    match ft:
        case 'live-optics':
            csv_file = lova_conversion(**ingest_params)
        case 'rv-tools':
            csv_file = rvtools_conversion(**ingest_params)

    #transform parsed data according to arguments
    if csv_file is not None:

        if kwargs['power_state'] is not None:
            power_params = {"power_state":kwargs['power_state'], "output_path":output_path, "csv_file":csv_file}
            csv_file = ps_filter(**power_params)
        else:
            pass

        if kwargs['include_filter'] is not None:
            if kwargs['include_filter_field'] is None:
                print("You must specify BOTH a text string to use as a filter, AND field to filter by (vm_name, guest_os, cluster) when using an include filter.")
            else:
                inc_filter_params = {"include_filter":kwargs['include_filter'], "include_filter_field":kwargs['include_filter_field'], "output_path":output_path, "csv_file":csv_file}
                csv_file = include_workloads(**inc_filter_params)
        else:
            pass
        
        if kwargs['exclude_filter'] is not None:
            if kwargs['exclude_filter_field'] is None:
                print("You must specify BOTH a text string to use as a filter, AND field to filter by (vm_name, guest_os, cluster) when using an exclude filter.")
            else:
                ex_filter_params = {"exclude_filter":kwargs['exclude_filter'], "exclude_filter_field":kwargs['exclude_filter_field'], "output_path":output_path, "csv_file":csv_file}
                csv_file = exclude_workloads(**ex_filter_params)
        else:
            pass

        if kwargs['workload_profiles'] is not None:
            match kwargs['workload_profiles']:
                case "all_clusters":
                    profile_params = {"csv_file":csv_file, "workload_profiles":kwargs['workload_profiles'], "profile_list":kwargs['profile_list'], "include_remaining":kwargs['include_remaining'], "output_path":output_path}
                    wp_file_list = build_workload_profiles(**profile_params)

                case "some_clusters" | "os" | "vmName":
                    if kwargs['profile_list'] is None:
                        print("You must supply a list of one or more valid cluster names / guest operating systems / VM names.  Use './sizer-cli.py describe' for a summary of the environment, or review your file.")
                        sys.exit(1)
                    else:
                        profile_params = {"csv_file":csv_file, "workload_profiles":kwargs['workload_profiles'], "profile_list":kwargs['profile_list'], "include_remaining":kwargs['include_remaining'], "output_path":output_path}
                        wp_file_list = build_workload_profiles(**profile_params)
        else:
            pass

        # ensure either the last processed csv_file OR the list of workload profiles is stored as a common vairable to be used in the payload parameter dictionary
        if len(wp_file_list) == 0:
            wp_file_list = [csv_file]
        else:
            pass
        
        print("Your data is prepped - please find the following files in the 'output' directory:")
        print()
        for file in wp_file_list:
            print(file)
    
    else:
        print("Something went wrong.  Please check your syntax and try again.")
        sys.exit(1)
