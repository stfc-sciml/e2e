# This script makes use of the CCP-EM pipeliner API to Relion.
#
# Martyn Winn, STFC, Dec 2020

import time, os

from pipeliner.api.manage_project import RelionProject

my_project = RelionProject()
benchmark='refine3D'

# For the distributed benchmark, the project is already created
#my_project.start_new_project()
#print("Project set up")

if benchmark == 'particle_picking':
    # schedule 1
    autopick_job = my_project.schedule_job("JobFiles/AutoPick_template_job.star")   

    my_project.run_schedule(
            "AutoPick", 
            [autopick_job], 
            nr_repeat=1,
            minutes_wait=1, 
            minutes_wait_before=0, 
            seconds_wait_after=60,
        )
elif benchmark == 'class2D':
    # schedule 2
    class2D_job = my_project.schedule_job("JobFiles/Class2D_job.star")

    my_project.run_schedule(
            "Class2D", 
            [class2D_job], 
            nr_repeat=1,
            minutes_wait=1, 
            minutes_wait_before=0, 
            seconds_wait_after=60,
        )
elif benchmark == 'class3D':
    # schedule 3
    class3D_job = my_project.schedule_job("JobFiles/Class3D_job.star")

    my_project.run_schedule(
            "Class3D", 
            [class3D_job], 
            nr_repeat=1,
            minutes_wait=1, 
            minutes_wait_before=0, 
            seconds_wait_after=60,
        )
elif benchmark == 'refine3D':
    # schedule 4
    refine3D_job = my_project.schedule_job("JobFiles/Refine3D_job.star")
    # add an alias for this job. This alias is used in the subsequent *_job.star files 
    # so don't change it without also changing those files.
    cmd = "cd Refine3D; ln -s "+os.path.basename(refine3D_job.strip("/"))+" refine; cd .."
    os.system(cmd)
    maskcreate_job = my_project.schedule_job("JobFiles/MaskCreate_job.star")
    # add an alias for this job. This alias is used in the subsequent *_job.star files 
    # so don't change it without also changing those files.
    cmd = "cd MaskCreate; ln -s "+os.path.basename(maskcreate_job.strip("/"))+" maskcreate; cd .."
    os.system(cmd)
    # this is official way, but doesn't seem to work right
    #my_project.add_alias(maskcreate_job,"maskcreate")
    postprocess_job = my_project.schedule_job("JobFiles/PostProcess_job.star")

    my_project.run_schedule(
            "Refine3D", 
            [refine3D_job, maskcreate_job, postprocess_job], 
            nr_repeat=1,
            minutes_wait=1, 
            minutes_wait_before=0, 
            seconds_wait_after=60,
        )

elif benchmark == 'delete_jobs':

    # edit this for particular job(s)
    my_project.delete_job("Refine3D/job036/")
    my_project.delete_job("Refine3D/job037/")
