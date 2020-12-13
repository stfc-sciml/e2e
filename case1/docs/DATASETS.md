# Datasets

Three datasets are provided with this benchmark. The details of each individual
dataset are given in the table below. 


| Dataset | EMPIAR ID    | Size (GB) | Description                                                                                                                                      |
|---------|--------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| RELION tutorial | n/a | 8 | Small dataset from the Relion tutorial for rapid testing of setup. |
| Rabbit muscle aldolase  | 10338          | ??      | Martyn's. 200kV microscope.      |
| Coronavirus-HKU1 haemagglutinin esterase | 10390          | ??        |  Tom's |

# Layout of each dataset

Each dataset contains the following:

- Most files are from a completed Relion project. These give the necessary input data for benchmarking runs.
- The JobFiles subdirectory contains job control files in .star format for running the benchmarking jobs. Most parameters should be left untouched, as appropriate for the benchmark. Parameters in the Running section should be adjusted to specific the number of MPI tasks, threads, etc. Parameters in the Compute section could be adjusted to tune the job.
- The file slurm_template.sh is referenced from the job files, and provides a template for cluster submission.
- The script benchmark_runs.py is the main way of running the benchmarks. Select the benchmark by editing at the top of the script, and run.
