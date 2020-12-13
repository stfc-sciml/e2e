#!/bin/bash
#SBATCH --ntasks=XXXmpinodesXXX
#SBATCH --partition=XXXqueueXXX
#SBATCH --cpus-per-task=XXXthreadsXXX
##### --exclusive
#SBATCH --constraint=scarf18
#SBATCH --error=XXXerrfileXXX
#SBATCH --output=XXXoutfileXXX

export PATH=/home/vol08/scarf228/relion/relion/build_act/bin:$PATH

mpirun time XXXcommandXXX
