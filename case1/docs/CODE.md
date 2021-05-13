# Code

The benchmarks require the following software: 


| Code | Origin    | Availability   |
|---------|--------------|-----------|
| RELION | Open source package from MRC-LMB Cambridge | Download |
| CTFFIND  | Package from Grigorieff lab        |  Download     | 
| relion-pipeline | CCP-EM module         | Supplied as Python       | 

# Relion

Available from https://www3.mrc-lmb.cam.ac.uk/relion/index.php?title=Main_Page
Use git clone to get master branch. It is easiest to get the latest version
from the Cambridge server, rather than picking up a snapshot from STFC. 

The benchmark was developed using RELION version 3.1-beta-commit-9090fd with
precision BASE=double, CUDA-ACC=single. Two sets of executables were compiled on the STFC
SCARF cluster, with and without CPU acceleration, following the instructions at
https://www3.mrc-lmb.cam.ac.uk/relion/index.php/Download_%26_install

### Basic

Intel compilers for cpu/MPI e.g. icc/2018.3.222-GCC-7.3.0-2.30
CUDA for GPU e.g. CUDA/10.1.105-GCC-8.2.0-2.31.1
With these compilers loaded ("module load"), cmake run with no options.
From within the build directory, type "cmake .." and then "make".

### Accelerated

Following the instructions at https://www3.mrc-lmb.cam.ac.uk/relion/index.php?title=Benchmarks_%26_computer_hardware#Intel_.22Skylake.22_systems_-_RELION_built_for_Intel.C2.AE_AVX-512_with_Intel.28R.29_C.2B.2B_Compiler_2018_Update_3 use the following cmake command:

CC=mpiicc CXX=mpiicpc cmake -DCUDA=OFF -DALTCPU=ON -DCudaTexture=OFF -DMKLFFT=ON -DCMAKE_C_FLAGS="-O3 -ip -g -xCOMMON-AVX512 -restrict " -DCMAKE_CXX_FLAGS="-O3 -ip -g -xCOMMON-AVX512 -restrict " -DGUI=OFF -DCMAKE_BUILD_TYPE=Release ..

### Further benchmarks on CLX cluster

RELION version 3.1.2-commit-dcab79 was built on the nextgenio Cascade Lake cluster. This is a slightly more
recent version of RELION with a number of minor fixes, but it should not affect the benchmark timings
significantly. Relion was built with acceleration options:

cmake -DTIFF_INCLUDE_DIR=/home/software/tiff/4.0.10/include -DTIFF_LIBRARY=/home/software/tiff/4.0.10/lib/libtiff.so.5 -DALTCPU=ON -DMKLFFT=ON -DFORCE_OWN_TBB=ON -DCMAKE_INSTALL_PREFIX=/lustre/home/nx04/nx04/mfarsara/build/relion ..

# CTFFIND

Available from https://grigoriefflab.umassmed.edu/ctffind4

This is unlikely to be needed for the benchmarks. It is only used for the CtfFind job type
(see workflows), and would only be required if the intermediate files need to
be re-created.


# CCP-EM pipeliner

Developed in-house, in collaboration with Sjors' group. A snapshot of the master branch has been included in directory 'e2e_benchmark' which is compatible with Relion 3.1. An updated version is being developed by CCP-EM that will be compatible with the forthcoming Relion 4, but that has not been used here.

The pipeliner library should be installed as follows:

python3 -m venv vrelion  
source vrelion/bin/activate
cd relion-pipeline   
pip install -r requirements.txt  
pip install -r requirements-dev.txt  
pre-commit install  
python setup.py install  

and used with:

source .../vrelion/bin/activate    
export PYTHONPATH=.../relion-pipeline:$PYTHONPATH

Benchmarks are run using the Python script benchmark_runs.py which loads the relion-pipeline package as:

from pipeliner.api.manage_project import RelionProject
