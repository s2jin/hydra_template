import os, sys
import tarfile
import hydra ## pip install hydra-core==1.2.0
from omegaconf import DictConfig

import logging
logging.basicConfig(level=logging.INFO)
logging = logging.getLogger(__name__)

os.environ['HYDRA_FULL_ERROR'] = '1'


@hydra.main(version_base='1.2', config_path='configs/', config_name="config.yaml")
def main(config: DictConfig):
    logging.info('COMMAND: python '+' '.join(sys.argv))

    if type(config.seed) != int:
        config.seed = round(time.time())
    logging.info(f'SET seed {config.seed}')

    config.job_num = '' if config.job_num == None else str(config.job_num)

    logging.info('<CONFIG>\n'+'\n'.join(print_config(config)))

    '''
    with open_dict(config):
        config.hydra = hydra.core.hydra_config.HydraConfig.get()
    '''

    if not config.checkpoint_path:
        config.checkpoint_path = os.path.join(config.save_dir, config.save_path)


    agent = hydra.utils.get_class(config.agent._target_)
    agent = agent(**config)
    save_code(config.checkpoint_path)

    agent.run()


def print_config(config_dict, level=0):
    if type(config_dict) != dict:
        config_dict = dict(config_dict)
    result = list()
    for key in config_dict:
        if type(config_dict[key]) == DictConfig:
            result.append(f"{'    '*level}[ {key} ]:\t(dict)")
            result += print_config(config_dict[key], level=level+1)
        else:
            result.append(f"{'    '*level}[ {key} ]:\t({type(config_dict[key]).__name__})\t{config_dict[key]}")

    return result

def save_code(path, mode='default'):
    codelist = [d.replace('.','/')+'.py' for d in sys.modules.keys() if 'src.' in d]
    codelist = [d for d in codelist if os.path.isfile(d)]
    codelist.append( os.path.join(path,'.hydra/') )
    codelist.append('run.py')

    with tarfile.open(os.path.join(path, f'code_{mode}.tar.gz'),'w:gz') as f:
        for filename in codelist:
            f.add(filename)

    ## save_conifg
    filename = os.path.join(path, '.hydra', 'config.yaml')
    with open(filename) as f:
        content = f.read()
    with open(os.path.join(path, f'config_{mode}.yaml'), 'w') as f:
        f.write(content+'\n')

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


if __name__ == "__main__":
    main()

