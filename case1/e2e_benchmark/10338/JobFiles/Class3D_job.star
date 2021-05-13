
# version 30001

data_job

_rlnJobType                             9
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 

# Running options (as tab on Relion GUI) - will need to set these
nr_mpi          9 
nr_threads          2 
do_queue        Yes 
queuename      nextgenio
qsub     sbatch 
qsubscript slurm_template.sh 
min_dedicated          1 
other_args       "--cpu" 
#
# # Compute options (as tab on Relion GUI) - may want to change these
do_parallel_discio        Yes 
nr_pool         30 
do_pad1         Yes
skip_gridding        Yes 
do_preread_images     No
scratch_dir         "" 
do_combine_thru_disc         No 
use_gpu         No 
gpu_ids         "" 
#
# # Relion options (other tabs on Relion GUI) - don't change
allow_coarser         No 
ctf_corrected_ref        Yes 
ctf_intact_first_peak         No 
do_apply_helical_symmetry        Yes 
do_ctf_correction        Yes 
do_fast_subsets        Yes 
do_helix         No 
do_local_ang_searches         No 
do_local_search_helical_symmetry         No 
do_zero_mask        Yes 
dont_skip_align        Yes 
fn_cont         "" 
fn_img Select/job032/particles.star 
fn_mask MaskCreate/job038/mask.mrc 
fn_ref Import/job033/run_class001_rescaled.mrc 
helical_nr_asu          1 
helical_range_distance         -1 
helical_rise_inistep          0 
helical_rise_initial          0 
helical_rise_max          0 
helical_rise_min          0 
helical_tube_inner_diameter         -1 
helical_tube_outer_diameter         -1 
helical_twist_inistep          0 
helical_twist_initial          0 
helical_twist_max          0 
helical_twist_min          0 
helical_z_percentage         30 
highres_limit          7 
ini_high         30 
keep_tilt_prior_fixed        Yes 
nr_classes          4 
nr_iter         25 
offset_range          5 
offset_step          1 
particle_diameter        120 
range_psi         10 
range_rot         -1 
range_tilt         15 
ref_correct_greyscale         No 
sampling "7.5 degrees" 
sigma_angles          5 
sym_name         D2 
tau_fudge          2 
 
