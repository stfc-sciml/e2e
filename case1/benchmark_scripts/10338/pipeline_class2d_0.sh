#!/bin/bash

#####
# This benchmark implements jobs 025 of the workflow
# which cover 2D classification.
# This was followed by job026 which uses a graphical display to select
# 22 out of 100 2D classes, containing 451k out of 749k particles.
#####

#########################################################
# 025 Class2D
#########################################################

mpirun $RELION_MPI_FLAGS $RELION_CMD relion_refine_mpi --o ${RELION_OUTPUT_DIR}/Class2D/run --i Extract/job024/particles.star --pad 2  --ctf  --iter 25 --tau2_fudge 2 --particle_diameter 120 --fast_subsets  --K 100 --flatten_solvent  --zero_mask  --oversampling 1 --psi_step 12 --offset_range 5 --offset_step 2 --norm --scale  --j $RELION_CPUS_PER_TASK $RELION_OPT_FLAGS

