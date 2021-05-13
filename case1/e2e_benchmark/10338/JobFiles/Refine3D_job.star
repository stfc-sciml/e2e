
# version 30001

data_job

_rlnJobType                            10
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 

# Running options (as tab on Relion GUI) - will need to set these
nr_mpi           33
nr_threads          2 
do_queue        Yes 
qsub     sbatch 
qsubscript slurm_template.sh 
queuename       nextgenio 
min_dedicated          1 
other_args         "" 

# Compute options (as tab on Relion GUI) - may want to change these
nr_pool         30 
do_parallel_discio        Yes 
do_pad1        Yes 
skip_gridding        Yes 
do_preread_images         No 
scratch_dir         "" 
do_combine_thru_disc         No 
use_gpu        No
gpu_ids         "" 

# Relion options (other tabs on Relion GUI) - don't change
auto_faster         No 
auto_local_sampling "1.8 degrees" 
ctf_corrected_ref        Yes 
ctf_intact_first_peak         No 
do_apply_helical_symmetry        Yes 
do_ctf_correction        Yes 
do_helix         No 
do_local_search_helical_symmetry         No 
do_solvent_fsc         No 
do_zero_mask        Yes 
fn_cont         "" 
fn_img Select/job026/particles.star 
fn_mask         "" 
fn_ref Import/job028/emd_8743_rescaled3.mrc 
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
ini_high         30 
keep_tilt_prior_fixed        Yes 
offset_range          5 
offset_step          1 
particle_diameter        120 
range_psi         10 
range_rot         -1 
range_tilt         15 
ref_correct_greyscale         No 
sampling "7.5 degrees" 
sym_name         D2 
 
