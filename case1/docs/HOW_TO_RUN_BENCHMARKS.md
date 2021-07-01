
# Getting organised

For details of the code, and setting the environment, see CODE.md

Benchmarks must be run from within a Relion project, since Relion expects
a certain directory structure. This will be either .../relion30_tutorial/
or .../10338/ (for aldolase).

The top directory of a Relion project should contain the files
benchmark_runs.py and slurm_template.sh, and the subdirectory JobFiles/
(contained *_job.star files). If these are not already within the
distributed datasets, then copies can be found on github in the
"e2e_benchmark" folder.

# Editing benchmark_runs.py

This provides scripts for running benchmarks. Code is provided for the
main pinch points, namely Class2D, Class3D and Refine3D jobs. Extra code
for other job types could be added by copying these examples.

Refine3D gives an example of pipelining, with the main refinement job
being followed by maskcreate and postprocess to give a more robust
resolution estimate. In principle, this example could be expanded to
run the whole end2end pipeline (see the flowcharts in the docs/ folder
on github), but this would not be very sensible: (a) the whole pipeline
would take weeks to run, (b) for benchmarking, it would be better to
spend the time on the pinch points, and (c) in practice, you would always
want to manually inspect the intermediate results, and perhaps adjust
the workflow.

With the provided files, you should only need to edit the line

> benchmark='refine3D'

to select your preferred benchmark.

# Editing JobFiles

The benchmark selected in benchmark_runs.py makes use of one or more
.star files in the JobFiles subdirectory. These contain parameters for
the job. In the top section ("Running options ...") are parameters that
you probably want to fix, e.g. the number of MPI tasks (nr_mpi) or
threads (nr_threads) that you want to use. The parameter other_args is
where you can set --cpu to use CPU acceleration.

The next section ("Compute options ...") don't have to be changed, but
could be explored. They mainly control how Relion handles i/o.

The final section ("Relion options ...") should not be edited. This
contains parameters specific to the workflow, and have been copied from
the initial processing. Randomly changing the particle diameter will
break the job!

The final section also specifies the input files needed. If a path contains
e.g. "/job028/" then it is using some of the supplied intermediate data.
If a path contains e.g. "/refine/" then it is using an alias that has
been set in benchmark_runs.py

NOTE: The aldolase workflow involves multiple Refine3D jobs.  The benchmark
jobfile corresponds to job030 in the workflow. You can compare
10338/JobFiles/Refine3D_job.star with 10338/Refine3D/job030/job.star
(though note I reordered the parameters in the former, to highlight the
ones which could be changed). To run a different Refine3D from the workflow,
the job file will need to be updated. Try

> diff Refine3D/job030/job.star Refine3D/job057/job.star

to see what needs updating (it is mainly input files). 

# Editing slurm_template.sh

This must be customised for the local platform. Some parameters are
set by Relion at runtime e.g. XXXmpinodesXXX is set from nr_mpi in
the JobFiles file.

The slurm script is used when submitting a job to a batch queue. This
is controlled by do_queue in the JobFiles file, and is not always used.
For example, the maskcreate and postprocess jobs are usually quick enough
to be run interactively.

# Running

After setting the environment, and editing the benchmark-specific
scripts as above, run as:

> nohup python benchmark_runs.py &

# Output

The top level project directory will have a file RUNNING_PIPELINER_default_Class3D
(or similar) that shows that the job is running. This should get removed when
the pipeline is finished (though beware crashed jobs, when it is not
always cleaned up properly).

The top level project directory will also have a file pipeline_Class3D.log
(or similar) which list the jobs that have been run within the pipeline.

Use that to find the job output, e.g. Class3D/job082/.  stdout and
stderr go to run.out and run.err in each job directory (as set in the
slurm file by Relion).

jobs are run with "time" and the timing information can be found in
run.err, while run.out confirms the nodes/tasks/threads used.

# Has it worked?

The pipeline has finished if each job directory has a file RELION_JOB_EXIT_SUCCESS.
Whether or not the job has worked correctly and given the right answer is
very task-specific.  In the results (aldolase_performance_benchmarks.pdf),
I have given the example of the population of the top class in 3D
classification. This was taken from the table data_model_classes in
the output file run_it025_model.star  Due to the stochastic nature of the
algorithm, this can vary, but you would expect the top class to be
significantly above the others.
