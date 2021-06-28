#!/bin/bash
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --partition=scarf

set -e

#####
# This benchmark implements jobs 039 of the workflow
# which covers 3D classification.
# job041 and job042 involve graphical selection of particles in the top class (so not included here)
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

#time mpirun $RELION_CMD relion_refine_mpi --o benchmark_scripts/${RELION_BENCHMARK}/Class3D/run --i Select/job032/particles.star --ref Import/job033/run_class001_rescaled.mrc --firstiter_cc --ini_high 30 --dont_combine_weights_via_disc --pool 30 --pad 1  --skip_gridding  --ctf --ctf_corrected_ref --iter 25 --tau2_fudge 2 --particle_diameter 120 --fast_subsets  --K 4 --flatten_solvent --zero_mask --strict_highres_exp 7 --solvent_mask MaskCreate/job038/mask.mrc --oversampling 1 --healpix_order 2 --offset_range 5 --offset_step 2 --sym D2 --norm --scale  --j 1 --gpu ""

if [[ ! -s ${class3D_output}/run_class001.mrc ]]; then
    echo "relion_refine failed to output a final reconstruction"
    exit 1
fi
read accRot accRot_flag accTrans accTrans_flag reso reso_flag <<< $( awk '/run_class001/ {accRot=$3; accTrans=$4; reso=$5;
                                                 if (accRot > 1.3) 
                                                     accRot_flag=1
                                                 else
                                                     accRot_flag=0 ;
                                                 if (accTrans > 0.6) 
                                                     accTrans_flag=1
                                                 else
                                                     accTrans_flag=0 ;
                                                 if (reso > 3.7) 
                                                     reso_flag=1
                                                 else
                                                     reso_flag=0 };
     END { {print accRot}; {print accRot_flag}; {print accTrans}; {print accTrans_flag}; {print reso} {print reso_flag}; }' \
   ${class3D_output}/run_model.star )
# replace this with your favourite formatting
printf "%s\n%s\n%s\n" "##########" " Refine3D " "##########"
printf "%s %s %s\n" "Accuracy of rotations" $accRot "(expected 1.125)"
if [[ $accRot_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: rotation accuracy worse than expected"
fi
printf "%s %s %s\n" "Accuracy of translations " $accTrans " (expected 0.427)"
if [[ $accTrans_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: translation accuracy worse than expected"
fi
printf "%s %s %s\n" "Estimated resolution " $reso " (expected 3.50)"
if [[ $reso_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: estimated unmasked resolution worse than expected" 
fi


