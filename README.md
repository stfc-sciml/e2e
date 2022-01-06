# E2E: Table of Contents
- [1. Synopsis](#1-synopsis)
- [2. Benchmarks](#2-benchmarks)
  * [2.1 Organisation](#21-organisation)
  * [2.2 Benchmarks Datasets](#22-datasets)
- [3. Installation and Usage](#3-installation-and-usage)
- [4. Citation](#4-citation)
- [5. Acknowledgments](#5-acknowledgments)



# 1. Synopsis

This repository provides the code, documentation and results of the End-to-End (e2e) benchmarking project.

# 2. Benchmarks 


## 2.1 Organisation

The end to end benchmarking project consists of two benchmarks:

1. **Case 1: RELION**: The RELION end-to-end benchmark reproduces a full end-to-end refinement using the RELION software, including 2D classification, 3D classification, 3D refinement and polishing.

2. **Case 2: Cloud Masking**: The cloud masking benchmark prepares, trains, and evaluates a U-Net style segmentation model on Sentinel-3 data for cloud masking.

The source tree, which captures these aspects, is organised as follows:

```bash
├── README.md                   <This file>
└── case1/                      <Root folder for the Case 1: RELION benchmark>
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

The `download.sh` script in this directory can be used to download all the data for both benchmarks. For more information on specific datasets used both both datasets please see:

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

# 4. Contributors and Citation

## 4.1 Contributors

These examples were developed by the [Scientific Machine Learning (SciML) Group](https://bityl.co/ANZz) at the [Rutherford Appleton Laboratory (RAL)](https://bityl.co/ANa0), [Science and Technology Facilities Council (STFC)](https://stfc.ukri.org/index.cfm), UK in collaboration with [Intel Corporation](https://www.intel.co.uk/) through the [Alan Turing Institute’s](https://www.turing.ac.uk/) Data Science at Scale programme. Key contributors are: 

* Jeyan Thiyagalingam, RAL, STFC,
* Samuel Jackson, RAL, STFC,
* Martyn Winn, RAL, STFC, 
* Manos Farsarakis, Intel, and
* Tony Hey, RAL, STFC.


Cite these end-to-end benchmarks as follows:

```
@misc{sciml-e2e:2021,
    title  = {End-to-End Benchmarking for AI for Science: Two Examples},
    author = {Samuel Jackson, Martyn Winn,  Manos Farsarakis, Jeyan Thiyagalingam, Tony Hey},
    url    = {https://github.com/stfc-sciml/e2e},
    year   = {2021}
}
```

Please email scdsciml@stfc.ac.uk for any clarification regarding these examples. 

# 5. Acknowledgments

*This work was supported by the Alan Turing Institute’s Data Science at Scale programme through a partnership with Intel.*

<div style="text-align: right">◼︎</div>

