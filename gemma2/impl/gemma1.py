# GEMMA1 calls

import logging
from os.path import dirname, basename
from subprocess import run,CompletedProcess

from gemma2.format.bimbam import write_bimbam
from gemma2.utility.options import get_options_ns

def compute_kinship(control, standardized):
    opts = get_options_ns()
    output_path = dirname(opts.out_prefix)
    if not output_path:
        output_path = "."
    output_basename = basename(opts.out_prefix)
    logging.info('Computing GRM with GEMMA1')
    logging.info('Convert to intermediate BIMBAM')
    genofn, phenofn = write_bimbam(control['name'])
    logging.info(f"Call gemma with {genofn}")
    k_type = "2" if not standardized else "1"
    args1 = [opts.gemma1_bin,'-debug','-debug-data','-outdir',output_path,'-o',output_basename,'-gk',k_type,'-g',genofn,'-p',phenofn]
    cmd = " ".join(args1)
    logging.warning("Calling: "+cmd)
    # print(args1)
    run(args1, check=True)
    logging.info(f"Writing to {output_path}/{output_basename}.cXX.txt")
