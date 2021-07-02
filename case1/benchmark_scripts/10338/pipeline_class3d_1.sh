#!/bin/bash

#####
# This benchmark implements jobs 039 and job042  of the workflow
# which cover 3D classification and selection of particles in the top class.
# The 3D reconstruction from job 039 and the particle list from job 042 form the
# input for the next Refine3D job.
# job040 and job041 were concerned with graphical selection of particles, which
# we don't do here.
#####

#########################################################
# 039 Class3D
#########################################################

mpirun $RELION_MPI_FLAGS $RELION_CMD relion_refine_mpi --o ${RELION_OUTPUT_DIR}/Class3D/run --i Select/job032/particles.star --ref Import/job033/run_class001_rescaled.mrc --firstiter_cc --ini_high 30  --pad 1  --skip_gridding  --ctf --ctf_corrected_ref --iter 25 --tau2_fudge 2 --particle_diameter 120 --fast_subsets  --K 4 --flatten_solvent --zero_mask --strict_highres_exp 7 --solvent_mask MaskCreate/job038/mask.mrc --oversampling 1 --healpix_order 2 --offset_range 5 --offset_step 2 --sym D2 --norm --scale $RELION_OPT_FLAGS --j $RELION_CPUS_PER_TASK 

#########################################################
# 042 Select
#########################################################

$RELION_CMD relion_star_handler --i Class3D/job039/run_it025_data.star --o ${RELION_OUTPUT_DIR}/Select/particles.star --select rlnClassNumber --minval 2 --maxval 2

