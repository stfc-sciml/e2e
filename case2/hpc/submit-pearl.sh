#!/bin/bash

sbatch --gres=gpu:1 -n 1 hpc/e2e-pearl.job  
sbatch --gres=gpu:2 -n 2 hpc/e2e-pearl.job  
sbatch --gres=gpu:4 -n 4 hpc/e2e-pearl.job  
sbatch --gres=gpu:8 -n 8 hpc/e2e-pearl.job  
sbatch --gres=gpu:16 -n 16 hpc/e2e-pearl.job  
