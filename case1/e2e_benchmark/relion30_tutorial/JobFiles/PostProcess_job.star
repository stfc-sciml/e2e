
# version 30001

data_job

_rlnJobType                            15
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 

# Running options (as tab on Relion GUI) - will need to set these
do_queue        No 
queuename      scarf 
qsub     sbatch 
qsubscript slurm_template.sh 
min_dedicated          1 
other_args         --cpu 

# Relion options (other tabs on Relion GUI) - don't change
adhoc_bfac      -1000 
    angpix      1.244 
autob_lowres         10 
do_adhoc_bfac         No 
do_auto_bfac        Yes 
do_skip_fsc_weighting         No 
     fn_in Refine3D/refine/run_half1_class001_unfil.mrc 
   fn_mask MaskCreate/maskcreate/mask.mrc 
    fn_mtf         "" 
  low_pass          5 
mtf_angpix          1 
 
