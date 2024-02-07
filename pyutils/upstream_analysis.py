import os
import shutil
import subprocess
import logging

from pyutils.constants import (
    PROJECT_DIR,
    OUTPUT_DIR,
    REF_SEQS
)

logging.basicConfig(
    filename="run_upstream.log",
    format="[%(asctime)s %(process)s]: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.INFO
)

COMMOND_CMD = ['docker', 'run', '--rm', '-v', f'{OUTPUT_DIR}:/root/output']


def run_cmd(cmd, work_dir, log_file):
    with subprocess.Popen(
        cmd,
        text=True,
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as p:
        stdout, stderr = p.communicate()
    with open(log_file, 'a') as f:
        f.write(f'[command]:\n{" ".join(cmd)}\n')
        f.write(f'[stdout]:\n{stdout}\n')
        f.write(f'[stderr]:\n{stderr}\n')
        f.write(f'[return code]:\n{p.returncode}\n')


def need_output_file(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return True
    return False


def workflow(sra_id, exp_name):

    # This is actually the directory from the container
    exp_name_dir = os.path.join('output', exp_name.replace(' ', '_'))
    refseq_file = os.path.join(exp_name_dir, 'refseq.fasta')
    if not os.path.exists(exp_name_dir):
        os.mkdir(exp_name_dir)
    if not os.path.exists(refseq_file):
        shutil.copyfile(REF_SEQS[exp_name], refseq_file)
        logging.info(f'{exp_name} [start] build BMA index')
        run_cmd(
            cmd=[
                *COMMOND_CMD,
                'trace_mutation-bowtie2',
                'bowtie2-build',
                refseq_file,
                refseq_file
            ],
            work_dir=exp_name_dir,
            log_file=os.path.join(exp_name_dir, 'refseq.log')
        )
        logging.info(f'{exp_name} [complete] build BMA index')

    work_dir = os.path.join(exp_name_dir, sra_id)
    log_file = os.path.join(work_dir, f'{sra_id}.log')
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)

    logging.info(f'{sra_id} [start] fasterq-dump')
    run_cmd(
        cmd=[
            *COMMOND_CMD,
            '-v', f'{os.path.join(PROJECT_DIR, '.ncbi')}:/root/.ncbi',
            'trace_mutation-sra-tools',
            'fasterq-dump',
            sra_id,
            '-O', work_dir,
            '-v',
        ],
        work_dir=work_dir,
        log_file=log_file
    )
    logging.info(f'{sra_id} [complete] fasterq-dump')

    sam_file = os.path.join(work_dir, f'{sra_id}.sam')
    if need_output_file(sam_file):
        logging.info(f'{sra_id} [start] bowtie2')
        run_cmd(
            cmd=[
                *COMMOND_CMD,
                'trace_mutation-bowtie2',
                'bowtie2',
                '--no-unal',
                '-q',
                '-x', refseq_file,
                '-1', os.path.join(work_dir, f'{sra_id}_1.fastq'),
                '-2', os.path.join(work_dir, f'{sra_id}_2.fastq'),
                '-S', sam_file,
            ],
            work_dir=work_dir,
            log_file=log_file
        )
        logging.info(f'{sra_id} [complete] bowtie2')

    sorted_bam_file = os.path.join(work_dir, f'{sra_id}.sorted.bam')
    if need_output_file(sorted_bam_file):
        logging.info(f'{sra_id} [start] samtools sort')
        run_cmd(
            cmd=[
                *COMMOND_CMD,
                'trace_mutation-samtools',
                'sort',
                sam_file,
                '-o', sorted_bam_file,
            ],
            work_dir=work_dir,
            log_file=log_file
        )
        logging.info(f'{sra_id} [complete] samtools sort')

    sorted_bam_index_file = os.path.join(
        work_dir,
        f'{sra_id}.sorted.bam.bai'
    )
    if need_output_file(sorted_bam_index_file):
        logging.info(f'{sra_id} [start] samtools index')
        run_cmd(
            cmd=[
                *COMMOND_CMD,
                'trace_mutation-samtools',
                'index',
                os.path.join(work_dir, f'{sra_id}.sorted.bam'),
            ],
            work_dir=work_dir,
            log_file=log_file
        )
        logging.info(f'{sra_id} [complete] samtools index')
    return sorted_bam_file, refseq_file, work_dir, sra_id, log_file


def run_freebayes(sorted_bam_file, refseq_file, work_dir, sra_id, log_file):

    vcf_file = os.path.join(work_dir, f'{sra_id}.vcf')
    if need_output_file(vcf_file):
        logging.info(f'{sra_id} [start] freebayes')
        run_cmd(
            cmd=[
                *COMMOND_CMD,
                'trace_mutation-freebayes',
                '-f', refseq_file,
                sorted_bam_file,
                '-v', vcf_file,
                '--haplotype-length', '0',
                '--min-alternate-count', '1',
                '--min-alternate-fraction', '0',
                '--pooled-continuous',
                '--report-monomorphic',
                '--no-indels',
            ],
            work_dir=work_dir,
            log_file=log_file
        )
        logging.info(f'{sra_id} [complete] freebayes')
