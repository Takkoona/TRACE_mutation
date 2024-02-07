import logging


logging.basicConfig(
    filename="run_downstream.log",
    format="[%(asctime)s %(process)s]: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.INFO
)


def update_mutation_summary(mutation_summary, alignment):
    refseq, readseq = alignment.sequences
    logging.info(readseq.id)
    ref_indices, read_indices = alignment.indices
    for ref_index, read_index in zip(ref_indices, read_indices):
        ref_l, read_l = alignment[:, read_index]
        if ref_index != -1:
        # if ref_index != -1 and ref_l != '-' and ref_l != read_l and read_l != '-':
            key_value = (ref_index+1, read_l)
            if key_value not in mutation_summary:
                mutation_summary[key_value] = 0
            mutation_summary[key_value] += 1
