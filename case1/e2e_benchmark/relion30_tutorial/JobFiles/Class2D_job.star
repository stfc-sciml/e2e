
# version 30001

data_job

_rlnJobType                             8
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 

# Running options (as tab on Relion GUI) - will need to set these
nr_mpi          5 
nr_threads          8 
do_queue        Yes 
queuename      scarf 
qsub     sbatch 
qsubscript slurm_template.sh 
min_dedicated          1 
other_args         --cpu 

# Compute options (as tab on Relion GUI) - may want to change these
do_parallel_discio        Yes 
nr_pool         30 
do_preread_images        Yes 
scratch_dir         "" 
do_combine_thru_disc         No 
use_gpu         No 
gpu_ids         "" 

# Relion options (other tabs on Relion GUI) - don't change
allow_coarser         No 
ctf_intact_first_peak         No 
do_bimodal_psi        Yes 
do_ctf_correction        Yes 
do_fast_subsets         No 
do_helix         No 
do_restrict_xoff        Yes 
do_zero_mask        Yes 
dont_skip_align        Yes 
fn_cont         "" 
fn_img Extract/job021/particles.star 
helical_rise       4.75 
helical_tube_outer_diameter        200 
highres_limit         -1 
nr_classes        100 
nr_iter         25 
offset_range          5 
offset_step          1 
particle_diameter        200 
psi_sampling          6 
range_psi          6 
tau_fudge          2 
 
