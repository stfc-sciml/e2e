#!/bin/bash

#sbatch --nodes=4 --ntasks=41 hpc/submit_scarf_10338.sh
#sbatch --nodes=8 --ntasks=81 hpc/submit_scarf_10338.sh
#sbatch --nodes=16 --ntasks=161 hpc/submit_scarf_10338.sh

#sbatch --nodes=4 --ntasks=4 hpc/submit_scarf_10338.sh
#sbatch --nodes=8 --ntasks=8 hpc/submit_scarf_10338.sh
#sbatch --nodes=16 --ntasks=16 hpc/submit_scarf_10338.sh

sbatch --nodes=4 --ntasks=41 hpc/submit_scarf_relion_benchmark.sh
sbatch --nodes=8 --ntasks=81 hpc/submit_scarf_relion_benchmark.sh
sbatch --nodes=16 --ntasks=161 hpc/submit_scarf_relion_benchmark.sh
