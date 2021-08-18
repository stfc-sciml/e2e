#####
# This benchmark implements jobs 057 to 059 of the workflow
# which cover 3D refinement with fully sampled particles (hence longer job), 
# mask creation, and postprocessing.
# Note that jobs 060, 062 were failed jobs and so not included in the main workflow.
#####


#########################################################
# 057 Refine3D
# using re-extracted particles from job056 and re-sampled 3D reference from job055
#########################################################


mpirun $RELION_MPI_FLAGS $RELION_CMD relion_refine_mpi --o ${RELION_OUTPUT_DIR}/Refine3D/run  -auto_refine --split_random_halves --i Select/job056/particles.star --ref Import/job055/run_class001_rescaled.mrc --firstiter_cc --ini_high 30 --pad 1  --skip_gridding  --ctf --ctf_corrected_ref --particle_diameter 120 --flatten_solvent --zero_mask --oversampling 1 --healpix_order 2 --auto_local_healpix_order 4 --offset_range 5 --offset_step 2 --sym D2 --low_resol_join_halves 40 --norm --scale  $RELION_OPT_FLAGS

#########################################################
# 058 MaskCreate
# mask based on output 3D model from Refine3D job
#########################################################

$RELION_CMD relion_mask_create --i Refine3D/job057/run_class001.mrc --o ${RELION_OUTPUT_DIR}/MaskCreate/mask.mrc --lowpass 15 --ini_threshold 0.001 --extend_inimask 0 --width_soft_edge 8 --j 1

# No useful metrics in text output. Mask is tested in following PostProcess job.

#########################################################
# 059 Post Process
# based on output 3D model from Refine3D job and mask from MaskCreate job
#########################################################

$RELION_CMD relion_postprocess --mask ${RELION_OUTPUT_DIR}/MaskCreate/mask.mrc --i Refine3D/job057/run_half1_class001_unfil.mrc --o ${RELION_OUTPUT_DIR}/PostProcess/postprocess --angpix -1 --mtf benchmark_scripts/mtf_k2_200kV.star --mtf_angpix 0.56 --auto_bfac  --autob_lowres 10


