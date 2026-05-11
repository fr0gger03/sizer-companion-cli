#!/usr/bin/env python3

# ACC Sizer Companion CLI - output module
################################################################################
### Copyright 2023 VMware, Inc.
### SPDX-License-Identifier: MIT License
################################################################################

import os
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


# VMware By Broadcom Dark Theme Palette (AA compliant)
VMW_BLUE = "#0088EF"       # Titles
VMW_LIGHT_BLUE = "#0098C7" # Row labels
VMW_AQUA = "#01B9C6"       # Column headers
VMW_GREEN = "#61A60E"      # Accent / positive values
VMW_PURPLE = "#A468EE"     # Panel borders


def df_to_table(df, title=None):
    table = Table(title=title, show_lines=True, title_style=f"bold {VMW_BLUE}")
    for col in df.columns:
        table.add_column(str(col), justify="right", header_style=f"bold {VMW_AQUA}")
    for _, row in df.iterrows():
        values = [str(v) for v in row]
        # Style the first column as a row label if it looks like a label (non-numeric)
        if values and not values[0].replace('.','',1).replace('-','',1).isdigit():
            values[0] = f"[bold {VMW_LIGHT_BLUE}]{values[0]}[/bold {VMW_LIGHT_BLUE}]"
        table.add_row(*values)
    return table


def data_describe(output_path, csv_file):
    console = Console()
    vm_data_df = pd.read_csv(os.path.join(output_path, csv_file), index_col=0)
    vm_data_df['os'] = vm_data_df['os'].astype(str)

    # --- Overview ---
    power_counts = vm_data_df['vmState'].value_counts()
    
    overview = Table(title=f"Environment Overview — {csv_file}", title_style=f"bold {VMW_BLUE}")
    overview.add_column("Total VMs", justify="center", header_style=f"bold {VMW_AQUA}")
    for state in power_counts.index:
        overview.add_column(str(state), justify="center", header_style=f"bold {VMW_AQUA}")
    overview.add_column("Clusters", justify="center", header_style=f"bold {VMW_AQUA}")
    overview.add_column("Unique OS", justify="center", header_style=f"bold {VMW_AQUA}")
    overview.add_column("vCPU", justify="center", header_style=f"bold {VMW_AQUA}")
    overview.add_column("vRAM (GiB)", justify="center", header_style=f"bold {VMW_AQUA}")
    overview.add_column("Used VMDK (GiB)", justify="center", header_style=f"bold {VMW_AQUA}")
    overview.add_column("Provisioned VMDK (GiB)", justify="center", header_style=f"bold {VMW_AQUA}")
    
    overview.add_row(
        str(vm_data_df.vmName.count()),
        *[str(v) for v in power_counts.values],
        str(vm_data_df.cluster.nunique()),
        str(vm_data_df.os.nunique()),
        str(vm_data_df.vCpu.sum()),
        str(round(vm_data_df.vRam.sum(), 1)),
        str(round(vm_data_df.vmdkUsed.sum(), 1)),
        str(round(vm_data_df.vmdkTotal.sum(), 1)),
    )
    console.print(Panel(overview, border_style=VMW_PURPLE))

    # --- Clusters (horizontal) ---
    cluster_names = vm_data_df.cluster.unique()
    cl_table = Table(title=f"Clusters ({len(cluster_names)})", title_style=f"bold {VMW_BLUE}")
    for name in cluster_names:
        cl_table.add_column(str(name), justify="center", header_style=f"bold {VMW_AQUA}")
    cl_table.add_row(*[
        str(vm_data_df[vm_data_df.cluster == c].vmName.count())
        for c in cluster_names
    ])
    console.print(Panel(cl_table, border_style=VMW_PURPLE))

    # --- vCPU Distribution ---
    vcpu_counts = vm_data_df.groupby('vCpu')['vmId'].nunique().reset_index()
    vcpu_counts.columns = ['vCPU Count', 'VM Count']
    vcpu_counts = vcpu_counts.sort_values('vCPU Count').reset_index(drop=True)
    console.print(Panel(df_to_table(vcpu_counts, title="vCPU Distribution"), border_style=VMW_PURPLE))

    # --- Guest OS (vertical — can be many rows) ---
    os_counts = vm_data_df.groupby('os')['vmId'].nunique().reset_index()
    os_counts.columns = ['Guest OS', 'VM Count']
    console.print(Panel(df_to_table(os_counts, title="Guest Operating Systems"), border_style=VMW_PURPLE))

    # --- Statistics ---
    desc = vm_data_df.describe().drop('count').reset_index()
    desc.rename(columns={'index': ''}, inplace=True)
    console.print(Panel(df_to_table(desc, title="Statistics"), border_style=VMW_PURPLE))
