#!/bin/bash

JOB_SCRIPT=hpc/submit_clx_10338_bare.sh

# Each node has 24 cores. We need an odd number of tasks, so we use 23 here.
RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_class2d_0.sh sbatch --nodes=1 --ntasks=23  $JOB_SCRIPT
RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_class3d_1.sh sbatch --nodes=1 --ntasks=23  $JOB_SCRIPT
RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_refine3d_2.sh sbatch --nodes=1 --ntasks=23  $JOB_SCRIPT
RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_refine3d_3.sh sbatch --nodes=1 --ntasks=23  $JOB_SCRIPT
RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_refine3d_4.sh sbatch --nodes=1 --ntasks=23  $JOB_SCRIPT
RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_polish_5.sh sbatch --nodes=1 --ntasks=23  $JOB_SCRIPT
