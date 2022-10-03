from bw_repro.recordtools.recorder import record

def test():
    import brightway2 as bw
    log_config = {
        "logger_path": "config/",
        "name": "experiment"
    }
    bw = record(bw, log_config)

    bw.projects.set_current("ABM_SN")
    meth = bw.methods.random()
    process = bw.Database('test_db').random()

    def do_random_lca():
        fu = {process: 1}
        lca = bw.LCA(fu, meth)
        lca.lci()
        lca.lcia()

    def do_random_mlca():
        fu = {process: 1}
        mlca = bw.MonteCarloLCA(fu, meth, seed=0)
        for i in range(3):
            next(mlca)
        mlca.record()

    for _ in range(0, 5):
        do_random_lca()
        do_random_mlca()

    bw.export_record(log_config)

if __name__ == "__main__":
    test()