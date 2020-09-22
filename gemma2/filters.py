# Filtering functions

import collections
import logging
from os.path import dirname, basename, isfile
import sys
from gemma2.utility.options import get_options_ns
import gemma2.utility.safe as safe
from gemma2.format.rqtl2 import load_control, iter_pheno, iter_geno, write_control

def maf_filter(marker: str, maf_threshold: float, gs: list, na_strings: list) -> bool:
    """Pass maf threshold? FIXME: need to account for values.
    Returns True if SNP passes MAF threshold
    """
    realgs = list(filter(lambda g: not g in na_strings, gs))
    realnum = len(realgs)
    missing = len(gs) - realnum
    counter=collections.Counter(realgs)
    if len(counter) < 2:
        logging.debug(f"MAF filter {maf_threshold} fails {counter} at {marker}")
        return False
    # we take the second value which differs from GEMMA1 in the rare
    # instance that we have enough Heterozygous - FIXME when we have
    # genotype numbers
    minor_count = counter.most_common()[1][1]
    ret = minor_count/realnum > maf_threshold
    if not ret:
        logging.debug(f"MAF filter {maf_threshold} fails {counter} at {marker}")
    return ret

def filters(controlfn: str, pheno_column: int, maf: float):
    control = load_control(controlfn)
    print(control)
    na_strings = control.na_strings
    path = dirname(controlfn) or "."
    ids = []
    idx = []
    count = -1

    with safe.pheno_write_open() as p:
        for row in iter_pheno(path+"/"+control.pheno, header = True):
            count += 1
            if not row[pheno_column] in na_strings:
                id = row[0]
                ids.append(id)
                idx.append(count)
                p.write("\t".join([id,row[pheno_column]]).encode())
                p.write("\n".encode())
        phenofn = p.name
    ids = ids[1:] # strip leading column
    idx = idx[1:]
    markers = 0
    with safe.geno_write_open() as g:
        g.write("\t".join(["marker"]+ids).encode())
        g.write("\n".encode())
        for marker,genos in iter_geno(path+"/"+control.geno, header = False):
            gs = []
            for i in idx:
                gs.append(genos[i-1])
            if maf_filter(marker,maf,gs,na_strings):
                markers += 1
                g.write(marker.encode())
                g.write("\t".encode())
                g.write("".join(gs).encode())
                g.write("\n".encode())
        genofn = g.name
    inds = len(idx)
    # Write control file last
    write_control(inds,markers,control.phenotypes,genofn,phenofn,control.gmap,maf=maf)
