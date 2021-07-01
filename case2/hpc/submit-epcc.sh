#!/bin/bash

sbatch -N 1 --ntasks-per-node=4 hpc/e2e-epcc.job
sbatch -N 2 --ntasks-per-node=4 hpc/e2e-epcc.job
sbatch -N 4 --ntasks-per-node=4 hpc/e2e-epcc.job
sbatch -N 8 --ntasks-per-node=4 hpc/e2e-epcc.job

sbatch -N 1 --ntasks-per-node=8 hpc/e2e-epcc.job
sbatch -N 2 --ntasks-per-node=8 hpc/e2e-epcc.job
sbatch -N 4 --ntasks-per-node=8 hpc/e2e-epcc.job
sbatch -N 8 --ntasks-per-node=8 hpc/e2e-epcc.job
