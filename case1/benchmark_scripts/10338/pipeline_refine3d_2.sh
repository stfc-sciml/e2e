#!/bin/bash
# Refine 3D Pipeline for the EMPIAR-10338 Rabbit muscle aldolase dataset
# https://www.ebi.ac.uk/pdbe/emdb/empiar/entry/10338/

#########################################################
# This benchmark implements jobs 043, 048, 049, 050 of the workflow
# which cover 3D refinement of the top 3D class (2x sampling), mask creation,
# postprocessing, and per-particle Ctf refinement (defocus and global
# astigmatism) and beam tilt estimation.
# Note that jobs 044-047 were failed attempts at postprocessing, and
# are ignored.
#########################################################

#########################################################
# 043 Refine3D
# using particles from job042 and 3D reference from job039
#########################################################
mpirun $RELION_MPI_FLAGS $RELION_CMD relion_refine_mpi --o $RELION_OUTPUT_DIR/Refine3D/run --auto_refine --split_random_halves --i Select/job042/particles.star --ref Class3D/job039/run_it025_class002.mrc --ini_high 30 --pad 1  --skip_gridding  --ctf --ctf_corrected_ref --particle_diameter 120 --flatten_solvent --zero_mask --oversampling 1 --healpix_order 2 --auto_local_healpix_order 4 --offset_range 5 --offset_step 2 --sym D2 --low_resol_join_halves 40 --norm --scale $RELION_OPT_FLAGS 

#########################################################
# 048 MaskCreate
# mask based on output 3D model from Refine3D job
#########################################################
$RELION_CMD relion_mask_create --i Refine3D/job043/run_class001.mrc --o ${RELION_OUTPUT_DIR}/MaskCreate/mask.mrc --lowpass 15 --ini_threshold 0.007 --extend_inimask 0 --width_soft_edge 5 --j 1

#########################################################
# 049 Post Process
# based on output 3D model from Refine3D job and mask from MaskCreate job
#########################################################
$RELION_CMD relion_postprocess --mask ${RELION_OUTPUT_DIR}/MaskCreate/mask.mrc --i Refine3D/job043/run_half1_class001_unfil.mrc --o ${RELION_OUTPUT_DIR}/PostProcess/postprocess  --angpix -1 --mtf mtf_k2_200kV.star --mtf_angpix 0.56 --auto_bfac  --autob_lowres 10

#########################################################
# 050 CtfRefine
# corrections for particles taken from Refine3D job, other filenames taken
# from PostProcess output
#########################################################
mpirun $RELION_MPI_FLAGS $RELION_CMD relion_ctf_refine_mpi --i ${RELION_OUTPUT_DIR}/Refine3D/run_data.star --f ${RELION_OUTPUT_DIR}/PostProcess/postprocess.star --o ${RELION_OUTPUT_DIR}/CtfRefine/ --fit_defocus --kmin_defocus 30 --fit_mode fpmff --fit_beamtilt --kmin_tilt 30 --j $RELION_CPU_THREADS_PER_TASK
