#####
# This benchmark implements jobs 051 to 056 of the workflow
# which cover 3D refinement with Ctf refined particles (2x sampling), 
# mask creation, postprocessing, re-extract particles at original sampling,
# import re-sampled reference, remove duplicate particles
#####

#########################################################
# 051 Refine3D
# using particles from job050 and 3D reference from job043
#########################################################

mpirun $RELION_CMD relion_refine_mpi --o ${RELION_OUTPUT_DIR}/Refine3D/run --auto_refine --split_random_halves --i CtfRefine/job050/particles_ctf_refine.star --ref Refine3D/job043/run_class001.mrc --ini_high 30 --pad 1  --skip_gridding  --ctf --ctf_corrected_ref --particle_diameter 120 --flatten_solvent --zero_mask --oversampling 1 --healpix_order 2 --auto_local_healpix_order 4 --offset_range 5 --offset_step 2 --sym D2 --low_resol_join_halves 40 --norm --scale  --j $RELION_CPUS_PER_TASK $RELION_OPT_FLAGS

#########################################################
# 052 MaskCreate
# mask based on output 3D model from Refine3D job
#########################################################

$RELION_CMD relion_mask_create --i Refine3D/job051/run_class001.mrc --o ${RELION_OUTPUT_DIR}/MaskCreate/mask.mrc --lowpass 15 --ini_threshold 0.007 --extend_inimask 0 --width_soft_edge 5 --j 1

# No useful metrics in text output. Mask is tested in following PostProcess job.

#########################################################
# 053 Post Process
# based on output 3D model from Refine3D job and mask from MaskCreate job
#########################################################

$RELION_CMD relion_postprocess --mask ${RELION_OUTPUT_DIR}/MaskCreate/mask.mrc --i Refine3D/job051/run_half1_class001_unfil.mrc --o ${RELION_OUTPUT_DIR}/PostProcess/postprocess  --angpix -1 --mtf mtf_k2_200kV.star --mtf_angpix 0.56 --auto_bfac  --autob_lowres 10

#########################################################
# 054 Extract at original sampling
# extract from motion corrected micrographs job009 with refined coordinates
# from Refine3D job
#########################################################

mpirun $RELION_CMD relion_preprocess_mpi --i Select/job009/micrographs.star --reextract_data_star Refine3D/job051/run_data.star --recenter --recenter_x 0 --recenter_y 0 --recenter_z 0 --part_star ${RELION_OUTPUT_DIR}/Extract/particles.star --part_dir ${RELION_OUTPUT_DIR}/Extract/ --extract --extract_size 512 --norm --bg_radius 192 --white_dust -1 --black_dust -1 --invert_contrast

echo Select/job009/micrographs.star > ${RELION_OUTPUT_DIR}/Extract/coords_suffix_extract.star

#########################################################
# 055 Import
# import rescaled reference volume
#########################################################

# Rescaling of reference volume is done manually, so need to include from pre-calculated
# (this step is only really useful in context of a Relion project)

$RELION_CMD relion_import  --do_other --i "Refine3D/job051/run_class001_rescaled.mrc" --odir ${RELION_OUTPUT_DIR}/Import/ --ofile run_class001_rescaled.mrc

#########################################################
# 056 Select
# filter the particles from the Extract job to remove duplicates
#########################################################

$RELION_CMD relion_star_handler --i ${RELION_OUTPUT_DIR}/Extract/particles.star --o ${RELION_OUTPUT_DIR}/Select/particles.star --remove_duplicates 30 --image_angpix 0.56
