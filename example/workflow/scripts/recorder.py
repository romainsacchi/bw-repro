import logging
import os
from pathlib import Path
import uuid
from bw2calc.log_utils import JSONFormatter
import json
from subprocess import run

DUMMY_NAME_TO_TRIGGER_LOGGER = "there_is_a_low_probability_that_someone_will_call_a_record_like_that"

"""
    Create a file handler to write bw2calc operations into a file.
"""
def createJSONFileHandler(
    dirpath="logs",
    name="record",
    **kwargs
):
    path_to_dir = Path(dirpath)
    # TODO: Check if dirpath exist, if not create it
    if not path_to_dir.is_dir():
        os.mkdir(path_to_dir)
    fullpath = path_to_dir / f"{name}.json"

    # Create file handler
    handler = logging.FileHandler(filename=fullpath, encoding="utf-8")
    
    # Here we use default JSONFormatter found in bw2calc package
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    return handler


"""
    TODO: Read packages version and create needed to create a 'conda-like' environment.
"""
def dump_and_save_environment():
    # Call conda from python ?
    def conda_list(environment):
        proc = run(["conda", "list", "--json", "--name", environment],
                text=True, capture_output=True)
        return json.loads(proc.stdout)
    
    print(conda_list)
    pass

"""
    Transform JSON file to be valid as it will contain one JSON object for each line.
"""
def clean_json_output(dirpath, filename):
    path_to_dir = Path(dirpath)
    filepath = path_to_dir / f"{filename}.json"


    with open(filepath, "r") as f_input:
        with open(
            path_to_dir / f"{filename}-calculations.json",
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


"""
    Start recording data.
    - Read packages version
    - Setup logger
"""
def start_record(dirpath, filename):
    # TODO: retreive all needed information about environment
    # dump_and_save_environment
    
    # setup bw2 logging listener
    handler = createJSONFileHandler(dirpath, filename)
    logger = logging.getLogger("bw2calc")
    logger.addHandler(handler)


"""
    End recording.
    Here we can do things at the end of record:
    - Clean JSON file
    - Create one single output file.

"""
def end_record(dirpath, filename):
    clean_json_output(dirpath, filename)
    # TODO: merge environment and calculation files
    pass


def test():
    import brightway2 as bw
    bw.projects.set_current("my_project")
    
    # dummy log config is needed to trigger
    log_config= {
        "dirpath":"logs",
        "name": DUMMY_NAME_TO_TRIGGER_LOGGER
    }

    def do_random_lca():
            meth = bw.methods.random()
            process = bw.Database('ecoinvent36').random()
            fu = {process: 1}
            lca = bw.LCA(fu, meth, log_config=log_config)
            lca.lci()
            lca.lcia()

    start_record("logs", "test")
    for _ in range(0,5):
        do_random_lca()

    end_record("logs", "test")

if __name__ == "__main__":
    test()
