#!/bin/bash
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --partition=scarf

set -e

#####
# This benchmark implements jobs 039 and job042  of the workflow
# which cover 3D classification and selection of particles in the top class.
# The 3D reconstruction from job 039 and the particle list from job 042 form the
# input for the next Refine3D job.
# job040 and job041 were concerned with graphical selection of particles, which
# we don't do here.
#####

# Set this environment variable to something unique for each
# run of this benchmark
RELION_BENCHMARK='benchmark6'
#class3D_output=benchmark_scripts/${RELION_BENCHMARK}/Class3D
# use pre-calculated output when testing later steps
class3D_output=Class3D/job039

mkdir -p benchmark_scripts/${RELION_BENCHMARK}

#########################################################
# 039 Class3D
#########################################################

mkdir -p benchmark_scripts/${RELION_BENCHMARK}/Class3D

printf "%s\n%s\n%s\n" "################" " run Class3D " "################"

#time mpirun $RELION_CMD relion_refine_mpi --o benchmark_scripts/${RELION_BENCHMARK}/Class3D/run --i Select/job032/particles.star --ref Import/job033/run_class001_rescaled.mrc --firstiter_cc --ini_high 30 --dont_combine_weights_via_disc --pool 30 --pad 1  --skip_gridding  --ctf --ctf_corrected_ref --iter 25 --tau2_fudge 2 --particle_diameter 120 --fast_subsets  --K 4 --flatten_solvent --zero_mask --strict_highres_exp 7 --solvent_mask MaskCreate/job038/mask.mrc --oversampling 1 --healpix_order 2 --offset_range 5 --offset_step 2 --sym D2 --norm --scale  --j 1 --gpu ""

if [[ ! -s ${class3D_output}/run_it025_class004.mrc ]]; then
    echo "relion_refine failed to output four 3D classes"
    exit 1
fi
read reso reso_flag nclass nclass_flag class1_occ class2_occ class3_occ class4_occ <<< $( awk \
    '/_rlnCurrentResolution/ {reso=$2;
                                                  if (reso > 6.0) 
                                                     reso_flag=1
                                                 else
                                                     reso_flag=0 };
     /_rlnNrClasses/ {nclass=$2;
                                                  if (nclass != 4) 
                                                     nclass_flag=1
                                                 else
                                                     nclass_flag=0 };
     /run_it025_class001/ {class1_occ=$2};
     /run_it025_class002/ {class2_occ=$2};
     /run_it025_class003/ {class3_occ=$2};
     /run_it025_class004/ {class4_occ=$2};
     END { {print reso}; {print reso_flag}; {print nclass}; {print nclass_flag}; {print class1_occ} {print class2_occ}; {print class3_occ} {print class4_occ} }' \
   ${class3D_output}/run_it025_model.star )
# replace this with your favourite formatting
printf "%s\n%s\n%s\n" "################" " validate Class3D " "################"
printf "%s %s %s\n" "Current resolution" $reso "(expected 5.2)"
if [[ $reso_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: current resolution worse than expected"
fi
printf "%s %s %s\n" "Number of 3D classes " $nclass " (expected 4)"
if [[ $nclass_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: number of output classes wrong!"
fi
printf "%s %s %s %s %s\n" "Class distribution: " $class1_occ  $class2_occ $class3_occ $class4_occ 
printf "%s\n" " (expected 2nd class to be largest with fraction 0.49 of particles)"


#########################################################
# 042 Select
#########################################################

mkdir -p benchmark_scripts/${RELION_BENCHMARK}/Select

printf "%s\n%s\n%s\n" "################" " run Select " "################"

# This was the top class before but might change!
top_class=2

#time `which relion_star_handler` --i ${class3D_output}/run_it025_data.star --o benchmark_scripts/${RELION_BENCHMARK}/Select/particles.star --select rlnClassNumber --minval ${top_class} --maxval ${top_class}

if [[ ! -s benchmark_scripts/${RELION_BENCHMARK}/Select/particles.star ]]; then
    echo "relion_star_handler failed to output particles.star"
    exit 1
fi

printf "%s %s %s\n" "Size of particle file" `wc -l benchmark_scripts/${RELION_BENCHMARK}/Select/particles.star | cut -d " " -f 1` "should be around 219k lines."

# Can also check for output:
# "Written: benchmark_scripts/benchmark6/Select/particles.star with 219012 item(s)"
# The number of particles selected for the top class would be a good check, 
# but it is only written to stdout so I can't script it. 
