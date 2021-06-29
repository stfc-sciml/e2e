# Case 1 Overview

This folder contains scripts for the Relion End-to-End benchmark.

Contents:
 - [Installation](#installation)
 - [Running benchmarks](#running-benchmarks)
 - [Datasets](#datasets)

## Installation
To run the benchmark you will need a copy of [relion](https://github.com/3dem/relion) and [ctffind](https://grigoriefflab.umassmed.edu/ctffind4).

### Using a container

The easiest method to get Relion running on you system is to use a container. This is the recommended way to run  this suite of benchmarks. NVIDIA provide a [containerized version of Relion](https://ngc.nvidia.com/catalog/containers/hpc:relion). This benchmark suite makes use of the Singularity version of that container.

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

A relion pipeline is defined by a sequence of Relion commands, e.g. `relion_refine`, `relion_postprocess` `relion_mask_create` etc. Pipeline scripts use intermidate files (provided with the dataset) from the full refinement as input, allowing the user to only run a single component, or to run multiple pipelines in parallel. All pipeline scripts are located in the `benchmark_scripts` folder.

To run a pipeline, use the `benchmark_scripts/benchmark_relion.py` tool. This tool requires the use to setup several environment variables to configure the run.

| Name                 | Description                                                                                                                                                                                                                      | Example                                                                        |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| RELION_PROJ_DIR      | Relion project directory containing the data files for the benchmark                                                                                                                                                             | RELION_PROJ_DIR="data/10338"                                                   |
| RELION_OUTPUT_DIR    | Output directory to store the results of the benchmark                                                                                                                                                                           | RELION_OUTPUT_DIR="runs/pearl/test_job"                                        |
| RELION_CMD           | Command used to run Relion if using a singularity container. If the Relion singularity container is used then this option must be set. If Relion is not being run from within a singularity container then this must be omitted. | RELION_CMD="singularity run --nv -B $BASE_DIR -H $RELION_PROJ_DIR $RELION_IMG" |
| RELION_CPUS_PER_TASK | Optional. Number of CPUS used per task. This option is passed to the `-j` flag in Relion commands                                                                                                                                             | RELION_CPUS_PER_TASK=2                                                         |
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

### Benchmark Outputs

All output from the running the Relion pipeline will be output to the `RELION_OUTPUT_DIR`. Additional the benchmarking tool will also output a `metrics.json` file. This file contains the timings and quality metrics (if defined) of each step, along with some metadata about the run. An example of the output is shown below.

In this example:

 - `pipeline_file`: the pipeline file run to produce this `metrics.json`
 - `total_duration`: is the total execution time for the pipeline
 - `steps`: contains the timing & quality metrics for each step in the pipeline.
    - `duration`:  total execution time of the step.
 - `RELION_*`: the environment variables used by this run.

```json
{
  "pipeline_file": "benchmark_scripts/rabbit_aldolase_benchmark.sh",
  "total_duration": 16983.38385272026,
  "steps": [
    {
      "name": "relion_refine_mpi",
      "duration": 14575.145715475082,
      "acc_rotation": 1.213,
      "acc_translation": 0.47824,
      "resolution": 3.629367
    },
    {
      "name": "relion_mask_create",
      "duration": 41.833229780197144
    },
    {
      "name": "relion_postprocess",
      "duration": 11.278026342391968,
      "_rlnFinalResolution": 3.150769,
      "_rlnBfactorUsedForSharpening": -114.15386,
      "_rlnParticleBoxFractionSolventMask": 44.736736
    },
    {
      "name": "relion_ctf_refine_mpi",
      "duration": 2354.8725686073303,
      "beam_tilt_x": -0.11172,
      "beam_tilt_y": 0.104509
    }
  ],
  "RELION_OPT_FLAGS": "--gpu --dont_combine_weights_via_disc --pool 30",
  "RELION_CMD": "singularity run --nv -B /mnt/beegfs/work/stfc/pearl008/intel-e2e-benchmark/case1 -H /mnt/beegfs/work/stfc/pearl008/intel-e2e-benchmark/case1/data/10338 /mnt/beegfs/work/stfc/pearl008/intel-e2e-benchmark/case1/relion.sif",
  "RELION_CPUS_PER_TASK": "2",
  "RELION_OUTPUT_DIR": "/mnt/beegfs/work/stfc/pearl008/intel-e2e-benchmark/case1/runs/pearl/job_28257",
  "RELION_PROJ_DIR": "/mnt/beegfs/work/stfc/pearl008/intel-e2e-benchmark/case1/data/10338",
  "RELION_IMG": "/mnt/beegfs/work/stfc/pearl008/intel-e2e-benchmark/case1/relion.sif"
}
```

## Datasets

Two datasets are provided with this benchmark. The details of each individual
dataset are given in the table below. 


| Dataset | Published    | Size (TB) | Description                                                                                                                                      |
|---------|--------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| RELION tutorial | [Wong et al, eLife 2014](http://dx.doi.org/10.7554/eLife.03080) | 0.08 | Small dataset from the Relion tutorial for rapid testing of setup. Cryo-EM structure of the Plasmodium falciparum 80S ribosome bound to the anti-protozoan drug emetine |
| Rabbit muscle aldolase  | [EMPIAR 10338](https://www.ebi.ac.uk/pdbe/emdb/empiar/entry/10338/)          | 1.4      | Rabbit muscle aldolase movies obtained using a Talos Arctica (200 kV) equipped with a K2.|