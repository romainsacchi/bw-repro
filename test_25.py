from bw_repro.recordtools.recorder import record

import bw2data, bw2io

def test():
    import bw2calc as bwc

    log_config = {"output_path": "outputs", "name": "experiment"}
    bwc = record(bwc, log_config)

    # bw2data.projects.set_current("bw25")
    bw2data.projects.set_current("ABM_SN")
    meth = bw2data.methods.random()
    # process = bw2data.Database("ei39").random()
    process = bw2data.Database("ecoinvent36").random()

    def do_random_lca():
        fu = {process: 1}
        lca = bwc.LCA(fu, meth)
        lca.lci()
        lca.lcia()

    def do_random_mlca():
        fu = {process: 1}
        mlca = bwc.MonteCarloLCA(fu, meth, seed=0)
        for i in range(3):
            next(mlca)
        mlca.record()
    #
    for _ in range(0, 2):
        do_random_lca()
        do_random_mlca()

    bwc.export_record()

if __name__ == "__main__":
    test()
