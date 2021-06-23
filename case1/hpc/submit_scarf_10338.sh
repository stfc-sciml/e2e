#!/bin/bash
#SBATCH -p gpu
#SBATCH --ntasks=3
#SBATCH --cpus-per-task=2
#SBATCH --nodes=1
#SBATCH --gres=gpu:2

# Load modules
module load OpenMPI/4.1.0-iccifort-2018.3.222-GCC-7.3.0-2.30

# Set environment variables for this machine

#Location of the case1 folder
export BASE_DIR="/home/vol08/scarf688/git/intel-e2e-benchmark/case1"
# Location of the relion singularity image
export RELION_IMG="$BASE_DIR/relion.sif"
# Relion project directory data
export PROJ_DIR="/work3/cse/scarf228/intel-benchmark/10338"
# Location to store output files
export OUTPUT_DIR="$BASE_DIR/runs/scarf/job_$SLURM_JOB_ID"
# Relion command
export RELION_CMD="singularity run --nv -B $BASE_DIR -H $PROJ_DIR $RELION_IMG"
# Number of cpus to use with -j option
export CPUS_PER_TASK=$SLURM_CPUS_PER_TASK

# Run pipeline
./benchmark_scripts/pipeline_2nd_refine3D_single.sh
