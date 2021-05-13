#!/bin/bash

# These are populated by Relion. 
# You may need to add other platform-specific lines.
#SBATCH --ntasks=XXXmpinodesXXX
#SBATCH --partition=XXXqueueXXX
#SBATCH --cpus-per-task=XXXthreadsXXX
#SBATCH --error=XXXerrfileXXX
#SBATCH --output=XXXoutfileXXX

# Add in any necessary environment.
export PATH=/home/vol08/scarf228/relion/relion/build_act/bin:$PATH
export LD_LIBRARY_PATH=/home/vol08/scarf228/relion/relion/build_act/lib:$LD_LIBRARY_PATH

# Relion supplies the appropriate command.
mpirun time XXXcommandXXX
