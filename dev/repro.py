import logging
import os
from pathlib import Path
from bw2calc import LCA, MultiLCA, MonteCarloLCA, MultiMonteCarlo, log_utils, utils
from subprocess import run
import brightway2 as bw

"""
    Create Conda environemnt.yaml file 
"""
def dump_and_save_environment(dirpath):
    with open(Path(dirpath) / f"environment.yaml", "w") as f:
        # Call conda from python
        proc = run(["conda", "env", "export", "--name", os.environ['CONDA_DEFAULT_ENV'], "--no-builds"], text=True, capture_output=True)
        f.write(proc.stdout)

"""
    Start recording data.
    - Read packages version
    - Setup logger
"""
def start_record(dirpath):
    path_to_dir = Path(dirpath)
    # Check if dirpath exist, if not create it
    if not path_to_dir.is_dir():
        os.mkdir(path_to_dir)

    # Retreive all needed information about environment
    dump_and_save_environment(dirpath)

"""
    Transform JSON file to be valid as it will contain one JSON object for each line.
"""
def clean_json_output(dirpath):
    path_to_dir = Path(dirpath)
    filepath = path_to_dir / "calculation-steps.json"

    with open(filepath, "r") as f_input:
        with open(
            path_to_dir / "calculations.json",
            "w"
        ) as f_output:
            # Create an array
            f_output.write("[")
            # Append "," at end of each line
            new_lines = list(
                map(
                    lambda line: f"{line},",
                    f_input.readlines()
                )
            )
            new_lines[-1] = new_lines[-1][:-1]
            for l in new_lines:
                f_output.write(l)
            f_output.write("]")

    os.remove(path_to_dir / f"calculation-steps.json")

"""
    Transform JSON file to be valid as it will contain one JSON object for each line.
"""
def clean_json_output(dirpath):
    path_to_dir = Path(dirpath)
    filepath = path_to_dir / "calculation-steps.json"


    with open(filepath, "r") as f_input:
        with open(
            path_to_dir / f"calculations.json",
            "w"
        ) as f_output:
            # Create an array
            f_output.write("[")

            # Append "," at end of each line
            new_lines = list(
                map(
                    lambda line: f"{line},",
                    f_input.readlines()
                )
            )

            # Remove last ","
            new_lines[-1] = new_lines[-1][:-1]
            for l in new_lines:
                f_output.write(l)
            # Close list
            f_output.write("]")

    os.remove(path_to_dir / "calculation-steps.json")

def clean_the_mess(dirpath):
    clean_json_output(dirpath)

"""
    End recording.
    Here we can do things at the end of record:
    - Clean JSON file
    - Create one single output file.

"""
def end_record(dirpath):
    clean_the_mess(dirpath)
    # Merge environment and calculation files
    # merge_json_files(dirpath, filename)

def coolname(bw_module: bw, config:dict=None):
    start_record(dirpath=config["logger_path"])

    # Here we have code that converts the bw package
    create_logger(dirpath=config["logger_path"], name = config["name"])
    bw_module.LCA= upgrade_LCA(config)
    # bw.MultiLCA= upgrade_MultiLCA(config)
    # bw.MonteCarloLCA= upgrade_MonteCarloLCA(config)
    # bw.MultiMonteCarlo= upgrade_MultiMonteCarlo(config)
    
    # add a custom root to save change
    bw.repro = { "save": end_record}
    return bw

"""
    Create a file handler to write bw2calc operations into a file.
"""
def create_logger(dirpath=None, name=None, **kwargs):
    # Use safe_filepath here

    formatter = log_utils.JSONFormatter()
    path_to_dir = Path(dirpath)
    fullpath = path_to_dir / "calculation-steps.json"

    json_handler = logging.FileHandler(filename=fullpath,mode="w+", encoding='utf-8',)
    json_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(json_handler)
    logger.setLevel(logging.INFO)

def upgrade_LCA(config):
    class newLCA(LCA):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.logger = logging.getLogger(config["name"])

        def lcia(self, *args, **kwargs):
            super().lcia(*args,**kwargs)
            self.logger.info(
                "Performing LCIA -test-",
                extra={
                    'calc_name': "LCA",
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
        "logger_path": "yooolo",
        "name": "yoo"
    }
    bw = coolname(bw, log_config)

    bw.projects.set_current("ABM_SN")
    # bw.projects.set_current("my_project")

    def do_random_lca():
        meth = bw.methods.random()
        process = bw.Database('ecoinvent36').random()
        fu = {process: 1}
        lca = bw.LCA(fu, meth)
        lca.lci()
        lca.lcia()

    for _ in range(0, 5):
        do_random_lca()
    
    bw.repro["save"](log_config["logger_path"])

if __name__ == "__main__":
    test()


def upgrade_MonteCarloLCA(config):
    class newMonteCarloLCA(MonteCarloLCA):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.logger = logging.getLogger(config["name"])
        
        def load_data(self, *args, **kwargs):
            super().load_data(*args,**kwargs)
            self.logger.info(
                "Performing LCIA -test-",
                extra={
                    'calc_name': "MonteCarloLCA",
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

    return newMonteCarloLCA
