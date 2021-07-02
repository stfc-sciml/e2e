#####
# This benchmark implements jobs 061 and 068 of the workflow
# which cover polishing (training and applying).
# Note that 063-067 were additional benchmarking jobs and so 
# not included in the main workflow.
#####

#########################################################
# 061 Polish (training)
# polish particles taken from Refine3D job, using movie frames from
# job 005, and other filenames taken from PostProcess output
#########################################################

$RELION_CMD relion_motion_refine --i Refine3D/job057/run_data.star --f PostProcess/job059/postprocess.star --corr_mic MotionCorr/job005/corrected_micrographs.star --first_frame 1 --last_frame -1 --o ${RELION_OUTPUT_DIR}/Polish_t/ --min_p 10000 --eval_frac 0.5 --align_frac 0.5 --params3  --j $RELION_CPUS_PER_TASK

#########################################################
# 068 Polish (apply)# polish particles taken from Refine3D job, using movie frames from
# polish particles taken from Refine3D job, using movie frames from
# job 005, and other filenames taken from PostProcess output
#########################################################

mpirun $RELION_MPI_FLAGS $RELION_CMD relion_motion_refine_mpi --i Refine3D/job057/run_data.star --f PostProcess/job059/postprocess.star --corr_mic MotionCorr/job005/corrected_micrographs.star --first_frame 1 --last_frame -1 --o ${RELION_OUTPUT_DIR}/Polish/ --params_file ${RELION_OUTPUT_DIR}/Polish_t/opt_params_all_groups.txt --combine_frames --bfac_minfreq 20 --bfac_maxfreq -1 --j $RELION_CPUS_PER_TASK

# No easy metric to check. You are supposed to inspect the output graphs showing the
# particle drift. 
