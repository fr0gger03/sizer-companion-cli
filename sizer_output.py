#!/usr/bin/env python3

# ACC Sizer Companion CLI - output module
################################################################################
### Copyright 2023 VMware, Inc.
### SPDX-License-Identifier: MIT License
################################################################################

import os
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich import box


# VMware By Broadcom Dark Theme Palette (AA compliant)
VMW_BLUE = "#0088EF"       # Titles
VMW_LIGHT_BLUE = "#0098C7" # Row labels
VMW_AQUA = "#01B9C6"       # Column headers
VMW_GREEN = "#61A60E"      # Accent / positive values


def df_to_table(df, title=None):
    table = Table(title=title, box=box.MINIMAL, title_style=f"bold {VMW_BLUE}")
    for col in df.columns:
        table.add_column(str(col), justify="right", header_style=f"bold {VMW_AQUA}")
    for _, row in df.iterrows():
        values = [str(v) for v in row]
        # Style the first column as a row label if it looks like a label (non-numeric)
        if values and not values[0].replace('.','',1).replace('-','',1).isdigit():
            values[0] = f"[bold {VMW_LIGHT_BLUE}]{values[0]}[/bold {VMW_LIGHT_BLUE}]"
        table.add_row(*values)
    return table


def data_describe(output_path, csv_file, vcpu_grouping=None):
    console = Console()
    vm_data_df = pd.read_csv(os.path.join(output_path, csv_file), index_col=0)
    vm_data_df['os'] = vm_data_df['os'].astype(str)

    # --- Overview ---
    power_counts = vm_data_df['vmState'].value_counts()
    
    overview = Table(title=f"Environment Overview — {csv_file}", box=box.MINIMAL, title_style=f"bold {VMW_BLUE}")
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
    console.print(overview)

    # --- Clusters (vertical) ---
    cluster_names = vm_data_df.cluster.unique()
    cl_table = Table(title=f"Clusters ({len(cluster_names)})", box=box.MINIMAL, title_style=f"bold {VMW_BLUE}")
    cl_table.add_column("Cluster", justify="left", header_style=f"bold {VMW_AQUA}")
    cl_table.add_column("VM Count", justify="right", header_style=f"bold {VMW_AQUA}")
    for c in cluster_names:
        cl_table.add_row(
            f"[bold {VMW_LIGHT_BLUE}]{c}[/bold {VMW_LIGHT_BLUE}]",
            str(vm_data_df[vm_data_df.cluster == c].vmName.count()),
        )

    # --- vCPU Distribution ---
    vcpu_counts = vm_data_df.groupby('vCpu')['vmId'].nunique().reset_index()
    vcpu_counts.columns = ['vCPU Count', 'VM Count']
    vcpu_counts = vcpu_counts.sort_values('vCPU Count').reset_index(drop=True)
    vcpu_table = df_to_table(vcpu_counts, title="vCPU Distribution")

    # --- Guest OS ---
    os_counts = vm_data_df.groupby('os')['vmId'].nunique().reset_index()
    os_counts.columns = ['Guest OS', 'VM Count']
    os_table = df_to_table(os_counts, title="Guest Operating Systems")

    # Display clusters, vCPU, and OS tables side by side
    grid = Table.grid(padding=(0, 2))
    grid.add_row(cl_table, vcpu_table, os_table)
    console.print(grid)

    # --- Statistics ---
    desc = vm_data_df.describe().drop('count').reset_index()
    desc.rename(columns={'index': ''}, inplace=True)
    console.print(df_to_table(desc, title="Statistics"))

    # --- Mean by vCPU Group ---
    if vcpu_grouping is not None:
        import math
        upper = vm_data_df['vCpu'].apply(lambda v: max(1, math.ceil(v / vcpu_grouping)) * vcpu_grouping)
        lower = upper - vcpu_grouping + 1
        vm_data_df = vm_data_df.copy()
        vm_data_df['vcpu_group'] = lower.astype(int).astype(str) + '-' + upper.astype(int).astype(str) + ' vCPU'

        agg_cols = {'vmId': 'count', 'vCpu': 'mean', 'vRam': 'mean', 'vmdkUsed': 'mean', 'vmdkTotal': 'mean'}
        # Include IOPS columns if present (LiveOptics data)
        for col in ['readIOPS', 'writeIOPS']:
            if col in vm_data_df.columns:
                agg_cols[col] = 'mean'

        grouped = vm_data_df.groupby('vcpu_group', sort=False).agg(agg_cols)
        grouped = grouped.sort_values('vCpu').reset_index()
        grouped = grouped.round(1)
        grouped.rename(columns={
            'vcpu_group': 'vCPU Group',
            'vmId': 'VM Count',
            'vCpu': 'Mean vCPU',
            'vRam': 'Mean vRAM (GiB)',
            'vmdkUsed': 'Mean Used VMDK (GiB)',
            'vmdkTotal': 'Mean Prov. VMDK (GiB)',
            'readIOPS': 'Mean Read IOPS',
            'writeIOPS': 'Mean Write IOPS',
        }, inplace=True)

        console.print(df_to_table(grouped, title=f"Mean by vCPU Group (buckets of {vcpu_grouping})"))
