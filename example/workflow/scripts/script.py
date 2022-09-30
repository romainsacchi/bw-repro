import bw2data
import bw2io

import bw2calc
import eidl
from pathlib import Path
import json

CONFIG_PATH = Path(__file__).parent.parent / "config"
RESOURCES_PATH = Path(__file__).parent.parent / "resources"
RESULTS_PATH = Path(__file__).parent.parent / "results"

with open(CONFIG_PATH / "config.json") as f:
    config = json.load(f)

print("Creating project...")

bw2data.projects.set_current("default")

print("Installing biosphere...")
print(bw2data.databases)
bw2io.bw2setup()


def install_dbs(db):

    if db["available in resources"]:
        if all(i in bw2data.databases for i in db["depends on"]):
            # import local db
            print(f"Importing {db['name']}...")
            bw2io.BW2Package.import_file(
                RESOURCES_PATH / db["file name"]
            )
        else:
            raise ValueError(f"Missing databases in order to import {db['name']}.")
    else:
        if db["name"] == "ecoinvent" and all(i in bw2data.databases for i in db["depends on"]):
            name = db["name"]
            ver = db["version"]
            system_model = db["system model"]
            if f"{name} {system_model} {ver}" not in bw2data.databases:
                # download ei from website
                eidl.get_ecoinvent(
                    db_name=f"{name} {system_model} {ver}",
                    auto_write=True,
                    version=ver,
                    system_model=system_model,
                )
            else:
                print(f"{name} {ver} {system_model} already present.")
        else:
            raise ValueError("Not implemented yet")


def run_lca(lca_setup):
    # fetch activity
    # it should be in the form of {act: 1}
    db = lca_setup["demand"]["database"]
    code = lca_setup["demand"]["code"]
    qty = lca_setup["demand"]["quantity"]

    for c in config[0]:
        if
    act = bw2data.get_activity((db, code))
    # fetch method
    method = bw2data.methods.random()
    # run lca
    lca = bw2calc.LCA({act: qty}, method)
    lca.lci()
    lca.lcia()
    return lca.score

dbs = config[0]["databases"]


print("Running LCA...")

with open(RESULTS_PATH / "results.txt", "w") as f:
    for lca_setup in config:
        f.write(str(run_lca(lca_setup)))

