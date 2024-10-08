import os
import json
import time
import hashlib
from copy import deepcopy

import logging
logging.basicConfig(level=logging.INFO)
logging = logging.getLogger(__name__)

from omegaconf import DictConfig, OmegaConf


class Agent():
    

    def __init__(self, **kwargs):

        self.config = DictConfig(kwargs)  
        set_seed(self.config.seed)

    def run(self):
        raise NotImplementedError  ## XXX




def cache(inputs=None, outputs=None, verbose=True):

    if outputs == None: mode = 'r'
    else:               mode = 'w'

    if inputs == None: 
        if verbose: logging.warn(f"NONE INPUT: cache key is `{inputs}`")

    hashkey = hashlib.sha1(f"{inputs}".encode('utf8')).hexdigest()
    cache_filepath = os.path.join('cache', hashkey)

    if mode == 'r':
        if not os.path.isfile(cache_filepath):
            if verbose: logging.warn(f'Not Found "{cache_filepath}"')
            return None, hashkey

        if verbose: logging.info(f'LOAD cache file "{cache_filepath}"')
        with open(cache_filepath) as f:
            data = json.load(f)
        return data, hashkey

    else: ## mode = 'w'
        if verbose: logging.info(f'SAVE cache file "{cache_filepath}"')
        with open(cache_filepath,'w') as f:
            json.dump(outputs, f, ensure_ascii=False)


def set_seed(seed):
    # torch.manual_seed(seed)
    # np.random.seed(seed)
    # random.seed(seed)
    pass


if __name__=='__main__':
    
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('config_path', nargs='+', metavar='str', type=str)
    args = parser.parse_args()
    
    if len(args.config_path) != 1: raise ValueError(f'config_path need one path, but input is {args.config_path}')
    config = OmegaConf.load(args.config_path[0])
    agent = Agent(**config)

    agent.run()
