import bw2data
import bw2io

import bw2calc
from eidl import get_ecoinvent, eidlstorage
from pathlib import Path
import json

CONFIG_PATH = Path(__file__).parent.parent / "config"
RESOURCES_PATH = Path(__file__).parent.parent / "resources"
RESULTS_PATH = Path(__file__).parent.parent / "results"

with open(CONFIG_PATH / "config.json") as f:
    config = json.load(f)

eidlstorage.clear_stored_dbs()

print("Creating project...")

bw2data.projects.set_current("default")

print("Installing biosphere...")
print(bw2data.databases)
bw2io.bw2setup()


def install_dbs(db):

    if db["available in resources"]:
        print("Installing database from resources...")
        # import local db
        print(f"Importing {db['name']}...")
        bw2io.BW2Package.import_file(RESOURCES_PATH / db["file name"])

    else:
        if "ecoinvent" in db["name"]:
            name = db["name"]
            ver = db["version"]
            system_model = db["system model"]
            if f"{name} {system_model} {ver}" not in bw2data.databases:
                # download ei from website
                get_ecoinvent(
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

    # checking that all databases are installed
    for db in lca_setup["calc_config"]["databases"]:
        for dependency in db["depends on"]:
            if dependency not in bw2data.databases:
                print(f"Installing {dependency}...")
                install_dbs(
                    [
                        d
                        for d in lca_setup["calc_config"]["databases"]
                        if d["name"] == dependency
                    ][0]
                )

    # fetch activity
    # it should be in the form of {act: 1}
    print("Running LCA...")
    acts = []
    for calculation in lca_setup["demand"]:
        db, code, qty = calculation.values()
        act = bw2data.get_activity((db, code))
        acts.append({act: qty})

    # fetch method
    method = tuple(lca_setup["method"])

    # run lca
    bw2calc.calculation_setups["calculation setup"] = {
        "ia": method,
        "inv": acts,
    }
    mlca = bw2calc.multiLCA("calculation setup")
    return mlca.results


with open(RESULTS_PATH / "results.txt", "w") as f:
    for lca_setup in config:
        f.write(str(run_lca(lca_setup)))
