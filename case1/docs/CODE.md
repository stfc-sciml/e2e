# Code

The benchmarks require the following software: 


| Code | Origin    | Availability   |
|---------|--------------|-----------|
| RELION | Open source package from MRC-LMB Cambridge | Download |
| CTFFIND  | Package from ...        | Supplied as binary     | 
| pipeliner | CCP-EM module         | Supplied as Python       | 

# Relion

Available from https://www3.mrc-lmb.cam.ac.uk/relion/index.php?title=Main_Page
Use git clone to get master branch. It is easiest to get the latest version
from the Cambridge server, rather than picking up a snapshot from STFC. 

The benchmark was developed using RELION version 3.1-beta-commit-9090fd with
precision BASE=double, CUDA-ACC=single. Two sets of executables were compiled,
following the instructions at
https://www3.mrc-lmb.cam.ac.uk/relion/index.php/Download_%26_install

### Basic

Intel compilers for cpu/MPI e.g. icc/2018.3.222-GCC-7.3.0-2.30
CUDA for GPU e.g. CUDA/10.1.105-GCC-8.2.0-2.31.1
With these compilers loaded ("module load"), cmake run with no options.
From within the build directory, type "cmake .." and then "make".

### Accelerated

Following the instructions at https://www3.mrc-lmb.cam.ac.uk/relion/index.php?title=Benchmarks_%26_computer_hardware#Intel_.22Skylake.22_systems_-_RELION_built_for_Intel.C2.AE_AVX-512_with_Intel.28R.29_C.2B.2B_Compiler_2018_Update_3 use the following cmake command:

CC=mpiicc CXX=mpiicpc cmake -DCUDA=OFF -DALTCPU=ON -DCudaTexture=OFF -DMKLFFT=ON -DCMAKE_C_FLAGS="-O3 -ip -g -xCOMMON-AVX512 -restrict " -DCMAKE_CXX_FLAGS="-O3 -ip -g -xCOMMON-AVX512 -restrict " -DGUI=OFF -DCMAKE_BUILD_TYPE=Release ..


# CTFFIND

Available from https://grigoriefflab.umassmed.edu/ctffind4

This is unlikely to be needed for the benchmarks. Only if input files need to
be re-created.

We will supply a linux binary for convenience.


# CCP-EM pipeliner

Developed in-house, in collaboration with Sjors' group.