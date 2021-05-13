
# version 30001

data_job

_rlnJobType                             4
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 

# Running options (as tab on Relion GUI) - will need to set these
nr_mpi          4 
do_queue        Yes 
queuename      scarf 
qsub     sbatch 
qsubscript slurm_template.sh 
min_dedicated          1 
other_args         --cpu 

# Compute options (autopicking tab on Relion GUI) - may want to change these
use_gpu         No 
gpu_ids         "" 

# Relion options (other tabs on Relion GUI) - don't change
angpix         -1 
angpix_ref       3.54 
do_amyloid         No 
do_ctf_autopick        Yes 
do_ignore_first_ctfpeak_autopick         No 
do_invert_refs        Yes 
do_log         No 
do_pick_helical_segments         No 
do_read_fom_maps         No 
do_ref3d         No 
do_write_fom_maps         No 
fn_input_autopick MotionCorr/job006/corrected_micrographs.star 
fn_ref3d_autopick         "" 
fn_refs_autopick Select/job013/class_averages.star 
helical_nr_asu          1 
helical_rise         -1 
helical_tube_kappa_max        0.1 
helical_tube_length_min         -1 
helical_tube_outer_diameter        200 
highpass         -1 
log_adjust_thr          0 
log_diam_max        180 
log_diam_min        150 
log_invert         No 
log_maxres         20 
log_upper_thr          5 
lowpass         20 
maxstddevnoise_autopick         -1 
minavgnoise_autopick       -999 
mindist_autopick        100 
particle_diameter         -1 
psi_sampling_autopick          5 
ref3d_sampling "30 degrees" 
ref3d_symmetry         C1 
shrink          0 
threshold_autopick        0.0 
 
