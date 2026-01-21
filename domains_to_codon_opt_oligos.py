# Name: domains_to_codon_opt_oligos.py
# Author: Connor Ludwig
# Organization: Bintu Lab, Stanford University
# Updated: 10/03/2020
# Modified: species passed via command line

import os
import sys
import pandas as pd
import math
from dnachisel import *


def optimizeOligo(failed, ID, dna_sequence, GCglobMax, species):
    problem = DnaOptimizationProblem(
        sequence=dna_sequence,
        constraints=[
            AvoidPattern('BsmBI_site'),
            AvoidPattern('7xC'),
            AvoidRareCodons(species=species, min_frequency=0.1),
            EnforceGCContent(mini=0.25, maxi=GCglobMax),
            EnforceGCContent(mini=0.20, maxi=0.70, window=50),
            EnforceTranslation(),
            AvoidStopCodons()
        ],
        objectives=[
            CodonOptimize(species=species, method='match_codon_usage')
        ]
    )

    try:
        problem.resolve_constraints()
    except:
        if ID not in failed:
            failed.append(ID)
        GCglobMax += 0.01
        print('++++++++++ GOING UP TO %s ++++++++++' % str(GCglobMax))
        optimizedDNA, failed = optimizeOligo(
            failed, ID, dna_sequence, GCglobMax, species
        )
        return optimizedDNA, failed

    problem.optimize()
    optimizedDNA = str(problem.sequence)
    return optimizedDNA, failed


# Command-line arguments
# sys.argv[1] = species (e.g. h_sapiens, m_musculus, e_coli)
# sys.argv[2] = input CSV with unique tiles
# sys.argv[3] = library name

species = sys.argv[1]
df = pd.read_csv(sys.argv[2])
libName = sys.argv[3]

# store tile ID and protein sequence column values as lists
tileID = df['Tile ID'].values.tolist()
tileAAseq = df['Tile Sequence'].values.tolist()

# initialize arrays
tileDNAseq = []
failedList = []

# codon optimization loop
for i in range(len(tileID)):
    initialDNAseq = reverse_translate(tileAAseq[i])
    coDNAseq, failedList = optimizeOligo(
        failedList,
        tileID[i],
        initialDNAseq,
        GCglobMax=0.65,
        species=species
    )
    tileDNAseq.append(coDNAseq)

# report failures
if len(failedList) != 0:
    print('Oligos with global GC content > 65%: ', failedList)
    failedFile = sys.argv[2][:-4] + '_oligos-globalGC-gt65-IDs.txt'
    with open(failedFile, 'w') as f:
        for failedID in failedList:
            f.write("%s\n" % failedID)
else:
    print('All oligos passed codon optimization with specified constraints')

# save output
df['DNA Sequence'] = tileDNAseq
df['Library'] = libName
savename = sys.argv[2][:-4] + '_codon-opt-oligos.csv'
df.to_csv(savename, index=False)
