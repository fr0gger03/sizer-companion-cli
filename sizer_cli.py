#!/usr/bin/env python3

# ACC Foundation Sizing Companion CLI - main module
################################################################################
### Copyright 2026 VMware, Inc.
### SPDX-License-Identifier: MIT License
################################################################################

import argparse
from argparse import SUPPRESS
import sys
from sizer_fxns import describe_import, prepare_import

def main():
    class MyFormatter(argparse.RawDescriptionHelpFormatter):
        def __init__(self,prog):
            super(MyFormatter, self).__init__(prog,max_help_position=10)

    ap = argparse.ArgumentParser(
                    prog = 'sizer-cli.py',
                    description = 'A Command-line companion for the ACC Sizer.',
                    formatter_class=MyFormatter, usage=SUPPRESS,
                    epilog='''
    Welcome to the ACC Companion CLI!! \n\n
    This tool is used to help you prepare raw data from your customer for the ACC Sizer quickly and reliably, with a number of available options.
    The script acn be used to import data from from either RVTools or LiveOptics (DO NOT MODIFY the original files).  Common use cases are to quickly include or exclude
    powered-off virtual machines, specific clusters or virtual machines by naming patterns, etc.  Further it will normalize the data from either RV Tools or LiveOptics
    into a common set of inputs ready for the sizer tools. \n\n
    Please do not edit or modify the source RV Tools or LiveOptics file(s) in any way - the tool depends on original file structure for the functions to work. \n\n
    Use arguments at the command line to transform the data before you receive your sizing!\n\n
    ''')

    # create a subparser for the subsequent sections    
    subparsers = ap.add_subparsers(help='sub-command help')

# ============================
# Parent parser containing arguments for all import operations
# ============================
    parent_import_parser = argparse.ArgumentParser(add_help=False)
    parent_import_parser.add_argument('-fn', '--file_name', nargs='*', required=True, help="A space-separated list of file names containing the VM inventory to be imported; all files must be of the same type (LiveOptics or RVTools).  By default, this script looks for the file in the 'input' subdirectory.")
    parent_import_parser.add_argument('-ft', '--file_type', required=True, choices=['rv-tools', 'live-optics'], type=str.lower, help="Specify either 'live-optics' or 'rv-tools'")


# ============================
# Subparsers for individual commands
# ============================

    describe_parser = subparsers.add_parser('describe', formatter_class=MyFormatter, parents=[parent_import_parser], help='Describe the contents of one or more imported files.')
    describe_parser.set_defaults(func = describe_import)

    preparation_parser = subparsers.add_parser('prepare', formatter_class=MyFormatter, parents=[parent_import_parser], help='Import one or more files and transform the data for use with sizing tools.')
    preparation_parser.add_argument('-exfil', '--exclude_filter', nargs = '+', help = 'A space-separated list of text strings used to identify workloads to exclude.')
    preparation_parser.add_argument('-eff', '--exclude_filter_field', choices = ['cluster','os','vmName'], help = 'The column/field used for exclusion filtering.')
    preparation_parser.add_argument('-infil', '--include_filter', nargs = '+', help = 'A space-separated list of text strings used to identify workloads to keep.')
    preparation_parser.add_argument('-iff', '--include_filter_field', choices = ['cluster','os','vmName'], help = "The column/field used for inclusion filtering.")
    preparation_parser.add_argument('-ps', '--power_state',  choices = ['p', 'ps'], type=str.lower, help = "By default, all VM are included regardless of powere state. Use to specify whether to include only those (p)owered on, or powered on and suspended (ps).")
    preparation_parser.add_argument('-wp', '--workload_profiles', choices=['all_clusters', 'some_clusters', 'os','vmName'], help = "Use to create workload profiles based on the selected grouping.")
    preparation_parser.add_argument('-pl', '--profile_list', nargs = '+', help = 'A space-separated list of text strings used to filter workloads for the creation of workload profiles.')
    preparation_parser.add_argument('-ir', '--include_remaining', action= 'store_true', help= 'Use to indicate you wish to keep remaining workloads - default is to discard.')   
    preparation_parser.add_argument('-sc', '--storage_capacity', nargs = '?', choices=['PROVISIONED', 'UTILIZED'], default = "UTILIZED", type=str.upper, help="Use to specify whether PROVISIONED or UTILIZED storage is used (default is UTILIZED).")
    preparation_parser.add_argument('-o', '--output_format', choices=['csv', 'pdf', 'ppt', 'xls', 'terminal'], default = "csv", help="Select output format Default is csv.")

    preparation_parser.set_defaults(func = prepare_import)

# ============================
# Parse arguments and call function
# ============================

    args = ap.parse_args()

    # If no arguments given, or no subcommands given with a function defined, return help:
    if 'func' not in args:
        ap.print_help(sys.stderr)
        sys.exit(0)
    else:
        pass

    params = vars(args)
    params.update({"input_path": 'input/'})
    params.update({"output_path": 'output/'})

    # Call the appropriate function with the dictionary containing the arguments.
    args.func(**params)
    sys.exit(0)

if __name__ == "__main__":
    main()
