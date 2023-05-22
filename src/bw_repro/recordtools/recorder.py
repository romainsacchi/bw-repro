import logging
import os
import shutil
import time
from pathlib import Path
from bw2calc import log_utils, utils
from subprocess import run
import bw2data, bw2io
from . import folder_utils
import numpy as np
import yaml
# from importlib.resources import files
import json
PATH_HIDDEN = ".bw_repro/"
PATH_RESOURCES = Path().resolve() / PATH_HIDDEN / "resources"
folder_utils.create_folders()
folder_utils.create_snakefile()
folder_utils.create_script()

"""
    Create Conda environemnt.yaml file 
"""

#
def dependency_filter(enviroment_file_path):
    """
    Filters dependencies to avoid incompatibilities with different architectures or unnecessary dependencies.
    Must be improved.
    """
    with open(enviroment_file_path, "r") as stream:
        env_dict = yaml.safe_load(stream)

    words = ["bw", "brightway", "eidl", "python=", "numpy","pandas","pypardiso", "scipy"]
    new_dependencies = []
    new_dependencies_pip = []

    for word in words:
        for dependency in env_dict["dependencies"]:
            if isinstance(dependency,str) and word in dependency:
                new_dependencies.append(dependency)
            if isinstance(dependency,dict) and dependency.get("pip"):
                for dependency_pip in dependency["pip"]:
                    if word in dependency_pip:
                        new_dependencies_pip.append(dependency_pip)
    new_dependencies.append({"pip": new_dependencies_pip})
    env_dict["dependencies"] = new_dependencies

    with open(enviroment_file_path, "w") as output_file:
        yaml.dump(env_dict, output_file)


def dump_and_save_environment(dirpath):

    yaml_path = Path(dirpath).parent / "envs" / f"environment.yaml"

    with open(yaml_path, "w") as f:
        # Call conda from python
        proc = run(
            [
                "conda",
                "env",
                "export",
                "--name",
                os.environ["CONDA_DEFAULT_ENV"],
                "--no-builds",
            ],
            text=True,
            capture_output=True,
        )
        f.write(proc.stdout)

    dependency_filter(yaml_path)


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


def clean_json_output():
    path_to_dir = Path(PATH_HIDDEN + "config/")
    filepath = path_to_dir / "config_messy.json"
    with open(filepath, "r") as f_input:
        with open(path_to_dir / f"config.json", "w") as f_output:
            # Create an array
            f_output.write("[")

            # Append "," at end of each line
            new_lines = list(map(lambda line: f"{line},", f_input.readlines()))

            # Remove last ","
            new_lines[-1] = new_lines[-1][:-1]
            for l in new_lines:
                f_output.write(l)
            # Close list
            f_output.write("]")

    with open(path_to_dir / f"config.json","r") as f_output:
        report_file = json.load(f_output)
    with open(path_to_dir / "config.yaml", "w") as readable_output:
        yaml.dump(report_file, readable_output)
    os.remove(path_to_dir / "config_messy.json")


def clean_the_mess():
    clean_json_output()


"""
    End recording.
    Here we can do things at the end of record:
    - Clean JSON file
    - Create one single output file.

"""


def end_record(output_path):
    def end_record_method():
        clean_the_mess()
        folder_utils.create_zip(output_path)
        shutil.rmtree(PATH_HIDDEN)
    return end_record_method

    # Merge environment and calculation files
    # merge_json_files(dirpath, filename)

def record(bw2calc_module, config: dict = None):
    PATH_LOGGER = PATH_HIDDEN + "config/"
    start_record(dirpath=PATH_LOGGER)

    # Here we have code that converts the bw package
    create_logger(dirpath=PATH_LOGGER, name=config["name"])
    bw2calc_module.config_bwrepro = config

    if bw2calc_module.__version__[0] > 1:
        bw2calc_module.LCA = upgrade_LCA(config, bw2calc_module)
    else:
        bw2calc_module.LCA = upgrade_LCA(config, bw2calc_module)
        bw2calc_module.MonteCarloLCA = upgrade_MonteCarloLCA(config, bw2calc_module)

    # TODO: do this
    # bw_module= upgrade_MultiLCA(config)
    # bw_module.MultiMonteCarlo= upgrade_MultiMonteCarlo(config)
    bw2calc_module.export_record = export_record(bw2calc_module)
    # add a custom root to save change
    bw2calc_module.repro = {"save": lambda: end_record(PATH_HIDDEN + config["logger_path"])}
    return bw2calc_module


def export_record(bw2calc_module):
    return end_record(bw2calc_module.config_bwrepro["output_path"])


"""
    Create a file handler to write bw2calc operations into a file.
"""


def create_logger(dirpath=None, name=None, **kwargs):
    # Use safe_filepath here

    formatter = log_utils.JSONFormatter()
    path_to_dir = Path(dirpath)
    fullpath = path_to_dir / "config_messy.json"

    json_handler = logging.FileHandler(
        filename=fullpath,
        mode="w+",
        encoding="utf-8",
    )
    json_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(json_handler)
    logger.setLevel(logging.INFO)


def upgrade_LCA(config, bw2calc_base):
    class newLCA(bw2calc_base.LCA):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.logger = logging.getLogger(config["name"])

        def lcia(self, *args, **kwargs):
            demand_dict = utils.wrap_functional_unit(self.demand)
            if bw2calc_base.__version__[0] > 1:
                demand_name = str(bw2data.get_activity(demand_dict[0]["id"]))
                db_to_export_name = bw2data.get_activity(demand_dict[0]["id"]).as_dict()["database"] # for 2.5 only handles 1 activity
                db_to_export = bw2data.Database(db_to_export_name)
                db_dependencies = bw2data.databases[db_to_export_name]["depends"]
                bw2package_name = f"{db_to_export_name}"
            else:
                demand_name = str(list(self.demand.keys())[0])
                db_to_export_name = demand_dict[0]["database"]
                db_to_export = bw2data.Database(db_to_export_name)
                db_dependencies = bw2data.databases[demand_dict[0]["database"]]["depends"]
                bw2package_name = f"{demand_dict[0]['database']}"


            # TODO: include an ecoinvent version detector using "./data/ei_id.yml"
            # filepath = bw2io.BW2Package.export_obj(
            #     obj=db_to_export,
            #     filename=bw2package_name,
            #     folder=PATH_RESOURCES,
            # )
            # filepath = Path(filepath).name
            filepath = "Here comes the path of the DataPackage (WIP)"
            # with open(files("bw_repro.data").joinpath("ei_id.yaml")) as eifile:
            #     ei_dict = yaml.safe_load(eifile)

            template_db = {
                "name": "database",
                "version": 3.9,
                "system model": "cutoff",
                "available in resources": False,
                "depends on": ["biosphere3"],
            },

            self.calc_config = {
                "databases": [
                    {
                        "name": db_to_export_name,
                        "available in resources": False,
                        "file name": filepath,
                        "depends on": db_dependencies,
                    },
                ]
            }
            start_time = time.time()
            super().lcia(*args, **kwargs)
            finish_time = time.time()

            if bw2calc_base.__version__[0] > 1:
                databases_file_paths = [str(bw2data.Database(db).filepath_processed()) for db in db_to_export.find_graph_dependents()]
                randomness_data = {
                    "use_distributions": self.use_distributions,
                    "use_arrays": self.use_arrays,
                }
            else:
                databases_file_paths = self.database_filepath
                randomness_data = {
                    "seed": self.seed
                }

            self.logger.info(
                "Performing LCIA",
                extra={
                    "calc_config": self.calc_config,
                    "calc_name": "LCA",
                    "seed": randomness_data,
                    "calculation_time": finish_time - start_time,
                    "function": self.lcia.__name__,
                    "demand": utils.wrap_functional_unit(self.demand),
                    "demand_repr": demand_name,
                    "functional_unit_amount": demand_dict[0]["amount"],
                    "method": self.method,
                    "normalization": self.normalization,
                    # "presamples": str(self.presamples),
                    "weighting": self.weighting,
                    "database_filepath": databases_file_paths,
                    "method_metadata": bw2data.methods.get(self.method),
                    "normalization_metadata": bw2data.normalizations.get(self.normalization),
                    "weighting_metadata": bw2data.weightings.get(self.weighting),
                    "score": self.score,
                },
            )

    return newLCA

def upgrade_MonteCarloLCA(config, bw2calc_base):
    class newMonteCarloLCA(bw2calc_base.MonteCarloLCA):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.list_scores = []
            self.score_mean = 0
            self.score_std = 0
            self.counter = 0
            self.logger = logging.getLogger(config["name"])

        def __next__(self):
            self.counter += 1
            _ = super().__next__()
            self.list_scores.append(self.score)
            self.score_mean = np.mean(self.list_scores)
            self.score_std = np.std(self.list_scores)

            return _

        def record(self):
            demand_dict = utils.wrap_functional_unit(self.demand)
            db_dependencies = bw2data.databases[demand_dict[0]["database"]]["depends"]
            bw2package_name = f"{demand_dict[0]['database']}.bw2package"
            # TODO: include an ecoinvent version detector using "./data/ei_id.yml"
            self.calc_config = {
                "databases": [
                    {
                        "name": "ecoinvent",
                        "version": "3.8",
                        "system model": "cutoff",
                        "available in resources": False,
                        "depends on": ["biosphere3"],
                    },
                    {
                        "name": demand_dict[0]["database"],
                        "available in resources": True,
                        "file name": bw2package_name,
                        "depends on": db_dependencies,
                    },
                ]
            }
            self.logger.info(
                "Performing MonteCarloLCA -test-",
                extra={
                    "calc_name": "MonteCarloLCA",
                    "seed": self.seed,
                    "function": self.load_data.__name__,
                    "demand": utils.wrap_functional_unit(self.demand),
                    "database_filepath": self.database_filepath,
                    "method": self.method,
                    "method_filepath": self.method_filepath,
                    "normalization": self.normalization,
                    "normalization_filepath": self.normalization_filepath,
                    "presamples": str(self.presamples),
                    "weighting": self.weighting,
                    "weighting_filepath": self.weighting_filepath,
                    "simulations": self.counter,
                    "score_mean": self.score,
                    "score_std": self.score_std,
                },
            )

    return newMonteCarloLCA
