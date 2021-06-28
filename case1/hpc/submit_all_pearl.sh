#!/bin/bash

#sbatch --gres=gpu:1 --ntasks=3 hpc/submit_pearl_10338.sh
#sbatch --gres=gpu:2 --ntasks=5 hpc/submit_pearl_10338.sh
#sbatch --gres=gpu:4 --ntasks=11 hpc/submit_pearl_10338.sh
#sbatch --gres=gpu:8 --ntasks=21 hpc/submit_pearl_10338.sh
#sbatch --gres=gpu:16 --ntasks=41 hpc/submit_pearl_10338.sh


sbatch --gres=gpu:1 --ntasks=3 --mem=200G hpc/submit_pearl_relion_benchmark.sh
sbatch --gres=gpu:2 --ntasks=5 --mem=200G hpc/submit_pearl_relion_benchmark.sh
sbatch --gres=gpu:4 --ntasks=11 --mem=200G hpc/submit_pearl_relion_benchmark.sh
sbatch --gres=gpu:8 --ntasks=21 --mem=200G hpc/submit_pearl_relion_benchmark.sh
sbatch --gres=gpu:16 --ntasks=41 --mem=200G hpc/submit_pearl_relion_benchmark.sh
