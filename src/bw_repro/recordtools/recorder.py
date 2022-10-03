import logging
import os
import shutil
from pathlib import Path
from bw2calc import LCA, MultiLCA, MonteCarloLCA, MultiMonteCarlo, log_utils, utils
from subprocess import run
import brightway2 as bw
from . import folder_utils
import numpy as np
import yaml


PATH_HIDDEN = ".bw_repro/"
PATH_RESOURCES = Path().resolve() / PATH_HIDDEN / "resources"
folder_utils.create_folders()
folder_utils.create_snakefile()
folder_utils.create_script()


"""
    Create Conda environemnt.yaml file 
"""


def dependency_filter(enviroment_file_path):
    """
    Filters dependencies to avoid incompatibilities with different architectures or unnecessary dependencies.
    Must be improved.
    """
    with open(enviroment_file_path, "r") as stream:
        env_dict = yaml.safe_load(stream)

    words = ["bw", "brightway", "eidl", "python="]
    new_dependencies = []
    for word in words:
        for dependency in env_dict["dependencies"]:
            if word in dependency:
                new_dependencies.append(dependency)
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


def clean_json_output(dirpath):
    path_to_dir = Path(dirpath)
    filepath = path_to_dir / "calculation-steps.json"

    with open(filepath, "r") as f_input:
        with open(path_to_dir / "config.json", "w") as f_output:
            # Create an array
            f_output.write("[")
            # Append "," at end of each line
            new_lines = list(map(lambda line: f"{line},", f_input.readlines()))
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
    folder_utils.create_zip()
    shutil.rmtree(PATH_HIDDEN)
    # Merge environment and calculation files
    # merge_json_files(dirpath, filename)


def record(bw_module: bw, config: dict = None):
    PATH_LOGGER = PATH_HIDDEN + config["logger_path"]
    start_record(dirpath=PATH_LOGGER)

    # Here we have code that converts the bw package
    create_logger(dirpath=PATH_LOGGER, name=config["name"])
    bw_module.LCA = upgrade_LCA(config)
    bw_module.MonteCarloLCA = upgrade_MonteCarloLCA(config)

    # TODO: do this
    # bw_module= upgrade_MultiLCA(config)
    # bw_module.MultiMonteCarlo= upgrade_MultiMonteCarlo(config)
    bw_module.export_record = export_record
    # add a custom root to save change
    bw.repro = {"save": lambda: end_record(PATH_HIDDEN + config["logger_path"])}
    return bw


def export_record(config):
    end_record(PATH_HIDDEN + config["logger_path"])


"""
    Create a file handler to write bw2calc operations into a file.
"""


def create_logger(dirpath=None, name=None, **kwargs):
    # Use safe_filepath here

    formatter = log_utils.JSONFormatter()
    path_to_dir = Path(dirpath)
    fullpath = path_to_dir / "calculation-steps.json"

    json_handler = logging.FileHandler(
        filename=fullpath,
        mode="w+",
        encoding="utf-8",
    )
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
            demand_dict = utils.wrap_functional_unit(self.demand)
            db_to_export = bw.Database(demand_dict[0]["database"])
            db_dependencies = bw.databases[demand_dict[0]["database"]]["depends"]
            bw2package_name = f"{demand_dict[0]['database']}"
            # TODO: include an ecoinvent version detector using "./data/ei_id.yml"
            filepath = bw.BW2Package.export_obj(
                obj=db_to_export,
                filename=bw2package_name,
                # folder="/home/glarrea/bw_repro/dev")
                folder=PATH_RESOURCES,
            )
            filepath = Path(filepath).name
            # TODO: fix this
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
                        "file name": filepath,
                        "depends on": db_dependencies,
                    },
                ]
            }

            super().lcia(*args, **kwargs)
            self.logger.info(
                "Performing LCIA -test-",
                extra={
                    "calc_config": self.calc_config,
                    "calc_name": "LCA",
                    "seed": self.seed,
                    "function": self.lcia.__name__,
                    "demand": utils.wrap_functional_unit(self.demand),
                    "database_filepath": self.database_filepath,
                    "method": self.method,
                    "method_filepath": self.method_filepath,
                    "normalization": self.normalization,
                    "normalization_filepath": self.normalization_filepath,
                    "presamples": str(self.presamples),
                    "weighting": self.weighting,
                    "weighting_filepath": self.weighting_filepath,
                    "score": self.score,
                },
            )

    return newLCA


def upgrade_MonteCarloLCA(config):
    class newMonteCarloLCA(MonteCarloLCA):
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
            db_dependencies = bw.databases[demand_dict[0]["database"]]["depends"]
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
