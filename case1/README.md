# Case 1 Overview

This folder contains scripts for the Relion End-to-End benchmark.

Contents:
 - [Quick Start](#quick-start-guide)
 - [Installation](#installation)
 - [Running benchmarks](#running-benchmarks)
 - [Benchmark Outputs](#benchmark-outputs)
 - [Datasets](#datasets)
 - [Pipeline Stages](#stages)
 - [Results](#results)

## Quick Start Guide

1. Clone the repository and `cd` into the folder.

```bash
git clone git@github.com:stfc-sciml/e2e.git
cd e2e/case1
```

2. Install Relion on your system (if not already available). Follow the following guide:
   - [Relion installation instructions](https://github.com/3dem/relion#installation)

3. Download the dataset folder

```bash
../download.sh /path/to/local/data
```

4. Setup the relevant environment variables and run benchmark stages. The following example will run the [case1/benchmark_scripts/10338/pipeline_class2d_0.sh](pipeline_class2d_0.sh) stage:

```bash
#Location of the case1 folder
export BASE_DIR="/home/nx07/nx07/sljack92/intel-e2e-benchmark/case1"
# Relion data folder
export RELION_PROJ_DIR="/path/to/local/data/relion/10338"
# Location to store output files
export RELION_OUTPUT_DIR="$BASE_DIR/runs/clx/pipeline_class2d_0"
# Relion command (make sure it's on the path)
export PATH="/home/nx07/nx07/sljack92/relion/relion-3.1.2-clx/build/bin:$PATH"
export RELION_CMD=""

# Number of cpus to use
export RELION_NUM_CPUS=23
# Number of cpu threads to use with --j option
export RELION_CPU_THREADS_PER_TASK=4
# Additional optimization flags
export RELION_OPT_FLAGS="--dont_combine_weights_via_disc --cpu --pool $RELION_NUM_CPUS --j $RELION_CPU_THREADS_PER_TASK"
# Additional MPI flags
export RELION_MPI_FLAGS="-n $RELION_NUM_CPUS"


# Run the pipeline stage
./benchmark_scripts/benchmark_relion.py ./benchmark_scripts/10338/pipeline_class2d_0.sh
```

See the [Running benchmarks](#running-benchmarks) section for more details on each environment variable. There are also a number of example files in the [hpc](case1/hpc) folder of this project.

5. Get the output in the `$RELION_OUTPUT_DIR` folder. For more details see section [Benchmark Outputs](#benchmark-outputs) .


## Installation
To run the benchmark you will need a copy of [relion](https://github.com/3dem/relion) and [ctffind](https://grigoriefflab.umassmed.edu/ctffind4).

### Using a container

The easiest method to get Relion running on you system is to use a container. This is the recommended way to run  this suite of benchmarks. NVIDIA provide a [containerized version of Relion](https://ngc.nvidia.com/catalog/containers/hpc:relion). This benchmark suite makes use of the Singularity version of that container.

To build the container `cd` into the `case1` folder and run the following command:

```bash
singularity build -F relion.sif relion.def
```

### Compiling from Source

You'll need to install Relion and ctffind on your machine. Please follow the installation instructions below:

 - [Relion installation instructions](https://github.com/3dem/relion#installation)
 - [Ctffind installation instructions](https://grigoriefflab.umassmed.edu/ctffind4) 

Finally, make sure that the Relion executable commands are visible on the PATH. 

## Running benchmarks

A full end to end refinement using Relion is can take days or even weeks of time. To facilitate running an end-to-end benchmark the full refinement is broken up into a number of stages. Each Relion stage is defined by a sequence of Relion commands, e.g. `relion_refine`, `relion_postprocess` `relion_mask_create` etc. Each stage uses intermediate files (provided with the dataset) from the full refinement as input, allowing the user to only run a single stage, or to run multiple stages in parallel. All scripts are located in the `benchmark_scripts` folder.

Relion benchmarks are run using the `benchmark_relion.py` script. This script is the entrypoint for setting up the environment, running Relion, and timing each step. To run a pipeline, use the `benchmark_scripts/benchmark_relion.py` tool. This tool requires the user to setup several environment variables to configure the run.

| Name                 | Description                                                                                                                                                                                                                      | Example                                                                        |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| RELION_PROJ_DIR      | Relion project directory containing the data files for the benchmark                                                                                                                                                             | RELION_PROJ_DIR="data/10338"                                                   |
| RELION_CMD           | Command used to run Relion if using a singularity container. If the Relion singularity container is used then this option must be set. If Relion is not being run from within a singularity container then this must be omitted. | RELION_CMD="singularity run --nv -B $BASE_DIR -H $RELION_PROJ_DIR $RELION_IMG" |
| RELION_OUTPUT_DIR    | Optional. Default = `relion_output`. Output directory to store the results of the benchmark                                                                                                                                                                           | RELION_OUTPUT_DIR="runs/pearl/test_job"                                        |
| RELION_CPUS_PER_TASK | Optional. Default = `1`. Number of CPUS used per task. This option is passed to the `-j` flag in Relion commands                                                                                                                                             | RELION_CPUS_PER_TASK=2                                                         |
| RELION_OPT_FLAGS     | Optional. Additional optimization flags to pass to relion.                                                                                                                                                                                 | RELION_OPT_FLAGS=='--gpu --dont_combine_weights_via_disc --pool 30'            |
| RELION_MPI_FLAGS      | Optional. Additional options to pass to mpirun    | RELION_MPI_FLAGS='--mca opal_warn_on_missing_libcuda 0' |


### Example Running with Singularity a Container

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

# Run the pipeline stage
benchmark_scripts/benchmark_relion.py ./benchmark_scripts/10338/pipeline_refine3d_2.sh
```

### Example Running with a compiled version of Relion

```bash
#Location of the case1 folder
export BASE_DIR="/home/nx07/nx07/sljack92/intel-e2e-benchmark/case1"
# Relion project directory data
export RELION_PROJ_DIR="/home/nx07/nx07/sljack92/relion/10338"
# Location to store output files
export RELION_OUTPUT_DIR="$BASE_DIR/runs/clx/job_$SLURM_JOB_ID"
# Relion command
export PATH="/home/nx07/nx07/sljack92/relion/relion-3.1.2-clx/build/bin:$PATH"
export RELION_CMD=""
# Number of cpus to use
export RELION_NUM_CPUS=${SLURM_NTASKS:-23}
# Number of cpu threads to use with --j option
export RELION_CPU_THREADS_PER_TASK=4
# Additional optimization flags
export RELION_OPT_FLAGS="--dont_combine_weights_via_disc --cpu --pool $RELION_NUM_CPUS --j $RELION_CPU_THREADS_PER_TASK"
# Additional MPI flags
export RELION_MPI_FLAGS="-n $RELION_NUM_CPUS"


# Run the pipeline stage
./benchmark_scripts/benchmark_relion.py ./benchmark_scripts/10338/pipeline_class2d_0.sh
```

Several more examples are provided in the form of jobs scripts in the [hpc](case1/hpc) folder of this project.

### CPU Only jobs
When running using the Relion singularity container on a CPU only machine, you must add the `-gpu_disable_check` option. This disables NVIDIA's check for a GPU's existence in the [nventry](https://gitlab.com/NVHPC/nventry#options) startup script. For example you can change the `RELION_CMD` to:

```bash
export RELION_CMD="singularity run --nv -B $BASE_DIR -H $RELION_PROJ_DIR $RELION_IMG -gpu_disable_check"
```

### Optimization options

The `-j` option for Relion can be set with the environment variable `RELION_CPUS_PER_TASK`. Several other optimization options can be passed to `relion_refine_mpi` commands using the environment variable `RELION_OPT_FLAGS`. Below is a list of common optimization flags from the Relion documentation:

| Name                            | Description                                                                                                                                                                                                                  |   |
|---------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| --dont_combine_weights_via_disc | By default large messages are passed between MPI processes through reading and writing of large files on the computer disk. By giving this option, the messages will be passed through the network instead.                  |   |
| --gpu                           | Use GPU-acceleration. We often use this option.                                                                                                                                                                              |   |
| --pool                          | This determines how many particles are processed together in a function call.                                                                                                                                                |   |
| --no_parallel_disc_io           | By default, all MPI slaves read their own particles (from disk or into RAM). Use this option to have the master read all particles, and then send them all through the network.                                              |   |
| --preread_images                | By default, all particles are read from the computer disk in every iteration. Using this option, they are all read into RAM once, at the very beginning of the job instead.                                                  |   |
| --scratch_dir                   | By default, particles are read every iteration from the location specified in the input STAR file. By using this option, all particles are copied to a scratch disk, from where they will be read (every iteration) instead. |   |

## Benchmark Outputs

All output from the running the Relion pipeline will be output to the `RELION_OUTPUT_DIR`. Additional the benchmarking tool will also output a `metrics.json` file. This file contains the timings and quality metrics (if defined) of each step, along with some metadata about the run. All durations are in units of seconds. Additional metrics captured by steps in the Relion workflow can be used to monitor the correctness of the processing. These include:

| Name                               | Step            | Relion Command           | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|------------------------------------|-----------------|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| resolution                         | Refine3D        | relion_refine_mpi        | estimated resolution of the refined reconstruction. This takes into account the whole box including the (noisy) solvent region, and so will be worse than that reported by the subsequent PostProcessing job.                                                                                                                                                                                                                                               |
| acc_rotation                       | Refine3D        | relion_refine_mpi        | estimated angular accuracy of the particle set (projection direction and in-plane rotation). The attainable accuracy will depend on the dataset, but should improve with refinement.                                                                                                                                                                                                                                                                        |
| acc_translation                    | Refine3D        | relion_refine_mpi        | estimated translation accuracy of the particle set (2D origin offset). The attainable accuracy will depend on the dataset, but should improve with refinement.                                                                                                                                                                                                                                                                                              |
| _rlnFinalResolution                | PostProcess     | relion_postprocess       | estimated resolution from PostProcessing. This is the resolution for the molecular region, and should be better than that reported for the reconstruction box.                                                                                                                                                                                                                                                                                              |
| _rlnParticleBoxFractionSolventMask | PostProcess     | relion_postprocess       | fraction of the reconstruction box which is considered to be surrounding solvent. This is an analysis of the mask from the MaskCreate job. The volume of solvent masked out depends on the threshold used and how soft the edge is, but should be physically reasonable.                                                                                                                                                                                    |
| _rlnBfactorUsedForSharpening       | PostProcess     | relion_postprocess       | B factor used for sharpening the postprocessed map. The B factor represents the fall off of the structure factor amplitude with resolution, and is estimated by the PostProcessing task. Compensating for this overall fall-off can enhance the signal (but also the noise).                                                                                                                                                                                |
| _rlnCurrentResolution              | Class2D/Class3D | relion_refine_mpi        | estimated overall resolution of the dataset. This is for the full heterogeneous dataset, before the 2D or 3D classes are separated out.                                                                                                                                                                                                                                                                                                                     |
| _rlnNrClasses                      | Class2D/Class3D | relion_refine_mpi        | number of 2D or 3D classes. This is set on input, so this is just a sanity check.                                                                                                                                                                                                                                                                                                                                                                           |
| classX_occ                         | Class3D         | relion_refine_mpi        | the fractional occupancy of the 3D classes. There may be one or more classes with significant occupancy, representing discrete conformational states of the molecule. Classes with low occupancy may be rare conformational states, or simply noise.                                                                                                                                                                                                        |
| beam_tilt_x / beam_tilt_y          | CtfRefine       | relion_ctf_refine_mpi    | data-driven estimation of the beam tilt in the microscope. These are calculated for each optics group, which represent subsets of micrographs collected on the same microscope under the same settings.                                                                                                                                                                                                                                                     |
| relion_motion_refine params        | Polish          | relion_motion_refine_mpi | particle polishing parameters determined by the training phase. As in the initial MotionCorrection job, Relion tries to correct for beam-induced motion of the particles. Now that the particles have been identified and refined, a more accurate correction can be made. The Bayesian model uses a prior with 3 parameters “sigma for velocity”, “sigma for divergence”, “sigma for acceleration” which ensure a smooth distribution of particles tracks. |
| pixel_size                         | Extract         | relion_preprocess_mpi    | pixel size (in Angstrom) of particles (small 2D images) extracted from the original large micrographs. In the early stages, the particles are under-sampled (larger pixel size) to save compute/memory when the full resolution is not required. This is a sanity check, as it is an input to the Extract job.                                                                                                                                              |
| particle_size                      | Extract         | relion_preprocess_mpi    | size in pixels of the extracted particles. As the sampling increases, the pixel size decreases and the number of pixels increases. This is a sanity check, as it is an input to the Extract job.                                                                                                                                                                                                                                                            |

An example of the output for a single stage is shown below. In example below:

 - `pipeline_file`: the pipeline file run to produce this `metrics.json`
 - `total_duration`: is the total execution time for the pipeline
 - `steps`: contains the timing & quality metrics for each step in the pipeline.
    - `duration`:  total execution time of the step.
 - `RELION_*`: the environment variables used by this run.

```json
{
  "pipeline_file": "benchmark_scripts/10338/pipeline_refine3d_2.sh",
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

## Stages

### Rabbit Muscle Aldolase (10338)

All of these stages roughly reproduce the workflow of published dataset. A brief description of what each stage of the pipeline does is given below:

| Name                   | Description                                                                                                                                                                                         |   |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| pipeline_class2d_0.sh |  2D classification.                        |   |
| pipeline_class3d_1.sh |  3D classification and selection of particles in the top class.                        |   |
| pipeline_refine3d_2.sh | 3D refinement of the top 3D class (2x sampling), mask creation, post-processing, and per-particle Ctf refinement (defocus and global astigmatism) and beam tilt estimation.                         |   |
| pipeline_refine3d_3.sh | 3D refinement with Ctf refined particles (2x sampling), mask creation, post-processing, re-extract particles at original sampling, importing re-sampled reference, and removing duplicate particles |   |
| pipeline_refine3d_4.sh | 3D refinement with fully sampled particles.                                                                                                                                                         |   |
| pipeline_polish_5.sh   | Polishing (training and applying).                                                                                                                                                                  |   |

## Results
A detailed breakdown of results can be found in [case1/docs/RESULTS.md](docs/RESULTS.md). Raw logs and tables of results can be found in [case1/runs](case1/runs). The tables of results were generated using the notebook [case1/results_tables.ipynb].

