import os

PROJECT_DIR = os.path.join(os.path.dirname(__file__), os.path.pardir)

DATA_DIR = os.path.join(PROJECT_DIR, 'data')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output')
PLOTS_DIR = os.path.join(PROJECT_DIR, 'plots')

SRA_SUMMARY_FILE = os.path.join(OUTPUT_DIR, 'sra_summary.csv')

REF_SEQS = {
    'MEK1 screen': os.path.join(DATA_DIR, 'TWIST_MEK1_cDNA.fasta')
}


if __name__ == '__main__':
    print(os.listdir(PROJECT_DIR))
