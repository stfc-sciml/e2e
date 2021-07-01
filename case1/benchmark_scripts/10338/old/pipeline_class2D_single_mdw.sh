#!/bin/bash
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --partition=scarf

set -e

#####
# This benchmark implements jobs 025 of the workflow
# which cover 2D classification.
# This was followed by job026 which uses a graphical display to select
# 22 out of 100 2D classes, containing 451k out of 749k particles.
# I don't see an easy way to script this (in real life, you'd always want
# to inspect the classes). 
#####

# Set this environment variable to something unique for each
# run of this benchmark
RELION_BENCHMARK='benchmark7'
#class2D_output=benchmark_scripts/${RELION_BENCHMARK}/Class2D
# use pre-calculated output when testing later steps
class2D_output=Class2D/job025

mkdir -p benchmark_scripts/${RELION_BENCHMARK}

#########################################################
# 025 Class2D
#########################################################

mkdir -p benchmark_scripts/${RELION_BENCHMARK}/Class2D

printf "%s\n%s\n%s\n" "################" " run Class2D " "################"

#time mpirun $RELION_CMD relion_refine_mpi --o benchmark_scripts/${RELION_BENCHMARK}/Class2D/run --i Extract/job024/particles.star --dont_combine_weights_via_disc --pool 3 --pad 2  --ctf  --iter 25 --tau2_fudge 2 --particle_diameter 120 --fast_subsets  --K 100 --flatten_solvent  --zero_mask  --oversampling 1 --psi_step 12 --offset_range 5 --offset_step 2 --norm --scale  --j 6 

if [[ ! -s ${class2D_output}/run_it025_classes.mrcs ]]; then
    echo "relion_refine failed to output stack of 100 2D classes"
    exit 1
fi
read reso reso_flag nclass nclass_flag nr_top <<< $( awk \
    '/_rlnCurrentResolution/ {reso=$2;
                                                  if (reso > 6.0) 
                                                     reso_flag=1
                                                 else
                                                     reso_flag=0 };
     /_rlnNrClasses/ {nclass=$2;
                                                  if (nclass != 100) 
                                                     nclass_flag=1
                                                 else
                                                     nclass_flag=0 };
     /Class2D/ {class_occ[$1]=$2};
     END { {nr_top=0; for (class in class_occ)
              {
	        if ( class_occ[class] > 0.02 ) {
		   top_occ[class] = class_occ[class];
                   nr_top++;
                }
              }
            };
      {print reso}; {print reso_flag}; {print nclass}; {print nclass_flag}; {print nr_top} }' \
   ${class2D_output}/run_it025_model.star )

# replace this with your favourite formatting
printf "%s\n%s\n%s\n" "################" " validate Class2D " "################"
printf "%s %s %s\n" "Current resolution" $reso "(expected 5.0)"
if [[ $reso_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: current resolution worse than expected"
fi
printf "%s %s %s\n" "Number of 3D classes " $nclass " (expected 100)"
if [[ $nclass_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: number of output classes wrong!"
fi
# Previously I selected 22 classes based on visual inspection
printf "%s %s %s\n" "Number of classes with occupancies > 0.02:" $nr_top "(expected 20)" 


