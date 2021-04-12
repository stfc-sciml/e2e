#!/bin/bash

sbatch -N 1 -n 1 --gres=gpu:1 hpc/e2e-scarf.job
sbatch -N 1 -n 2 --gres=gpu:2 hpc/e2e-scarf.job
sbatch -N 1 -n 4 --gres=gpu:4 hpc/e2e-scarf.job

sbatch -N 2 -n 8 --gres=gpu:4 hpc/e2e-scarf.job
sbatch -N 4 -n 16 --gres=gpu:4 hpc/e2e-scarf.job
sbatch -N 8 -n 32 --gres=gpu:4 hpc/e2e-scarf.job
