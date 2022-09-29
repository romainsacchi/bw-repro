import bw2io, bw2data, bw2calc
import eidl
from pathlib import Path
import json

CONFIG_PATH = Path(__file__).parent.parent / "config"
RESOURCES_PATH = Path(__file__).parent.parent / "resources"
RESULTS_PATH = Path(__file__).parent.parent / "results"

print("Creating project...")

bw2data.projects.set_current("example")

print("Installing biosphere...")

bw2io.bw2setup()

with open(CONFIG_PATH / "config.json") as f:
    config = json.load(f)


def install_dbs(dbs):
    for db in dbs:
        print(f"Importing {db['name']}...")
        if db["available in resources"]:
            if all(i in bw2data.databases for i in db["depends on"]):
                # import local db
                bw2io.BW2Package.import_file(
                    RESOURCES_PATH / db["file name"]
                )
        else:
            if db["name"] == "ecoinvent":
                name = db["name"]
                ver = db["version"]
                system_model = db["system model"]
                if f"{name} {ver} {system_model}" not in bw2data.databases:
                    # download ei from website
                    eidl.get_ecoinvent(
                        db_name=f"{name} {ver} {system_model}",
                        auto_write=True,
                        version=ver,
                        system_model=system_model,
                    )
                else:
                    print(f"{name} {ver} {system_model} already present.")
            else:
                raise ValueError("Not implemented yet")

def run_lca(config):

    # fetch activity
    # it should be in teh form of {act: 1}
    act = bw2data.get_activity(config["demand"])
    # fetch method
    method = bw2data.Method(config["method"])
    # run lca
    lca = bw2calc.LCA({act: 1}, method)
    lca.lci()
    lca.lcia()
    return lca.score

dbs = config[0]["databases"]

print(dbs)

install_dbs(dbs)

print("Running LCA...")
with open(RESULTS_PATH / "result.txt", "w") as f:
    f.write(str(run_lca(config)))

