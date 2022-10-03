# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 14:03:51 2022

@author: hahn
"""


import shutil
from pathlib import Path

PATH = Path().resolve()

def create_folders():
    
    proj_path_path = Path.cwd() / ".bw_repro"
    proj_path_path.mkdir(parents=True, exist_ok=True)
    

    config_path = Path.cwd() / ".bw_repro" /  'config'
    config_path.mkdir(parents=True, exist_ok=True)
    
    envs_path = Path.cwd() / ".bw_repro" /  'envs'
    envs_path.mkdir(parents=True, exist_ok=True)
    
    resources_path = Path.cwd() / ".bw_repro" /  'resources'
    resources_path.mkdir(parents=True, exist_ok=True)
    
    scripts_path = Path.cwd() / ".bw_repro" /  'scripts'
    scripts_path.mkdir(parents=True, exist_ok=True)
    
def create_zip():
    
    output_filename = 'output'
    dir_name = PATH / '.bw_repro/'
    shutil.make_archive(output_filename, 'zip', dir_name)
    
def create_snakefile():
    
    snkf = open( PATH / ".bw_repro/Snakefile.txt", "w")
    snkf.write("rule run:\n\tinput:\n\t\t'workflow/config/config.json'\n\n\toutput:\n\t\t'workflow/results/results.txt'\n\tconda:\n\t\t'envs/env.yaml'\n\tthreads: 1\n\tscript:\n\t\t'scripts/script.py'")
    snkf.close()

def create_script():
    script = open(".bw_repro/scripts/script.py", "w")
    script.write('import bw2io, bw2data, bw2calc\nimport eidl\nfrom pathlib import Path\nimport json\n\nCONFIG_PATH = Path(__file__).parent.parent / "config"\nRESOURCES_PATH = Path(__file__).parent.parent / "resources"\nRESULTS_PATH = Path(__file__).parent.parent / "results"\n\nwith open(CONFIG_PATH / "config.json") as f:\n\tconfig = json.load(f)\n\nprint("Creating project...")\
                 \n\nbw2data.projects.set_current("default")\n\nprint("Installing biosphere...")\nprint(bw2data.databases)\nbw2io.bw2setup()\n\n\ndef install_dbs(db):\n\n\tif db["available in resources"]:\n\t\tif all(i in bw2data.databases for i in db["depends on"]):\n\t\t\tprint(f"Importing {db[\'name\']}...")\n\t\t\tbw2io.BW2Package.import_file \
                 (RESOURCES_PATH / db["file name"])\n\t\telse:\n\t\t\traise ValueError(f"Missing databases in order to import {db[\'name\']}.")\n\telse:\n\t\tif db["name"] == "ecoinvent" and all(i in bw2data.databases for i in db["depends on"]):\n\t\t\tname = db["name"]\n\t\t\tver = db["version"]\n\t\t\tsystem_model = db["system model"]\n\t\t\tif f"{name} {system_model} {ver}" not in \
                 bw2data.databases:\n\t\t\t\teidl.get_ecoinvent(db_name=f"{name} {system_model} {ver}",auto_write=True,version=ver,system_model=system_model,)\n\t\t\t\telse\n\t\t\t\t\tprint(f"{name} {ver} {system_model} already present.")\n\t\t\telse:\n\t\t\t\traise \
                 ValueError("Not implemented yet")\n\n\ndef run_lca(lca_setup):\n\tdb = lca_setup["demand"]["database"]\n\tcode = lca_setup["demand"]["code"]\n\tqty = lca_setup["demand"]["quantity"]\n\tact = bw2data.get_activity((db, code))\n\tmethod = bw2data.methods.random()\n\tlca = bw2calc.LCA({act: qty}, method)\n\tlca.lci()\n\tlca.lcia()\n\treturn lca.score\n\ndbs = \
                 config[0]["databases"]\n\nprint("Running LCA...")\nwith open(RESULTS_PATH / "results.txt", "w") as f:\n\tfor lca_setup in config:\n\t\tf.write(str(run_lca(lca_setup)))')

    script.close()
    
# create_folder()
# create_snakefile()
# create_script()
# create_zip()
