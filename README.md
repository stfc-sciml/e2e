# E2E: Table of Contents
- [1. Synopsis](#1-synopsis)
- [2. Benchmarks](#2-benchmarks)
  * [2.1 Organisation](#21-organisation)
  * [2.2 Benchmarks Datasets](#22-datasets)
- [3. Installation and Usage](#3-installation-and-usage)
- [4. Citation](#4-citation)
- [5. Acknowledgments](#5-acknowledgments)



# 1. Synopsis

This repository provides the code, documentation and results of the End-2-End benchmarking project.

# 2. Benchmarks 


## 2.1 Organisation

The end to end benchmarking project consists of two benchmarks:

1. **Case 1: Relion**: The Relion end to end benchmark reproduces a full end to end refinement using Relion, including 2D classification, 3D classification, 3D refinement and polishing.

2. **Case 2: Cloud Mask**: The cloud mask benchmark prepares, trains, and evaluates a U-Net style segmentation model on Sentinel-3 data for cloud masking.

The source tree, which captures these aspects,  is organised as follows:

```bash
├── README.md                   <This file>
└── case1/                      <Root folder for the Case 1: Relion benchmark>
    ├── benchmark_scripts/      <Benchmark scripts & python implementation>
    ├── hpc/                    <Scripts for running the benchmark on HPC systems>
    └── runs/                   <Output captured for runs on each HPC system> 
└── case2/                      <Root folder for the Case 2: Cloud Mask benchmark>
    ├── e2e_benchmark/          <Benchmark python implementation>
    ├── hpc/                    <Scripts for running the benchmark on HPC systems>
    └── runs/                   <Output captured for runs on each HPC system> 
```

We have annotated the purpose of each folder/directory within `<>`.  

## 2.2 Datasets 

The `download.sh` script in thsi directory can be used to download all the data for both benchmarks. For more infomation on specific datasets used both both datasets please see:

 - [Case 1 Datasets](./case1/README.md#datasets)
 - [Case 2 Datasets](./case2/README.md#datasets)

The download script requires `aws-shell` to be installed and available on
the PATH. To install `aws-shell` run:

```bash
pip install aws-shell
```

To download benchmark data run:

```bash
./download.sh <output-folder>
```

For example:

```bash
./download.sh data
```

# 3. Installation and Usage

Please consult documentation for each of the individual benchmark cases.
 - Case 1: See the [README](./case1/README.md) for getting started.
 - Case 2: See the [README](./case2/README.md) for getting started.

# 5. Acknowledgments

*This work was supported by the Alan Turing Institute’s Data Science at Scale programme through a partnership with Intel.*

<div style="text-align: right">◼︎</div>

