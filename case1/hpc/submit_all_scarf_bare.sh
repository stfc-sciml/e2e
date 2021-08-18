#!/bin/bash

JOB_SCRIPT=hpc/submit_scarf_10338_bare.sh

# Each node has 24 cores. We need an odd number of tasks, so we use 23 here.
sbatch --nodes=1 --ntasks=23 RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_class2d_0.sh $JOB_SCRIPT
sbatch --nodes=1 --ntasks=23 RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_class3d_1.sh $JOB_SCRIPT
sbatch --nodes=1 --ntasks=23 RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_refine3d_2.sh $JOB_SCRIPT
sbatch --nodes=1 --ntasks=23 RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_refine3d_3.sh $JOB_SCRIPT
sbatch --nodes=1 --ntasks=23 RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_refine3d_4.sh $JOB_SCRIPT
sbatch --nodes=1 --ntasks=23 RELION_SCRIPT_NAME=./benchmark_scripts/10338/pipeline_polish_5.sh $JOB_SCRIPT
