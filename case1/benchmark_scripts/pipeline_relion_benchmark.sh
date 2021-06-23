#!/bin/bash

# Running standard benchmarks from the Plasmodium ribosome data
# https://www3.mrc-lmb.cam.ac.uk/relion/index.php?title=Benchmarks_%26_computer_hardware#Standard_benchmarks

set -e

cd $PROJ_DIR
mkdir -p ${OUTPUT_DIR}

#########################################################
# 2D Classification
#########################################################

mkdir -p ${OUTPUT_DIR}/class2d

time mpirun $RELION_CMD relion_refine_mpi --i Particles/shiny_2sets.star --ctf --iter 25 --tau2_fudge 2 --particle_diameter 360 --K 200 --zero_mask --oversampling 1 --psi_step 6 --offset_range 5 --offset_step 2 --norm --scale --random_seed 0 --o ${OUTPUT_DIR}/class2d -j $CPUS_PER_TASK --gpu

#########################################################
# 3D Classification
#########################################################

mkdir -p ${OUTPUT_DIR}/class3d

time mpirun $RELION_CMD relion_refine_mpi --i Particles/shiny_2sets.star --ref emd_2660.map:mrc --firstiter_cc --ini_high 60 --ctf --ctf_corrected_ref --iter 25 --tau2_fudge 4 --particle_diameter 360 --K 6 --flatten_solvent --zero_mask --oversampling 1 --healpix_order 2 --offset_range 5 --offset_step 2 --sym C1 --norm --scale --random_seed 0 --o ${OUTPUT_DIR}/class3d -j $CPUS_PER_TASK --gpu

