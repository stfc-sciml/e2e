#####
# This benchmark implements jobs 057 to 059, 061, 068 of the workflow
# which cover 3D refinement with fully sampled particles (hence longer job), 
# mask creation, postprocessing, and polishing (training and applying).
# Note that jobs 060, 062 were failed jobs, and 063-067 were additional
# benchmarking jobs and so not included in the main workflow.
#####


#########################################################
# 057 Refine3D
# using re-extracted particles from job056 and re-sampled 3D reference from job055
#########################################################


mpirun $RELION_CMD relion_refine_mpi --o ${RELION_OUTPUT_DIR}/Refine3D/run  -auto_refine --split_random_halves --i Select/job056/particles.star --ref Import/job055/run_class001_rescaled.mrc --firstiter_cc --ini_high 30 --pad 1  --skip_gridding  --ctf --ctf_corrected_ref --particle_diameter 120 --flatten_solvent --zero_mask --oversampling 1 --healpix_order 2 --auto_local_healpix_order 4 --offset_range 5 --offset_step 2 --sym D2 --low_resol_join_halves 40 --norm --scale  --j $RELION_CPUS_PER_TASK $RELION_OPT_FLAGS

#########################################################
# 058 MaskCreate
# mask based on output 3D model from Refine3D job
#########################################################

$RELION_CMD relion_mask_create --i Refine3D/job057/run_class001.mrc --o ${RELION_OUTPUT_DIR}/MaskCreate/mask.mrc --lowpass 15 --ini_threshold 0.007 --extend_inimask 0 --width_soft_edge 5 --j 1

# No useful metrics in text output. Mask is tested in following PostProcess job.

#########################################################
# 059 Post Process
# based on output 3D model from Refine3D job and mask from MaskCreate job
#########################################################

$RELION_CMD relion_postprocess --mask ${RELION_OUTPUT_DIR}/MaskCreate/mask.mrc --i Refine3D/job057/run_half1_class001_unfil.mrc --o ${RELION_OUTPUT_DIR}/PostProcess/postprocess  --angpix -1 --mtf benchmark_scripts/mtf_k2_200kV.star --mtf_angpix 0.56 --auto_bfac  --autob_lowres 10


#########################################################
# 061 Polish (training)
# polish particles taken from Refine3D job, using movie frames from
# job 005, and other filenames taken from PostProcess output
#########################################################

mpirun $RELION_CMD relion_motion_refine_mpi --i Refine3D/job057/run_data.star --f ${RELION_OUTPUT_DIR}/PostProcess/postprocess.star --corr_mic MotionCorr/job005/corrected_micrographs.star --first_frame 1 --last_frame -1 --o ${RELION_OUTPUT_DIR}/Polish_t/ --min_p 10000 --eval_frac 0.5 --align_frac 0.5 --params3  --j $RELION_CPUS_PER_TASK

#########################################################
# 068 Polish (apply)
# polish particles taken from Refine3D job, using movie frames from
# job 005, and other filenames taken from PostProcess output
#########################################################

mpirun $RELION_CMD relion_motion_refine_mpi --i Refine3D/job057/run_data.star --f ${RELION_OUTPUT_DIR}/PostProcess/postprocess.star --corr_mic MotionCorr/job005/corrected_micrographs.star --first_frame 1 --last_frame -1 --o ${RELION_OUTPUT_DIR}/Polish/ --params_file ${RELION_OUTPUT_DIR}/Polish_t/opt_params_all_groups.txt --combine_frames --bfac_minfreq 20 --bfac_maxfreq -1 --j $RELION_CPUS_PER_TASK

# No easy metric to check. You are supposed to inspect the output graphs showing the
# particle drift. 
