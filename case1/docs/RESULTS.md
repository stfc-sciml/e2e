# Results

All durations are in units of seconds. Additional metrics captured include:

 - `acc_rotation`
 - `acc_translation`
 - `_rlnFinalResolution`
 - `_rlnParticleBoxFractionSolventMask`
 - `_rlnBfactorUsedForSharpening`
 - `beam_tilt_x`
 - `beam_tilt_y`

## Rabbit Muscle Aldolase

Using [EMPIAR dataset 10338](https://www.ebi.ac.uk/pdbe/emdb/empiar/entry/10338/).

### PEARL
Run using the relion singularity container with Relion version 3.1.2.

#### Stage 2
| system | nodes | GPUs | ntasks | job_id | total_duration | ('relion_refine_mpi', 'duration') | ('relion_mask_create', 'duration') | ('relion_postprocess', 'duration') | ('relion_ctf_refine_mpi', 'duration') | ('relion_refine_mpi', 'acc_rotation') | ('relion_refine_mpi', 'acc_translation') | ('relion_refine_mpi', 'resolution') | ('relion_postprocess', '_rlnFinalResolution') | ('relion_postprocess', '_rlnBfactorUsedForSharpening') | ('relion_postprocess', '_rlnParticleBoxFractionSolventMask') | ('relion_ctf_refine_mpi', 'beam_tilt_x') | ('relion_ctf_refine_mpi', 'beam_tilt_y') |
|--------|-------|------|--------|--------|----------------|-----------------------------------|------------------------------------|------------------------------------|---------------------------------------|---------------------------------------|------------------------------------------|-------------------------------------|-----------------------------------------------|--------------------------------------------------------|--------------------------------------------------------------|------------------------------------------|------------------------------------------|
| PEARL  |     1 |    1 |      3 |  28256 |    31785.12639 |                       27851.31983 |                        41.74223351 |                        11.26367927 |                           3880.546141 |                                 1.227 |                                  0.47824 |                            3.629367 |                                      3.150769 |                                             -114.15386 |                                                    44.736736 |                                 -0.11276 |                                  0.10334 |
| PEARL  |     1 |    2 |      5 |  28257 |    16983.38385 |                       14575.14572 |                        41.83322978 |                        11.27802634 |                           2354.872569 |                                 1.213 |                                  0.47824 |                            3.629367 |                                      3.150769 |                                             -114.15386 |                                                    44.736736 |                                 -0.11172 |                                 0.104509 |
| PEARL  |     1 |    4 |     11 |  28258 |    10561.79723 |                       9376.763466 |                        41.48376679 |                        11.12217498 |                           1132.167431 |                                 1.234 |                                   0.4872 |                            3.629367 |                                      3.150769 |                                             -114.15386 |                                                    44.736736 |                                 -0.11315 |                                 0.102733 |
| PEARL  |     1 |    8 |     21 |  28259 |    4969.295334 |                       4265.943474 |                        40.93388176 |                        10.79140139 |                           651.3773253 |                                 1.233 |                                  0.47824 |                            3.629367 |                                      3.150769 |                                             -114.15386 |                                                    44.736736 |                                 -0.11153 |                                 0.107299 |
| PEARL  |     1 |   16 |     41 |  28260 |    2841.958082 |                       2357.543861 |                        40.91957307 |                        11.21114421 |                           432.0415237 |                                 1.224 |                                   0.4816 |                            3.629367 |                                      3.150769 |                                             -114.15386 |                                                    44.736736 |                                 -0.11405 |                                 0.100917 |

### SCARF
Run using the relion singularity container with Relion version 3.1.2.

#### Stage 2
| system | nodes | GPUs | ntasks | job_id | total_duration | relion_refine_mpi duration | relion_mask_create duration | relion_postprocess duration | relion_ctf_refine_mpi duration | relion_refine_mpi acc_rotation | relion_refine_mpi acc_translation | relion_refine_mpi resolution | relion_postprocess _rlnFinalResolution | relion_postprocess _rlnBfactorUsedForSharpening | relion_postprocess _rlnParticleBoxFractionSolventMask | relion_ctf_refine_mpi beam_tilt_x | relion_ctf_refine_mpi beam_tilt_y |
|--------|-------|------|--------|--------|----------------|----------------------------|-----------------------------|-----------------------------|--------------------------------|--------------------------------|-----------------------------------|------------------------------|----------------------------------------|-------------------------------------------------|-------------------------------------------------------|-----------------------------------|-----------------------------------|
| SCARF  |    16 |    0 |    161 | 173962 |    32738.90418 |                32106.58736 |                 119.2381268 |                 23.02787757 |                    489.3474171 |                          1.261 |                           0.49392 |                     3.629367 |                               3.150769 |                                      -114.15386 |                                             44.736736 |                          -0.11352 |                          0.102728 |
| SCARF  |     8 |    0 |     81 | 173964 |    48099.03498 |                47573.72996 |                 55.72322869 |                 11.62700438 |                    456.6823997 |                          1.231 |                           0.48496 |                     3.629367 |                               3.150769 |                                      -114.15386 |                                             44.736736 |                          -0.11137 |                          0.104368 |
## Plasmodium Ribosome

Using the standard Plasmodium Ribosome datasets used by the Relion benchmarks. Run using the relion singularity container with Relion version 3.1.2.

| system | GPUs | ntasks | job_id | total_duration | relion_refine_mpi duration | relion_refine_mpi duration |
|--------|------|--------|--------|----------------|----------------------------|----------------------------|
| PEARL  |    1 |      3 |  28261 |    83173.58003 |                76029.18724 |                7144.386019 |
| PEARL  |    2 |      5 |  28262 |    39838.16112 |                37526.42442 |                2311.719316 |
| PEARL  |    4 |     11 |  28263 |    18710.24553 |                17673.56563 |                1036.668402 |
| PEARL  |    8 |     21 |  28264 |    11656.12791 |                10487.92895 |                1168.177476 |
| PEARL  |   16 |     41 |  28265 |    8561.946626 |                7388.201614 |                1173.733041 |


# Systems

## PEARL
PEARL is a high-performance computing cluster, designed primarily for Deep Learning and AI research. At its core are two NVIDIA DGX-2s. Each DGX-2 utilises 16 Tesla V100 GPUs with a total of 512GB of GPU memory. Each also has 1.5TB of system RAM, two Intel Xeon Platinum CPUs and 30TB of NVME SSD local storage. The DGX-2s are connected over 100Gbit/s EDR InfiniBand to two Boston Flash-IO Talyn servers which together provide half a petabyte of NVMe storage.