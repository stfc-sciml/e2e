# Case 1 overview

Case 1 is supplied in 3 parts:

- This documentation
- Three example datasets. These include experimental data, intermediate data from processing, and
scripts/configurations specific to the dataset. Further details are in docs/DATASETS.md
- Code which can be used for all datasets. These are executables from the Relion package,
the additional program ctffind, and a Python package "pipeliner" developed by CCP-EM for
running Relion pipelines from the command line. Further details are in docs/CODE.md

Running a benchmark consists of the following steps:
1. Compile Relion executables locally to take advantage of latest compilers, options, etc.
2. Make sure these, and ctffind (if needed), are on PATH.
3. Make sure "pipeliner" is on PYTHONPATH.
4. Unpack the example dataset of choice.
5. Within the dataset, look at benchmark_runs.py  Edit "benchmark = " near the top to
choose a benchmark.
6. The benchmarks make use of slurm_template.sh to submit batch jobs. Edit this for
local system.
7. Run!

