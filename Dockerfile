FROM --platform=linux/amd64 ncbi/sra-tools as sra-tools
WORKDIR /root
RUN mkdir ./output

FROM --platform=linux/amd64 continuumio/miniconda3 as bcl2fastq2
WORKDIR /root
RUN mkdir ./output
RUN conda install bih-cubi::bcl2fastq2
ENTRYPOINT [ "bcl2fastq" ]

FROM --platform=linux/amd64 biocontainers/bowtie2:v2.4.1_cv1 as bowtie2
WORKDIR /root
USER root
RUN mkdir ./output

FROM --platform=linux/amd64 biocontainers/samtools:v1.9-4-deb_cv1 as samtools
WORKDIR /root
USER root
RUN mkdir ./output
ENTRYPOINT [ "samtools" ]

FROM --platform=linux/amd64 biocontainers/freebayes:v1.2.0-2-deb_cv1 as freebayes
WORKDIR /root
USER root
RUN mkdir ./output
ENTRYPOINT [ "freebayes" ]
