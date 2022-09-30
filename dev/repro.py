import logging
from datetime import datetime
import os
import uuid
from bw2calc import LCA, MultiLCA, MonteCarloLCA, MultiMonteCarlo, log_utils, utils

import brightway2 as bw

def coolname(bw_module: bw, config:dict=None):
    # Here we have code that converts the bw package
    create_logger(dirpath=config["logger_path"], name = config["name"])
    bw_module.LCA= upgrade_LCA(config)
    # bw.MultiLCA= upgrade_MultiLCA(config)
    # bw.MonteCarloLCA= upgrade_MonteCarloLCA(config)
    # bw.MultiMonteCarlo= upgrade_MultiMonteCarlo(config)
    return bw

def create_logger(dirpath=None, name=None, **kwargs):

    # assert os.path.isdir(dirpath) and os.access(dirpath, os.W_OK)

    # Use safe_filepath here
    filename = "{}.{}.json".format(
        name or uuid.uuid4().hex,
        str(datetime.utcnow())
    )
    formatter = log_utils.JSONFormatter()
    fp = os.path.abspath(os.path.join(dirpath, filename))

    json_handler = logging.FileHandler(filename=fp,mode="w+", encoding='utf-8',)
    json_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(json_handler)
    logger.setLevel(logging.INFO)

def upgrade_LCA(config):
    class newLCA(LCA):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.logger = logging.getLogger(config["name"])
            # self.repro_logger = logging.getLogger(config["name"])
        def lcia(self, *args, **kwargs):
            super().lcia(*args,**kwargs)
            self.logger.info("Performing LCIA -test-",
                             extra={
                                 'name': "LCA",
                                 'seed': self.seed,
                                 'function': self.lcia.__name__,
                                 'demand': utils.wrap_functional_unit(self.demand),
                                 'database_filepath': self.database_filepath,
                                 'method': self.method,
                                 'method_filepath': self.method_filepath,
                                 'normalization': self.normalization,
                                 'normalization_filepath': self.normalization_filepath,
                                 'presamples': str(self.presamples),
                                 'weighting': self.weighting,
                                 'weighting_filepath': self.weighting_filepath,
                                 'score': self.score,
                                 }
                             )

    return newLCA


def test():
    import brightway2 as bw
    log_config = {
        "logger_path": "",
        "name": "yooo"
    }
    bw = coolname(bw, log_config)
    bw.projects.set_current("ABM_SN")

    # dummy log config is needed to trigger


    def do_random_lca():
        meth = bw.methods.random()
        process = bw.Database('ecoinvent36').random()
        fu = {process: 1}
        lca = bw.LCA(fu, meth)
        lca.lci()
        lca.lcia()

    for _ in range(0, 5):
        do_random_lca()

if __name__ == "__main__":
    test()


def upgrade_MonteCarloLCA(config):
    class newMonteCarloLCA(MonteCarloLCA):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.logger = logging.getLogger(config["name"])
        def load_data(self, *args, **kwargs):
            super().load_data(*args,**kwargs)
            self.logger.info("Performing MonteCarloLCA -test-",
                             extra={
                                 'name': "MonteCarloLCA",
                                 'seed': self.seed,
                                 'function': self.load_data.__name__,
                                 'demand': utils.wrap_functional_unit(self.demand),
                                 'database_filepath': self.database_filepath,
                                 'method': self.method,
                                 'method_filepath': self.method_filepath,
                                 'normalization': self.normalization,
                                 'normalization_filepath': self.normalization_filepath,
                                 'presamples': str(self.presamples),
                                 'weighting': self.weighting,
                                 'weighting_filepath': self.weighting_filepath,
                                 'score': self.score,
                                 }
                             )

    return newMonteCarloLCA
