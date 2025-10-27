# Library-Design
Command line Python scripts for creating diverse oligonucleotide libraries from a set of protein tiles, including Golden Gate cloning overhangs.

# Create a conda environment from required_packages.txt
`conda create --name lib-design --file required_packages.txt`
`conda activate lib-design`

# Format reference protein sequences from UniprotKb or Uniref
Use the scripts `uniref_fast2csv.py` or `uniprotkb_fast2csv.py` to generate Python-readable .csv files from Uniprot reference sequence and metadata. For each script, you will need a UniRef90 or a UniProtKB fasta file downloaded with all sequences of interest, an dthe corresponding UniRef or UniProtKB metadata file for human protein clusters. The third argument is the savename for your new .csv file.

Example usage:
`python uniprotkb_fasta2csv.py /path/to/protein_fasta.fa /path/to/metadata.csv your_proteins.csv`

# Generate protein tiles from the generated list of proteins
Use the script `generate_tiles.py` to create all possible tiles of a desired amino acid length to query from the list of proteins. Specify the desired tile length, the desired distance between tiles (we recommend 10 amino acids for thorough tiling), and if your generated .csv file originated from Uniref or UniprotKB metadata.

Example usage:
`python generate_tiles.py your_proteins.csv 80 10 'uniprotkb'`

This script will generate three .csvs: one with all possible tile sequences, one with duplicates removed, and a summary dataframe to report how many tiles were created from each protein. The .csvs will be formatted as follows:
`your_proteins_all-tiles.csv`
`your_proteins_unique-tiles.csv`
`your_proteins_tile-summary.csv`
We recommend moving forward to further design steps with the unique-tiles.csv.

# Generate oligonucleotide sequences from the created protein tiles.
Use the script `domains_to_codon_opt_oligos.py` to reverse-translate the generated protein tiles into oligonucleotide sequences codon-optimized for human expression systems. This script will also ensure no oligonucleotides contain BsmBI cut sites, making them compatible for Golden Gate cloning applications, and will avoid polyC tracks that complicate high-throughput sequencing readouts.

Example usage: `python domains_to_codon_opt_oligos.py /path/to/your_proteins_unique-tiles.csv 'desired_library_name'

The script will generate a .csv entitled `desired_library_name_codon-opt-oligos.csv`.

# Generate random protein sequences to add to the library as negative controls.
Use the script `generate_randomers.py` to create a specific number of random protein sequences to serve as controls. We recommend generating 10% of your total library size. The -length argument specifies the length of each oligo in base pairs, NOT amino acids.

Example usage: `python generate_randomers.py -number 500 -length 240 -out_file 'your_randomers'`

A .csv file entitled `your_randomers.csv` will be produced.

# Combine tile oligonucleotides and randomers into one dataframe for further library QC
Example usage: `compile_dataframes.py /desired/path/to/your_final_library.csv /path/to/desired_library_name_codon-opt-oligos.csv /path/to/your_randomers.csv`

# Run QC on final library to ensure GC content is within synthesis standards and codon usage largely mirrors native human proteins
Example usage: `python qc_oligos_GC_content.py /path/to/your_final_library.csv`

This script will output the percentage of tiles with GC content >60% or <35%, which may flag them during library synthesis.

Example usage: `python qc_oligos_codon_usage.py /path/to/your_final_library.csv`

This script will compare the codon usage across your library to human codon usage. If any codon is overrepresented by >10% compared to human use, consider re-running oligo optimization scripts.

# Finish library and send for synthesis!
Use Python to add Golden Gate cloning overhangs to the DNA sequence of each member. We recommend the following sequences:

5': `CGTCTCActcc`

3': `ggatGGAGACG`

Then, send a final .csv file with two columns (`label` and `oligo` - a label column and a DNA sequence column) to your DNA synthesis company of choice!
