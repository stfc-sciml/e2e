#!/bin/bash
set -e

cd $PROJ_DIR
mkdir -p $OUTPUT_DIR

#########################################################
# Refine3D
#########################################################
mkdir -p $OUTPUT_DIR/Refine3D

time mpirun $RELION_CMD relion_refine_mpi --o $OUTPUT_DIR/Refine3D --auto_refine --split_random_halves --i Select/job042/particles.star --ref Class3D/job039/run_it025_class002.mrc --ini_high 30 --dont_combine_weights_via_disc --pool 30 --pad 1  --skip_gridding  --ctf --ctf_corrected_ref --particle_diameter 120 --flatten_solvent --zero_mask --oversampling 1 --healpix_order 2 --auto_local_healpix_order 4 --offset_range 5 --offset_step 2 --sym D2 --low_resol_join_halves 40 --norm --scale  --j 1 --gpu 


#########################################################
# MaskCreate
#########################################################
mkdir -p ${OUTPUT_DIR}/MaskCreate

time $RELION_CMD relion_mask_create --i Refine3D/job043/run_class001.mrc --o ${OUTPUT_DIR}/MaskCreate/mask.mrc --lowpass 15 --ini_threshold 0.007 --extend_inimask 0 --width_soft_edge 5 --j 1

if [[ ! -e ${OUTPUT_DIR}/MaskCreate/mask.mrc ]]; then
    echo "relion_mask_create failed to output mask"
    exit 1
fi

#########################################################
# Post Process
#########################################################
mkdir -p ${OUTPUT_DIR}/PostProcess

time $RELION_CMD relion_postprocess --mask ${OUTPUT_DIR}/MaskCreate/mask.mrc --i Refine3D/job043/run_half1_class001_unfil.mrc --o ${OUTPUT_DIR}/PostProcess/postprocess  --angpix -1 --mtf mtf_k2_200kV.star --mtf_angpix 0.56 --auto_bfac  --autob_lowres 10

if [[ ! -e ${OUTPUT_DIR}/PostProcess/postprocess.star ]]; then
    echo "relion_ctf_refine failed to output postprocess.star"
    exit 1
fi

#########################################################
# CtfRefine
#########################################################
mkdir -p ${OUTPUT_DIR}/CtfRefine

time mpirun $RELION_CMD relion_ctf_refine_mpi --i ${OUTPUT_DIR}/Refine3D/run_data.star --f ${OUTPUT_DIR}/PostProcess/postprocess.star --o ${OUTPUT_DIR}/CtfRefine/ --fit_defocus --kmin_defocus 30 --fit_mode fpmff --fit_beamtilt --kmin_tilt 30 --j $CPUS_PER_TASK


