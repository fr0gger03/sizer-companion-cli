# Sizer Companion CLI

A Python command-line tool that normalizes virtual machine inventory data from **RVTools** or **LiveOptics** exports into clean, standardized CSV files suitable for use with VMware Cloud Foundation sizing tools.

Forked from the [VMware Cloud Sizer Companion CLI](https://github.com/vmware-samples/vmware-cloud-sizer-companion-cli) and repurposed for general workload inventory normalization.

## Description

**Eliminate the tedious work**

Has this ever happened to you?  You need to run some calculations to determine how much infrastructure capacity you need for a project - maybe it's a migration, maybe a DR project, maybe a storage migration, maybe sizing for a ransomware isolated recovery environment.

If you have ever struggled with questions such as...

- I have many workloads across **multiple environments** - how do I quickly process **multiple spreadsheets**?
- should I use how much capacity is **configured** or how much is **utilized**?
- can or should I keep my current **cluster alignment**?
- how do I quickly eliminate (or keep) virtual machines that are **powered off**?
- how do I only process specific workloads by **name**, **operating system**, or **cluster**?

Then this tool is for you - quickly process one or many spreadsheets (LiveOptics or RV-Tools), and include or exclude workloads or clusters, your workloads by operating system, cluster, or naming patterns.  Select all virtual machines, or only those powered on, or powered on and suspended.  Quickly get a clean set of inputs for processing sizing exercises.

## Features

- **Import** VM inventory from one or more RVTools or LiveOptics `.xlsx` exports
- **Describe** an environment — get a quick summary of VM counts, power states, guest OS distribution, cluster names, and resource totals
- **Filter by power state** — include only powered-on VMs, or powered-on and suspended
- **Include / exclude workloads** — filter by cluster name, guest OS, or exact VM name
- **Build workload profiles** — split output into separate files grouped by cluster, OS, or VM name patterns
- **Choose storage metric** — use provisioned or utilized storage capacity

## Installation

There are two ways to use this tool: download a pre-built release binary, or run from source with Python.

### Option 1 — Pre-built release (no Python required)

Download the latest release for your platform from the [Releases](../../releases) page:

- **Linux** — `sizer-linux`
- **macOS** — `sizer-macos`
- **Windows** — `sizer-windows.exe`

Make the binary executable (Linux/macOS) and run it:

```bash
chmod +x sizer-macos          # or sizer-linux
./sizer-macos --help
```

### Option 2 — Run from source

**Prerequisites:** Python >= 3.12, [uv](https://docs.astral.sh/uv/) (recommended) or pip.

```bash
# Clone the repository
git clone <repo-url>
cd sizer-companion-cli

# Install dependencies with uv
uv sync

# Or with pip
pip install -r requirements.txt
```

## Usage

All examples below use `uv run sizer_cli.py` (running from source). If you are using the pre-built release binary, replace `uv run sizer_cli.py` with the path to the binary (e.g. `./sizer-macos` or `./sizer-linux`).

By default, input files are read from `./input/` and output files are written to `./output/` relative to the current working directory. You can override these with the `--input_dir` and `--output_dir` flags — this is especially useful when running the standalone binary from an arbitrary location.

### Describe

Print a summary of the imported environment (VM count, power states, OS breakdown, clusters, resource totals):

```bash
# From source
uv run sizer_cli.py describe -fn inventory.xlsx -ft rv-tools
uv run sizer_cli.py describe -fn capture.xlsx -ft live-optics

# Release binary with custom directories
./sizer-macos describe -fn inventory.xlsx -ft rv-tools \
  -id /path/to/input -od /path/to/output
```

### Prepare

Import, transform, and export normalized data:

```bash
# Basic import — all VMs, utilized storage (default)
uv run sizer_cli.py prepare -fn inventory.xlsx -ft rv-tools

# Include only powered-on VMs
uv run sizer_cli.py prepare -fn inventory.xlsx -ft rv-tools -ps p

# Include powered-on and suspended VMs
uv run sizer_cli.py prepare -fn inventory.xlsx -ft rv-tools -ps ps

# Include only specific clusters
uv run sizer_cli.py prepare -fn inventory.xlsx -ft rv-tools \
  -infil ClusterA ClusterB -iff cluster

# Exclude VMs by guest OS pattern
uv run sizer_cli.py prepare -fn inventory.xlsx -ft rv-tools \
  -exfil "Windows 2008" -eff os

# Use provisioned storage instead of utilized
uv run sizer_cli.py prepare -fn inventory.xlsx -ft rv-tools -sc PROVISIONED

# Build workload profiles — one file per cluster
uv run sizer_cli.py prepare -fn inventory.xlsx -ft rv-tools -wp all_clusters

# Build profiles for selected clusters, keep the rest in a remainder file
uv run sizer_cli.py prepare -fn inventory.xlsx -ft rv-tools \
  -wp some_clusters -pl ClusterA ClusterB -ir

# Multiple input files
uv run sizer_cli.py prepare -fn site1.xlsx site2.xlsx -ft rv-tools

# Release binary with custom input/output directories
./sizer-linux prepare -fn site1.xlsx site2.xlsx -ft rv-tools \
  -id ~/exports -od ~/results
```

### CLI Reference

| Flag | Long Form | Description |
|------|-----------|-------------|
| `-fn` | `--file_name` | Space-separated input file name(s) |
| `-ft` | `--file_type` | `rv-tools` or `live-optics` |
| `-id` | `--input_dir` | Directory containing input files (default: `./input/`) |
| `-od` | `--output_dir` | Directory for output files (default: `./output/`, created automatically if missing) |
| `-ps` | `--power_state` | `p` (powered on only) or `ps` (powered on + suspended) |
| `-infil` | `--include_filter` | Text pattern(s) to keep |
| `-iff` | `--include_filter_field` | Field for include filter: `cluster`, `os`, or `vmName` |
| `-exfil` | `--exclude_filter` | Text pattern(s) to exclude |
| `-eff` | `--exclude_filter_field` | Field for exclude filter: `cluster`, `os`, or `vmName` |
| `-wp` | `--workload_profiles` | Grouping mode: `all_clusters`, `some_clusters`, `os`, or `vmName` |
| `-pl` | `--profile_list` | Names/patterns for workload profile grouping |
| `-ir` | `--include_remaining` | Keep unmatched VMs in a remainder file |
| `-sc` | `--storage_capacity` | `PROVISIONED` or `UTILIZED` (default) |
| `-o` | `--output_format` | Output format (default: `csv`) |

## Project Structure

```
sizer-companion-cli/
├── sizer_cli.py        # CLI entry point — argument parsing and subcommands
├── sizer_fxns.py       # Orchestration logic for describe and prepare workflows
├── data_transform.py   # Data import, normalization, filtering, and profiling
├── sizer_output.py     # Terminal and table output helpers
├── main.py             # Placeholder entry point (unused by CLI)
├── input/              # Place source .xlsx files here
├── output/             # Transformed CSV output files
├── pyproject.toml      # Project metadata and dependencies
├── requirements.txt    # Pip-compatible dependency list
└── LICENSE             # MIT License
```

## License

MIT — see [LICENSE](LICENSE) for details.
