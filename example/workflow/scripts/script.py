import bw2io, bw2data, bw2calc
import eidl
from pathlib import Path
import json

CONFIG_PATH = Path(__file__).parent.parent / "config"
RESOURCES_PATH = Path(__file__).parent.parent / "resources"
RESULTS_PATH = Path(__file__).parent.parent / "results"

print(CONFIG_PATH)

bw2data.projects.set_current("example")
bw2io.bw2setup()

with open(CONFIG_PATH / "config.json") as f:
    config = json.load(f)

# config["databases"] = [
#     {
#         "name": "ecoinvent",
#         "version": "3.7",
#         "system model": "cut-off",
#         "available in resources": False,
#     },
#     {
#         "name": "my db",
#         "version": None,
#         "system model": None,
#         "available in resources": True,
#         "file name": "my db.bw2datapackage",
#         "depends on": ["ecoinvent"],
#     },
# ]


def install_dbs(dbs):
    for db in dbs:
        if db["available in resources"]:
            if all(i in bw2data.databases for i in db["depends on"]):
                # import local db
                bw2io.BW2Package.import_file(
                    RESOURCES_PATH / db["file name"]
                )
        else:
            if db["ecoinvent"] == "ecoinvent":
                # download ei from website
                eidl.get_ecoinvent()
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

dbs = config["databases"]
install_dbs(dbs)

with open(RESULTS_PATH / "result.txt", "w") as f:
    f.write(str(run_lca(config)))

