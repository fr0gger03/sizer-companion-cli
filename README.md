# ACC Sizer Companion CLI

A Python command-line tool that normalizes virtual machine inventory data from **RVTools** or **LiveOptics** exports into clean, standardized CSV files suitable for use with VMware Cloud Foundation sizing tools.

Forked from the [VMware Cloud Sizer Companion CLI](https://github.com/vmware-samples/vmware-cloud-sizer-companion-cli) and repurposed for general workload inventory normalization.

## Features

- **Import** VM inventory from one or more RVTools or LiveOptics `.xlsx` exports
- **Describe** an environment — get a quick summary of VM counts, power states, guest OS distribution, cluster names, and resource totals
- **Filter by power state** — include only powered-on VMs, or powered-on and suspended
- **Include / exclude workloads** — filter by cluster name, guest OS, or exact VM name
- **Build workload profiles** — split output into separate files grouped by cluster, OS, or VM name patterns
- **Choose storage metric** — use provisioned or utilized storage capacity

## Prerequisites

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

```zsh path=null start=null
# Clone the repository
git clone <repo-url>
cd acc-sizer-companion-cli

# Install dependencies with uv
uv sync

# Or with pip
pip install -r requirements.txt
```

## Usage

Place your **unmodified** RVTools or LiveOptics `.xlsx` file(s) in the `input/` directory, then run one of the subcommands below. Output files are written to the `output/` directory.

**NOTE** - if you have python 3.12 or later installed you should be ale to run the script directly without the use of 'uv'

### Describe

Print a summary of the imported environment (VM count, power states, OS breakdown, clusters, resource totals):

```zsh path=null start=null
uv run sizer_cli.py describe -fn inventory.xlsx -ft rv-tools
uv run sizer_cli.py describe -fn capture.xlsx -ft live-optics
```

### Prepare

Import, transform, and export normalized data:

```zsh path=null start=null
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
```

### CLI Reference

| Flag | Long Form | Description |
|------|-----------|-------------|
| `-fn` | `--file_name` | Space-separated input file name(s) (must be in `input/`) |
| `-ft` | `--file_type` | `rv-tools` or `live-optics` |
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
acc-sizer-companion-cli/
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
