# Case 1 Overview

This folder contains scripts for the Relion End-to-End benchmark.

## Installation
To run the benchmark you will need a copy of [relion](https://github.com/3dem/relion) and [ctffind](https://grigoriefflab.umassmed.edu/ctffind4).

### Using a container

The easiest method to get Relion running on you system is to use a container. This is the recommended way to run the this suite of benchmarks. NVIDIA provide a [containerized version of Relion](https://ngc.nvidia.com/catalog/containers/hpc:relion). This benchmark suite makes use of the Singularity version of that container.

To build the container `cd` into the `case1` folder and run the following command:

```bash
singularity build -F relion.sif relion.def
```

### Compiling from Source

You'll need to install Relion and ctffind on your machine.
 - [Relion installation instructions](https://github.com/3dem/relion#installation)
 - [Ctffind installation instructions](https://grigoriefflab.umassmed.edu/ctffind4) 


## Running benchmarks
Relion benchmarks are run using the `benchmark_relion.py` script. This script is the entrypoint for setting up the environment, running relion, and timing each step.

A relion pipeline is defined by a sequence of Relion commands. 
