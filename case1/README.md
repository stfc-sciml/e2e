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

And the Relion executable commands will need to be visible on the PATH. 

## Running benchmarks
Relion benchmarks are run using the `benchmark_relion.py` script. This script is the entrypoint for setting up the environment, running relion, and timing each step.

A relion pipeline is defined by a sequence of Relion commands, e.g. `relion_refine`, `relion_postprocess` `relion_mask_create` etc. Pipeline scripts use intermidate files (provided with the dataset) from the full refinement as input, allowing the user to only run a single component, or to run multiple pipelines in parallel.

To run a pipeline, use the `benchmark_scripts/benchmark_relion.py` tool. This tool requires the use to setup several environment variables to configure the run.

| Name                 | Description                                                                                                                                                                                                                      | Example                                                                        |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| RELION_PROJ_DIR      | Relion project directory containing the data files for the benchmark                                                                                                                                                             | RELION_PROJ_DIR="data/10338"                                                   |
| RELION_OUTPUT_DIR    | Output directory to store the results of the benchmark                                                                                                                                                                           | RELION_OUTPUT_DIR="runs/pearl/test_job"                                        |
| RELION_CMD           | Command used to run Relion if using a singularity container. If the Relion singularity container is used then this option must be set. If Relion is not being run from within a singularity container then this must be omitted. | RELION_CMD="singularity run --nv -B $BASE_DIR -H $RELION_PROJ_DIR $RELION_IMG" |
| RELION_CPUS_PER_TASK | Optional. No. of CPUS used per task. This option is passed to the `-j` flag in Relion commands                                                                                                                                             | RELION_CPUS_PER_TASK=2                                                         |
| RELION_OPT_FLAGS     | Optional. Additional optimization flags to pass to relion.                                                                                                                                                                                 | RELION_OPT_FLAGS=='--gpu --dont_combine_weights_via_disc --pool 30'            |

For example:

```bash
#Location of the case1 folder
export BASE_DIR="/mnt/beegfs/work/stfc/pearl008/intel-e2e-benchmark/case1"
# Location of the relion singularity image
export RELION_IMG="$BASE_DIR/relion.sif"
# Relion project directory data
export RELION_PROJ_DIR="$BASE_DIR/data/10338"
# Location to store output files
export RELION_OUTPUT_DIR="$BASE_DIR/runs/pearl/job_$SLURM_JOB_ID"
# Relion command
export RELION_CMD="singularity run --nv -B $BASE_DIR -H $RELION_PROJ_DIR $RELION_IMG"
# Number of cpus to use with -j option
export RELION_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK
# Additional optimization flags
export RELION_OPT_FLAGS='--gpu --dont_combine_weights_via_disc --pool 30'

benchmark_scripts/benchmark_relion.py benchmark_scripts/rabbit_aldolase_benchmark.sh
```

Several more examples are given in jobs scripts in the `hpc` folder.
