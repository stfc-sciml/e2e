#!/bin/bash
#SBATCH --ntasks=3
#SBATCH --cpus-per-task=12
#SBATCH --nodes=3
#SBATCH --partition=scarf

set -e

#####
# This benchmark implements jobs 057 to 059, 061, 068 of the workflow
# which cover 3D refinement with fully sampled particles (hence longer job), 
# mask creation, postprocessing, and polishing (training and applying).
# Note that jobs 060, 062 were failed jobs, and 063-067 were additional
# benchmarking jobs and so not included in the main workflow.
#####

# Set this environment variable to something unique for each
# run of this benchmark
RELION_BENCHMARK='benchmark5'
#refine3D_output=benchmark_scripts/${RELION_BENCHMARK}/Refine3D
# use pre-calculated output when testing later steps
refine3D_output=Refine3D/job057

mkdir -p benchmark_scripts/${RELION_BENCHMARK}

#########################################################
# 057 Refine3D
# using re-extracted particles from job056 and re-sampled 3D reference from job055
#########################################################

mkdir -p benchmark_scripts/${RELION_BENCHMARK}/Refine3D

printf "%s\n%s\n%s\n" "################" " run Refine3D " "################"

#time mpirun $RELION_CMD relion_refine_mpi --o benchmark_scripts/${RELION_BENCHMARK}/Refine3D/run  -auto_refine --split_random_halves --i Select/job056/particles.star --ref Import/job055/run_class001_rescaled.mrc --firstiter_cc --ini_high 30 --dont_combine_weights_via_disc --pool 30 --pad 1  --skip_gridding  --ctf --ctf_corrected_ref --particle_diameter 120 --flatten_solvent --zero_mask --oversampling 1 --healpix_order 2 --auto_local_healpix_order 4 --offset_range 5 --offset_step 2 --sym D2 --low_resol_join_halves 40 --norm --scale  --j 1 --gpu ""

if [[ ! -s ${refine3D_output}/run_class001.mrc ]]; then
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
   ${refine3D_output}/run_model.star )
# replace this with your favourite formatting
printf "%s\n%s\n%s\n" "###################" " validate Refine3D " "###################"
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


#########################################################
# 058 MaskCreate
# mask based on output 3D model from Refine3D job
#########################################################
mkdir -p benchmark_scripts/${RELION_BENCHMARK}/MaskCreate

printf "%s\n%s\n%s\n" "################" " run MaskCreate " "################"

#time `which relion_mask_create` --i ${refine3D_output}/run_class001.mrc --o benchmark_scripts/${RELION_BENCHMARK}/MaskCreate/mask.mrc --lowpass 15 --ini_threshold 0.007 --extend_inimask 0 --width_soft_edge 5 --j 1

if [[ ! -s benchmark_scripts/${RELION_BENCHMARK}/MaskCreate/mask.mrc ]]; then
    echo "relion_mask_create failed to output mask"
    exit 1
fi
# No useful metrics in text output. Mask is tested in following PostProcess job.

#########################################################
# 059 Post Process
# based on output 3D model from Refine3D job and mask from MaskCreate job
#########################################################
mkdir -p benchmark_scripts/${RELION_BENCHMARK}/PostProcess

printf "%s\n%s\n%s\n" "################" " run PostProcess " "################"

#time `which relion_postprocess` --mask benchmark_scripts/${RELION_BENCHMARK}/MaskCreate/mask.mrc --i ${refine3D_output}/run_half1_class001_unfil.mrc --o benchmark_scripts/${RELION_BENCHMARK}/PostProcess/postprocess  --angpix -1 --mtf benchmark_scripts/mtf_k2_200kV.star --mtf_angpix 0.56 --auto_bfac  --autob_lowres 10

if [[ ! -s benchmark_scripts/${RELION_BENCHMARK}/PostProcess/postprocess.star ]]; then
    echo "relion_ctf_refine failed to output postprocess.star"
    exit 1
fi
read reso res_flag bfac bfac_flag solv solv_flag <<< $( awk '/_rlnFinalResolution/ {reso=$2;
                                                 if (reso > 3.2) 
                                                     res_flag=1
                                                 else
                                                     res_flag=0 };
     /_rlnBfactorUsedForSharpening/ {bfac=$2;
                                                 if (bfac > -100 || bfac < -130) 
                                                     bfac_flag=1
                                                 else
                                                     bfac_flag=0 };
     /_rlnParticleBoxFractionSolventMask/ {solv = $2;
                                                 if (solv > 40 || solv < 30) 
                                                     solv_flag=1
                                                 else
                                                     solv_flag=0 };
     END { {print reso}; {print res_flag}; {print bfac}; {print bfac_flag}; {print solv} {print solv_flag}; }' \
   benchmark_scripts/${RELION_BENCHMARK}/PostProcess/postprocess.star )

# replace this with your favourite formatting
printf "%s\n%s\n%s\n" "######################" " validate PostProcess " "######################"
printf "%s %s %s\n" "Estimated resolution" $reso "(expected 3.19)"
if [[ $res_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: resolution worse than expected!"
fi
printf "%s %s %s\n" "B factor sharpening " $bfac " (expected -129)"
if [[ $bfac_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: change in B factor, check Guinier plot in logfile.pdf"
fi
printf "%s %s %s\n" "Percent solvent " $solv " (expected 34.2)"
if [[ $solv_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: change in solvent content, check mask" 
fi

#########################################################
# 061 Polish (training)
# polish particles taken from Refine3D job, using movie frames from
# job 005, and other filenames taken from PostProcess output
#########################################################
mkdir -p benchmark_scripts/${RELION_BENCHMARK}/Polish_t

printf "%s\n%s\n%s\n" "################" " run Polish (training) " "################"

#time mpirun `which relion_motion_refine_mpi` --i ${refine3D_output}/run_data.star --f benchmark_scripts/${RELION_BENCHMARK}/PostProcess/postprocess.star --corr_mic MotionCorr/job005/corrected_micrographs.star --first_frame 1 --last_frame -1 --o benchmark_scripts/${RELION_BENCHMARK}/Polish_t/ --min_p 10000 --eval_frac 0.5 --align_frac 0.5 --params3  --j 12

if [[ ! -s benchmark_scripts/${RELION_BENCHMARK}/Polish_t/opt_params_all_groups.txt ]]; then
    echo "relion_motion_refine failed to output opt_params_all_groups.txt"
    exit 1
fi
read par1 par2 par3  <<< $( awk '// {par1=$1; par2=$2; par3=$3};
     END { {print par1}; {print par2}; {print par3}; }' \
   benchmark_scripts/${RELION_BENCHMARK}/Polish_t/opt_params_all_groups.txt )
# replace this with your favourite formatting
printf "%s\n%s\n%s\n" "##########" " validate Polish (training) " "##########"
printf "%s %s %s\n" "par1" $par1 "(expected 1.0245)"
printf "%s %s %s\n" "par2" $par2 "(expected 7545)"
printf "%s %s %s\n" "par3" $par3 "(expected 2.4)"


#########################################################
# 068 Polish (apply)
# polish particles taken from Refine3D job, using movie frames from
# job 005, and other filenames taken from PostProcess output
#########################################################
mkdir -p benchmark_scripts/${RELION_BENCHMARK}/Polish

printf "%s\n%s\n%s\n" "################" " run Polish (apply) " "################"

#time mpirun `which relion_motion_refine_mpi` --i ${refine3D_output}/run_data.star --f benchmark_scripts/${RELION_BENCHMARK}/PostProcess/postprocess.star --corr_mic MotionCorr/job005/corrected_micrographs.star --first_frame 1 --last_frame -1 --o benchmark_scripts/${RELION_BENCHMARK}/Polish/ --params_file benchmark_scripts/${RELION_BENCHMARK}/Polish_t/opt_params_all_groups.txt --combine_frames --bfac_minfreq 20 --bfac_maxfreq -1 --j 12 

if [[ ! -s benchmark_scripts/${RELION_BENCHMARK}/Polish/shiny.star ]]; then
    echo "relion_motion_refine failed to output shiny.star"
    exit 1
fi

# No easy metric to check. You are supposed to inspect the output graphs showing the
# particle drift. 
