#!/bin/bash
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=12
#SBATCH --nodes=1
#SBATCH --partition=scarf

set -e

#####
# This benchmark implements jobs 043, 048, 049, 050 of the workflow
# which cover 3D refinement of the top 3D class (2x sampling), mask creation,
# postprocessing, and per-particle Ctf refinement (defocus and global
# astigmatism) and beam tilt estimation.
# Note that jobs 044-047 were failed attempts at postprocessing, and
# are ignored.
#####

# Set this environment variable to something unique for each
# run of this benchmark
RELION_BENCHMARK='benchmark3'
# use this if running full benchmark
#refine3D_output=benchmark_scripts/${RELION_BENCHMARK}/Refine3D
# use pre-calculated output when testing later steps
refine3D_output=Refine3D/job043

mkdir -p benchmark_scripts/${RELION_BENCHMARK}

#########################################################
# 043 Refine3D
# using particles from job042 and 3D reference from job039
#########################################################

mkdir -p benchmark_scripts/${RELION_BENCHMARK}/Refine3D

printf "%s\n%s\n%s\n" "################" " run Refine3D " "################"

#time mpirun $RELION_CMD relion_refine_mpi --o benchmark_scripts/${RELION_BENCHMARK}/Refine3D/run --auto_refine --split_random_halves --i Select/job042/particles.star --ref Class3D/job039/run_it025_class002.mrc --ini_high 30 --dont_combine_weights_via_disc --pool 30 --pad 1  --skip_gridding  --ctf --ctf_corrected_ref --particle_diameter 120 --flatten_solvent --zero_mask --oversampling 1 --healpix_order 2 --auto_local_healpix_order 4 --offset_range 5 --offset_step 2 --sym D2 --low_resol_join_halves 40 --norm --scale  --j 1 --gpu ""

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
                                                 if (reso > 3.8) 
                                                     reso_flag=1
                                                 else
                                                     reso_flag=0 };
     END { {print accRot}; {print accRot_flag}; {print accTrans}; {print accTrans_flag}; {print reso} {print reso_flag}; }' \
   ${refine3D_output}/run_model.star )
# replace this with your favourite formatting
printf "%s\n%s\n%s\n" "###################" " Refine3D " "###################"
printf "%s %s %s\n" "Accuracy of rotations" $accRot "(expected 1.173)"
if [[ $accRot_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: rotation accuracy worse than expected"
fi
printf "%s %s %s\n" "Accuracy of translations " $accTrans " (expected 0.478)"
if [[ $accTrans_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: translation accuracy worse than expected"
fi
printf "%s %s %s\n" "Estimated resolution " $reso " (expected 3.63)"
if [[ $reso_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: estimated unmasked resolution worse than expected" 
fi


#########################################################
# 048 MaskCreate
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
# 049 Post Process
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
                                                 if (solv > 50 || solv < 40) 
                                                     solv_flag=1
                                                 else
                                                     solv_flag=0 };
     END { {print reso}; {print res_flag}; {print bfac}; {print bfac_flag}; {print solv} {print solv_flag}; }' \
   benchmark_scripts/${RELION_BENCHMARK}/PostProcess/postprocess.star )

# replace this with your favourite formatting
printf "%s\n%s\n%s\n" "######################" " validate PostProcess " "######################"
printf "%s %s %s\n" "Estimated resolution" $reso "(expected 3.15)"
if [[ $res_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: resolution worse than expected!"
fi
printf "%s %s %s\n" "B factor sharpening " $bfac " (expected -114)"
if [[ $bfac_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: change in B factor, check Guinier plot in logfile.pdf"
fi
printf "%s %s %s\n" "Percent solvent " $solv " (expected 44.7)"
if [[ $solv_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: change in solvent content, check mask" 
fi

#########################################################
# 050 CtfRefine
# corrections for particles taken from Refine3D job, other filenames taken
# from PostProcess output
#########################################################
mkdir -p benchmark_scripts/${RELION_BENCHMARK}/CtfRefine

printf "%s\n%s\n%s\n" "################" " run CtfRefine " "################"

#time mpirun `which relion_ctf_refine_mpi` --i ${refine3D_output}/run_data.star --f benchmark_scripts/${RELION_BENCHMARK}/PostProcess/postprocess.star --o benchmark_scripts/${RELION_BENCHMARK}/CtfRefine/ --fit_defocus --kmin_defocus 30 --fit_mode fpmff --fit_beamtilt --kmin_tilt 30 --j 12

if [[ ! -s benchmark_scripts/${RELION_BENCHMARK}/CtfRefine/particles_ctf_refine.star ]]; then
    echo "relion_ctf_refine failed to output particles_ctf_refine.star"
    exit 1
fi
read beamTiltX beamTiltX_flag beamTiltY beamTiltY_flag <<< $( awk '/july/ {beamTiltX=$11; beamTiltY=$12;
                                                 if (beamTiltX < -0.2) 
                                                     beamTiltX_flag=1
                                                 else
                                                     beamTiltX_flag=0 ;
                                                 if (beamTiltY > 0.2) 
                                                     beamTiltY_flag=1
                                                 else
                                                     beamTiltY_flag=0 };
     END { {print beamTiltX}; {print beamTiltX_flag}; {print beamTiltY}; {print beamTiltY_flag}; }' \
   benchmark_scripts/${RELION_BENCHMARK}/CtfRefine/particles_ctf_refine.star )
# replace this with your favourite formatting
printf "%s\n%s\n%s\n" "###################" " validate CtfRefine " "###################"
printf "%s %s %s\n" "Beam tilt in X" $beamTiltX "(expected -0.11)"
if [[ $beamTiltX_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: beam tilt X more than expected"
fi
printf "%s %s %s\n" "Beam tilt in Y " $beamTiltY " (expected 0.10)"
if [[ $beamTiltY_flag -eq 1 ]]; then
    printf "%s\n" "WARNING: beam tilt Y more than expected"
fi

