import sys
from automated_APTDemo import logging_setup
__author__ = 'venom'

logger = logging_setup.init_logging()

def gen_jif(icd_target):
    logger.debug('Generating a JIF for {}'.format(icd_target))
    generate = jif_assembler.JIFBuilder(out_target, **config.config_dict)
    generate.gen_jifs()

