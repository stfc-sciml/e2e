#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --exclusive
#SBATCH --time 4-0

# Set environment variables for this machine
module load compiler/2021.1.1
module load mpi/2021.1.1 mkl/2021.1.1
module load tiff/4.0.10

#Location of the case1 folder
export BASE_DIR="/home/nx07/nx07/sljack92/intel-e2e-benchmark/case1"
# Relion project directory data
export RELION_PROJ_DIR="/home/nx07/nx07/sljack92/relion/10338"
# Location to store output files
export RELION_OUTPUT_DIR="$BASE_DIR/runs/icx/job_$RELION_SCRIPT_NAME"
# Relion command
export PATH="/home/nx07/nx07/sljack92/relion/relion-3.1.2/build/bin:$PATH"
export RELION_CMD=""
# Number of cpus to use
export RELION_NUM_CPUS=${SLURM_NTASKS:-23}
# Number of cpu threads to use with --j option
export RELION_CPU_THREADS_PER_TASK=4
# Additional optimization flags
export RELION_OPT_FLAGS="--dont_combine_weights_via_disc --pool $RELION_NUM_CPUS --cpu --j $RELION_CPU_THREADS_PER_TASK"
# Additional MPI flags
export RELION_MPI_FLAGS="-n $RELION_NUM_CPUS"


# Run pipeline
./benchmark_scripts/benchmark_relion.py $RELION_SCRIPT_NAME
