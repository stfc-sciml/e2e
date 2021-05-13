
# version 30001

data_job

_rlnJobType                            12
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 

# Running options (as tab on Relion GUI) - will need to set these
nr_threads          4 
do_queue        No 
queuename      scarf 
qsub     sbatch 
qsubscript slurm_template.sh 
min_dedicated          1 
other_args         --cpu 

# Relion options (other tabs on Relion GUI) - don't change
    angpix         -1 
  do_helix         No 
extend_inimask          0 
fn_in Refine3D/refine/run_class001.mrc 
helical_z_percentage         30 
inimask_threshold      0.005 
lowpass_filter         15 
width_mask_edge          6 
 
