#! /usr/bin/env python
import argparse
import re
import json
import os
import time
import subprocess
from pathlib import Path

from logger import MultiLevelLogger, SimpleTimer

def set_environment():
    env = os.environ.copy()

    # Set some default values for environment variables
    os.environ['RELION_CMD'] = env.get('RELION_CMD', '')
    os.environ['RELION_CPUS_PER_TASK'] = env.get('RELION_CPUS_PER_TASK', '1')
    os.environ['RELION_OUTPUT_DIR'] = env.get('RELION_OUTPUT_DIR', str(Path('relion_output').absolute()))

    if 'RELION_PROJ_DIR' not in env:
        raise RuntimeError('No project directory specified!')

def setup_output_folders():
    output_dir = Path(os.environ['RELION_OUTPUT_DIR'])
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / 'Refine3D/run').mkdir(parents=True, exist_ok=True)
    (output_dir / 'MaskCreate').mkdir(parents=True, exist_ok=True)
    (output_dir / 'Class2D').mkdir(parents=True, exist_ok=True)
    (output_dir / 'Class3D').mkdir(parents=True, exist_ok=True)
    (output_dir / 'PostProcess').mkdir(parents=True, exist_ok=True)
    (output_dir / 'CtfRefine').mkdir(parents=True, exist_ok=True)
    (output_dir / 'Polish').mkdir(parents=True, exist_ok=True)
    (output_dir / 'Polish_t').mkdir(parents=True, exist_ok=True)
    (output_dir / 'Extract').mkdir(parents=True, exist_ok=True)
    (output_dir / 'Import').mkdir(parents=True, exist_ok=True)
    (output_dir / 'Select').mkdir(parents=True, exist_ok=True)

    return output_dir

def read_pipeline(file_name):
    with file_name.open('r') as handle:
        lines = handle.readlines()

    def _is_command(line):
        return len(line) > 0 and line[0] != "#"

    lines = map(lambda s: s.strip(), lines)
    lines = list(filter(_is_command, lines))
    names = [re.search(r'.* (relion_[a-z_]+) ', line)[1] if 'relion' in line else line for line in lines]
    return list(zip(names, lines))


def write_json(file_name, data):
    with Path(file_name).open('w') as handle:
        json.dump(data, handle)

def run_step(step):
    env = os.environ.copy()
    subprocess.call(step, env=env, shell=True)

def parse_metrics(name, step, output_dir):
    try:
        if name == 'relion_postprocess':
            # Get resolution, B factor, and particle box fraction as metrics for PostPorcess
            file_name = output_dir / 'PostProcess/postprocess.star'
            names = ['_rlnFinalResolution', '_rlnBfactorUsedForSharpening', '_rlnParticleBoxFractionSolventMask']

            with file_name.open('r') as handle:
                lines = handle.readlines()

            lines = [line.strip().split() for line in lines]
            lines = [line for line in lines if len(line) > 0]
            lines = [line for line in lines if line[0] in names]
            names = [line[0].strip() for line in lines]
            values = [float(line[1].strip()) for line in lines]
            return dict(zip(names, values))
        elif name == 'relion_ctf_refine_mpi' or name == 'relion_ctf_refine':
            # Get beam tilt X/Y as metric from CtfRefine
            file_name = output_dir / 'CtfRefine/particles_ctf_refine.star'
            with file_name.open('r') as handle:
                lines = handle.readlines()
            line = lines[18]
            line = line.strip().split()
            return dict(beam_tilt_x=float(line[10]), beam_tilt_y=float(line[11]))
        elif name == 'relion_refine_mpi' or name == 'relion_refine':
            if 'Refine3D' in step:
                # Get rotation, translation, and resolution accuracy from Refine3D
                file_name = output_dir / 'Refine3D/run_model.star'
                with file_name.open('r') as handle:
                    lines = handle.readlines()
                line = lines[40]
                line = line.strip().split()
                return dict(acc_rotation=float(line[2]), acc_translation=float(line[3]), resolution=float(line[4]))
            elif 'Class3D' in step:
                # Get resolution, number of classes, and class distributions
                file_name = output_dir / 'Class3D/run_model.star'
                with file_name.open('r') as handle:
                    lines = handle.readlines()

                metrics = dict(
                    _rlnCurrentResolution=float(lines[8].strip().split()[-1]),
                    _rlnNrClasses=float(lines[15].strip().split()[-1])
                )

                # class distributions
                for i, line in enumerate(lines[range(40, 44)]):
                    class_occ = line.strip().split()[1]
                    metrics[f'class_{i+1}_occ'] = class_occ

                return metrics
        elif name == 'relion_preprocess_mpi' or name == 'relion_preprocess':
            # Get pixel/particle size
            file_name = output_dir / 'Extract/particles.star'
            with file_name.open('r') as handle:
                lines = handle.readlines()
            line = lines[18]
            line = line.strip().split()
            return dict(pixel_size=float(line[7]), particle_size=float(line[8]))
        elif name == 'relion_motion_refine_mpi' or name =='relion_motion_refine':
            # Get opt params from output training file
            file_name = output_dir / 'Polish_t/opt_params_all_groups.txt'
            with file_name.open('r') as handle:
                lines = handle.readlines()
            line = lines[0]
            line = line.strip().split()
            line = list(map(float, line))
            params = dict(zip(range(len(line)), line))
            return params
    except:
        pass

    return {}



def main(pipeline_file):
    set_environment()
    output_dir = setup_output_folders()
    steps = read_pipeline(pipeline_file)

    logger = MultiLevelLogger(output_dir / 'log.txt')

    logger.begin('Running pipeline')
    logger.message(f'Pipeline file {pipeline_file}')
    logger.message(f'No. Steps {len(steps)}')

    pipeline_timer = SimpleTimer()
    pipeline_timer.start()

    os.chdir(os.environ['RELION_PROJ_DIR'])

    step_metrics = []
    for name, step in steps:
        # Run step in pipeline
        logger.begin(f'Running step {name}')
        timer = SimpleTimer()
        timer.start()

        run_step(step)

        timer.stop()
        duration = timer.elapsed_time()
        logger.ended(f'Running step {name}')

        # Capture outputs
        step_metric = dict(name=name, duration=duration)
        step_metric.update(parse_metrics(name, step, output_dir))
        step_metrics.append(step_metric)

        logger.begin(f'Step {name} results')
        for k, v in step_metric.items():
            logger.message(f'{k}: {v}')
        logger.ended(f'Step {name} results')

    pipeline_timer.stop()
    total_duration = pipeline_timer.elapsed_time()

    metrics = {}
    metrics['pipeline_file'] = str(pipeline_file)
    metrics['total_duration'] = total_duration
    metrics['steps'] = step_metrics
    relion_env_vars = os.environ.copy()
    relion_env_vars = {k: v for k, v in relion_env_vars.items() if 'RELION' in k}
    metrics.update(relion_env_vars)

    json_file = output_dir / 'metrics.json'
    write_json(json_file, metrics)

    logger.message(f'Writing output to {json_file}')
    logger.ended('Running pipeline')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Benchmark multiple Relion steps.')
    parser.add_argument('pipeline_file', metavar='p', type=str,
                        help='Text file containing Relion pipeline')
    args = parser.parse_args()
    pipeline_file = Path(args.pipeline_file)

    main(pipeline_file)
