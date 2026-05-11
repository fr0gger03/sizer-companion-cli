#!/usr/bin/env python3

# ACC Sizer Companion CLI - data transformation module
################################################################################
### Copyright 2023 VMware, Inc.
### SPDX-License-Identifier: MIT License
################################################################################

import math
import os
import pandas as pd


def lova_conversion(**kwargs):
    input_path = kwargs['input_path']
    file_name = kwargs['file_name'] 
    output_path = kwargs['output_path']

    print()
    print("Parsing LiveOptics file(s) locally.")

    df_list = []
    for file in file_name:
        file_df = pd.read_excel(os.path.join(input_path, file), sheet_name="VMs")
        df_list.append(file_df)
    vmdata_df = pd.concat(df_list, axis=0, ignore_index=True)

    # specify columns to KEEP - all others will be dropped
    keep_columns = ['Cluster','Datacenter','Guest IP1','Guest IP2','Guest IP3','Guest IP4','VM OS','Guest Hostname', 'Power State', 'Virtual CPU', 'VM Name', 'MOB ID']
    if 'Virtual Disk Size (MiB)' in vmdata_df:
        keep_columns.extend(['Virtual Disk Size (MiB)','Virtual Disk Used (MiB)', 'Provisioned Memory (MiB)'])
    else:
        keep_columns.extend(['Virtual Disk Size (MB)','Virtual Disk Used (MB)', 'Provisioned Memory (MB)'])

    vmdata_df = vmdata_df.filter(items= keep_columns, axis= 1)

    # rename remaining columns
    vmdata_df.rename(columns = {
        'MOB ID':'vmId',
        'VM Name':'vmName',
        'VM OS':'os',
        'Guest Hostname':'os_name',
        'Power State':'vmState',
        'Virtual CPU':'vCpu',
        'Cluster':'cluster',
        'Datacenter':'virtualDatacenter'
        }, inplace = True)

    if 'Virtual Disk Size (MiB)' in vmdata_df:
        vmdata_df.rename(columns = {
            'Provisioned Memory (MiB)':'vRam',
            'Virtual Disk Size (MiB)':'vmdkTotal',
            'Virtual Disk Used (MiB)':'vmdkUsed',
            }, inplace = True)
    else:
        vmdata_df.rename(columns = {
            'Provisioned Memory (MB)':'vRam',
            'Virtual Disk Size (MB)':'vmdkTotal',
            'Virtual Disk Used (MB)':'vmdkUsed',
            }, inplace = True)

    fillna_values = {"Guest IP1": "no ip", "Guest IP2": "no ip", "Guest IP3": "no ip", "Guest IP4": "no ip", "os": "none specified"}
    vmdata_df.fillna(value=fillna_values, inplace = True)

    # aggregate IP addresses into one column
    vmdata_df['ip_addresses'] = vmdata_df['Guest IP1'].map(str)+ ', ' + vmdata_df['Guest IP2'].map(str)+ ', ' + vmdata_df['Guest IP3'].map(str)+ ', ' + vmdata_df['Guest IP4'].map(str)
    vmdata_df['ip_addresses'] = vmdata_df.ip_addresses.str.replace(', no ip' , '')
    vmdata_df.drop(['Guest IP1', 'Guest IP2', 'Guest IP3', 'Guest IP4'], axis=1, inplace=True)

    # convert RAM and storage numbers into GB
    vmdata_df['vmdkUsed'] = vmdata_df['vmdkUsed']/1024
    vmdata_df['vmdkTotal'] = vmdata_df['vmdkTotal']/1024
    vmdata_df['vRam'] = vmdata_df['vRam']/1024

    vm_df_export = vmdata_df.round({'vmdkUsed':0,'vmdkTotal':0,'vRam':0})

    # pull in rows from VM Performance for storage performance metrics
    diskperf_list = []
    for file in file_name:
        disk_df = pd.read_excel(os.path.join(input_path, file), sheet_name='VM Performance')
        diskperf_list.append(disk_df)
    diskperf_df = pd.concat(diskperf_list, axis=0, ignore_index=True)

    perf_columns = ["MOB ID","Avg Read IOPS","Avg Write IOPS","Peak Read IOPS","Peak Write IOPS","Avg Read MB/s","Avg Write MB/s","Peak Read MB/s","Peak Write MB/s"]
    diskperf_df = diskperf_df.filter(items= perf_columns, axis= 1)
    diskperf_df.rename(columns = {
        'MOB ID':'vmId', 
        'Avg Read IOPS':'readIOPS',
        'Avg Write IOPS':'writeIOPS',
        'Peak Read IOPS':'peakReadIOPS',
        'Peak Write IOPS':'peakWriteIOPS',
        'Avg Read MB/s':'readThroughput',
        'Avg Write MB/s':'writeThroughput',
        'Peak Read MB/s':'peakReadThroughput',
        'Peak Write MB/s':'peakWriteThroughput'
        }, inplace = True)

    vm_consolidated = pd.merge(vmdata_df, diskperf_df, on = "vmId", how = "left")

    vm_consolidated.to_csv(os.path.join(output_path, '1_vmdata_df_lova.csv'))

    csv_file = "1_vmdata_df_lova.csv"
    return csv_file


def rvtools_conversion(**kwargs):
    input_path = kwargs['input_path']
    file_name = kwargs['file_name'] 
    output_path = kwargs['output_path']

    print()
    print("Parsing RVTools file(s) locally.")

    df_list = []
    for file in file_name:
        print(f'Reading {os.path.join(input_path, file)}')
        file_df = pd.read_excel(os.path.join(input_path, file), sheet_name='vInfo')
        df_list.append(file_df)
    vmdata_df = pd.concat(df_list, axis=0, ignore_index=True)

    # specify columns to KEEP - all others will be dropped
    keep_columns = ['VM ID','Cluster', 'Datacenter','Primary IP Address','OS according to the VMware Tools', 'DNS Name','Powerstate','CPUs','VM','Memory']
    if 'Provisioned MiB' in vmdata_df:
        keep_columns.extend(['Provisioned MiB','In Use MiB'])
    else:
        keep_columns.extend(['Provisioned MB','In Use MB'])
    vmdata_df = vmdata_df.filter(items= keep_columns, axis= 1)

    # rename remaining columns
    vmdata_df.rename(columns = {
        'VM ID':'vmId', 
        'VM':'vmName',
        'OS according to the VMware Tools':'os',
        'DNS Name':'os_name',
        'Powerstate':'vmState',
        'CPUs':'vCpu',
        'Memory':'vRam', 
        'Primary IP Address':'ip_addresses',
        'Folder':'vmFolder',
        'Resource pool':'resourcePool',
        'Cluster':'cluster', 
        'Datacenter':'virtualDatacenter'
        }, inplace = True)
    
    if 'Provisioned MiB' in vmdata_df:
        vmdata_df.rename(columns = {
            'Provisioned MiB':'vinfo_provisioned', 
            'In Use MiB':'vinfo_used'
            }, inplace = True)
    else:
        vmdata_df.rename(columns = {
            'Provisioned MB':'vinfo_provisioned', 
            'In Use MB':'vinfo_used'
            }, inplace = True)

    fillna_values = {"ip_addresses": "no ip", "os": "none specified"}
    vmdata_df.fillna(value=fillna_values, inplace = True)

    # pull in rows from vDisk for allocated storage
    diskdf_list = []
    for file in file_name:
        disk_df = pd.read_excel(os.path.join(input_path, file), sheet_name='vDisk')
        diskdf_list.append(disk_df)
    vdisk_df = pd.concat(diskdf_list, axis=0, ignore_index=True)
    
    vdisk_columns = ['VM ID']
    # Different versions of RVTools use either "MB" or "MiB" for storage; check for presence and include appropriate columns
    if 'Capacity MiB' in vdisk_df:
        vdisk_columns.extend(['Capacity MiB'])
    else:
        vdisk_columns.extend(['Capacity MB'])
    vdisk_df = vdisk_df.filter(items= vdisk_columns, axis= 1)

    if 'Capacity MiB' in vdisk_df:
        vdisk_df.rename(columns ={'Capacity MiB':'vmdkTotal'}, inplace = True)
    else:
        vdisk_df.rename(columns ={'Capacity MB':'vmdkTotal'}, inplace = True)
    vdisk_df.rename(columns ={'VM ID':'vmId'}, inplace = True)

    vdisk_df = vdisk_df.groupby(['vmId'])['vmdkTotal'].sum().reset_index()

    # pull in rows from vPartition for consumed storage
    partdf_list = []
    for file in file_name:
        part_df = pd.read_excel(os.path.join(input_path, file), sheet_name='vPartition')
        partdf_list.append(part_df)
    vpart_df = pd.concat(partdf_list, axis=0, ignore_index=True)
    
    part_list = ['VM ID']
    if 'Consumed MiB' in vpart_df:
        part_list.extend(['Consumed MiB'])
    else:
        part_list.extend(['Consumed MB'])
    vpart_df = vpart_df.filter(items= part_list, axis= 1)

    if 'Consumed MiB' in vpart_df:
        vpart_df.rename(columns ={'Consumed MiB':'vmdkUsed'}, inplace = True)
    else:
        vpart_df.rename(columns ={'Consumed MB':'vmdkUsed'}, inplace = True)
    vpart_df.rename(columns ={'VM ID':'vmId'}, inplace = True)

    vpart_df = vpart_df.groupby(['vmId'])['vmdkUsed'].sum().reset_index()

    vm_consolidated = pd.merge(vmdata_df, vdisk_df, on = "vmId", how = "left")
    vm_consolidated = pd.merge(vm_consolidated, vpart_df, on = "vmId", how = "left")

    # convert RAM and storage numbers into GB
    vm_consolidated['vinfo_provisioned'] = vm_consolidated['vinfo_provisioned']/1024
    vm_consolidated['vinfo_used'] = vm_consolidated['vinfo_used']/1024
    vm_consolidated['vmdkTotal'] = vm_consolidated['vmdkTotal']/1024
    vm_consolidated['vmdkUsed'] = vm_consolidated['vmdkUsed']/1024
    vm_consolidated['vRam'] = vm_consolidated['vRam']/1024

    # Replace NA values for used VMDK and total VMDK with 0 GB
    storage_na_values = {"vmdkTotal": 0, "vmdkUsed": 0}
    vm_consolidated.fillna(value=storage_na_values, inplace = True)

    # replace missing values from vDisk or vPartition with values from vInfo
    vm_consolidated.loc[vm_consolidated.vmdkTotal == 0, 'vmdkTotal'] = vm_consolidated.vinfo_provisioned
    vm_consolidated.loc[vm_consolidated.vmdkUsed == 0, 'vmdkUsed'] = vm_consolidated.vinfo_used

    vm_consolidated.to_csv(os.path.join(output_path, '1_vmdata_df_rvtools.csv'))
    csv_file = "1_vmdata_df_rvtools.csv"
    return csv_file


def ps_filter(**kwargs):
    output_path = kwargs['output_path']
    csv_file = kwargs['csv_file']
    power_state = kwargs['power_state']

    print()
    print("Filtering workloads based on power state.")
    vm_data_df = pd.read_csv(os.path.join(output_path, csv_file), index_col=0)
    if power_state == "p":
        vm_data_df_trimmed = vm_data_df[vm_data_df.vmState == "poweredOn"]
    elif power_state == "ps":
        vm_data_df_trimmed = vm_data_df[vm_data_df.vmState != "poweredOff"]
    else:
        pass

    vm_data_df_trimmed.to_csv(os.path.join(output_path, '2_vmdata_df_power_state.csv'))
    csv_file = "2_vmdata_df_power_state.csv"
    return csv_file


def include_workloads(**kwargs):
    output_path = kwargs['output_path']
    csv_file = kwargs['csv_file']
    infil = kwargs['include_filter']
    infilf = kwargs['include_filter_field']

    print()
    print(f'Including only those workloads where {infilf} includes {infil}')
    vm_data_df = pd.read_csv(os.path.join(output_path, csv_file), index_col=0)

    if infilf == "vmName":
        print("using exact string match on vmName")
        vm_data_df_trimmed = vm_data_df[vm_data_df['vmName'].isin(infil)]
    else:
        pattern = '|'.join(infil)
        vm_data_df_trimmed = vm_data_df[vm_data_df[infilf].str.contains(pattern, case=False) == True]
    vm_data_df_trimmed.to_csv(os.path.join(output_path, '3_vmdata_df_infil.csv'))
    csv_file = "3_vmdata_df_infil.csv"
    return csv_file


def exclude_workloads(**kwargs):
    output_path = kwargs['output_path']
    csv_file = kwargs['csv_file']
    exfil = kwargs['exclude_filter']
    exfilf = kwargs['exclude_filter_field']

    print()
    print(f'Excluding those workloads where {exfilf} includes {exfil}')
    vm_data_df = pd.read_csv(os.path.join(output_path, csv_file), index_col=0)

    if exfilf == "vmName":
        print("using exact string match on vmName")
        vm_data_df_trimmed = vm_data_df[~vm_data_df['vmName'].isin(exfil)]
    else:
        pattern = '|'.join(exfil)
        vm_data_df_trimmed = vm_data_df[vm_data_df[exfilf].str.contains(pattern, case=False) == False]
    vm_data_df_trimmed.to_csv(os.path.join(output_path, '4_vmdata_df_exfil.csv'))
    csv_file = "4_vmdata_df_exfil.csv"
    return csv_file


def assign_vcpu_group(df, bucket_size):
    """Add a vcpu_group column with bucket labels like '1-2_vCPU' or '1-4_vCPU'."""
    upper = df['vCpu'].apply(lambda v: max(1, math.ceil(v / bucket_size)) * bucket_size)
    lower = upper - bucket_size + 1
    df = df.copy()
    df['vcpu_group'] = lower.astype(int).astype(str) + '-' + upper.astype(int).astype(str) + '_vCPU'
    return df


def _sub_split_by_vcpu(df, bucket_size, output_path, prefix):
    """Split a DataFrame by vCPU bucket and write one CSV per bucket.
    Returns a list of written CSV filenames."""
    df = assign_vcpu_group(df, bucket_size)
    file_list = []
    for group_label, group_df in df.groupby('vcpu_group'):
        fname = f'{prefix}_vcpu_{group_label}.csv'
        group_df.drop(columns=['vcpu_group']).to_csv(os.path.join(output_path, fname))
        file_list.append(fname)
    return file_list


def build_vcpu_profiles(**kwargs):
    """Standalone vCPU grouping — used when -vg is specified without -wp."""
    output_path = kwargs['output_path']
    csv_file = kwargs['csv_file']
    bucket_size = kwargs['vcpu_grouping']

    print()
    print(f'Grouping workloads into vCPU buckets of {bucket_size}.')
    vm_data_df = pd.read_csv(os.path.join(output_path, csv_file), index_col=0)
    return _sub_split_by_vcpu(vm_data_df, bucket_size, output_path, '5')


def build_workload_profiles(**kwargs):
    output_path = kwargs['output_path']
    csv_file = kwargs['csv_file']
    profile_config = kwargs['workload_profiles']
    if kwargs['profile_list'] is not None:
        profile_list = kwargs['profile_list']
    vcpu_grouping = kwargs.get('vcpu_grouping')

    print()
    if vcpu_grouping is not None:
        print(f'Separating workloads into profiles based on "{profile_config}" with vCPU sub-grouping (buckets of {vcpu_grouping})')
    else:
        print(f'Separating workloads into profiles based on "{profile_config}"')
    #create list for storing file names
    wp_file_list = []

    vm_data_df = pd.read_csv(os.path.join(output_path, csv_file), index_col=0)

    match profile_config:
        case "all_clusters":
            print("Creating workload profiles by cluster.")
            workload_profiles = vm_data_df.groupby('cluster')
            # save resulting dataframes as csv files 
            for profile, profile_df in workload_profiles:
                if vcpu_grouping is not None:
                    wp_file_list.extend(_sub_split_by_vcpu(profile_df, vcpu_grouping, output_path, f'5_cluster_{profile}'))
                else:
                    profile_df.to_csv(os.path.join(output_path, f'5_cluster_{profile}.csv'))
                    wp_file_list.append(f'5_cluster_{profile}.csv')
    
        case "some_clusters":
            print("Creating custom cluster workload profiles.")
            workload_profiles = vm_data_df.groupby('cluster')

            # for list of clusters to keep, export to csv
            for profile, profile_df in workload_profiles:
                if profile in profile_list:
                    if vcpu_grouping is not None:
                        wp_file_list.extend(_sub_split_by_vcpu(profile_df, vcpu_grouping, output_path, f'5_cluster_{profile}'))
                    else:
                        profile_df.to_csv(os.path.join(output_path, f'5_cluster_{profile}.csv'))
                        wp_file_list.append(f'5_cluster_{profile}.csv')

            # if desired in original DF, drop rows for exported clusters
            if kwargs['include_remaining'] == True:
                vm_data_df_trimmed = vm_data_df[vm_data_df.cluster.isin(profile_list) == False]
                if vcpu_grouping is not None:
                    wp_file_list.extend(_sub_split_by_vcpu(vm_data_df_trimmed, vcpu_grouping, output_path, '5_cluster_remainder'))
                else:
                    vm_data_df_trimmed.to_csv(os.path.join(output_path, '5_cluster_remainder.csv'))
                    wp_file_list.append('5_cluster_remainder.csv')

        case "os":
            print("Creating workload profiles based on GUEST OPERATING SYSTEM using text match.")
            for match_string in profile_list:
                profile_df = vm_data_df[vm_data_df['os'].str.contains(match_string)]
                if vcpu_grouping is not None:
                    wp_file_list.extend(_sub_split_by_vcpu(profile_df, vcpu_grouping, output_path, f'5_guest_os_{match_string}'))
                else:
                    profile_df.to_csv(os.path.join(output_path, f'5_guest_os_{match_string}.csv'))
                    wp_file_list.append(f'5_guest_os_{match_string}.csv')
                
            # to keep remaining workloads, export all VM NOT matching to remainder CSV
            if kwargs['include_remaining'] == True:
                pattern = '|'.join(profile_list)
                vm_data_df_trimmed = vm_data_df[~vm_data_df['os'].str.contains(pattern, case=False)]
                if vcpu_grouping is not None:
                    wp_file_list.extend(_sub_split_by_vcpu(vm_data_df_trimmed, vcpu_grouping, output_path, '5_os_remainder'))
                else:
                    vm_data_df_trimmed.to_csv(os.path.join(output_path, '5_os_remainder.csv'))
                    wp_file_list.append('5_os_remainder.csv')

        case "vmName":
            print("Creating workload profiles based on VM NAME using text match.")

            for match_string in profile_list:
                profile_df = vm_data_df[vm_data_df['vmName'].str.contains(match_string)]
                if vcpu_grouping is not None:
                    wp_file_list.extend(_sub_split_by_vcpu(profile_df, vcpu_grouping, output_path, f'5_vmName_{match_string}'))
                else:
                    profile_df.to_csv(os.path.join(output_path, f'5_vmName_{match_string}.csv'))
                    wp_file_list.append(f'5_vmName_{match_string}.csv')

            # to keep remaining workloads, export all VM NOT matching to remainder CSV
            if kwargs['include_remaining'] == True:
                pattern = '|'.join(profile_list)
                vm_data_df_trimmed = vm_data_df[~vm_data_df['vmName'].str.contains(pattern, case=False)]
                if vcpu_grouping is not None:
                    wp_file_list.extend(_sub_split_by_vcpu(vm_data_df_trimmed, vcpu_grouping, output_path, '5_vmName_remainder'))
                else:
                    vm_data_df_trimmed.to_csv(os.path.join(output_path, '5_vmName_remainder.csv'))
                    wp_file_list.append('5_vmName_remainder.csv')
    return wp_file_list

