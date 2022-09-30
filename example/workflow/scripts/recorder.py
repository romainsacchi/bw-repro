import logging
import os
from pathlib import Path
import uuid
from bw2calc.log_utils import JSONFormatter


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
            for line in f_input:
                f_output.write(f"{line},")
            
            # TODO: Fix last line (no comma)
            f_output.write("[")


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
    pass


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
