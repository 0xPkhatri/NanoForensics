"""Study records retain failed runs as immutable evidence; no outcome-selected retry."""
from backend.storage.db import Store
from backend.models.schemas import SimulationSummary
from backend.simulation.numpy_md_fallback import content_hash
from backend.simulation.lammps_runner import engine_capabilities


def run_key(specimen):
    return content_hash({'input':specimen.model_dump(),'solver_version':'sflj-1.1','engine':engine_capabilities()})


class DemonstrationStore(Store):
    def save_result(self,key,result):
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO results VALUES(?,?,?)',(key,result.sim_id,result.model_dump_json()))

    def retain_frozen_baselines(self):
        for case_id in self.case_ids():
            for raw in self.public(case_id).baseline_simulation.replicate_results:
                specimen=self.specimen(case_id);specimen.protocol.seed=raw['seed']
                self.save_result(run_key(specimen),SimulationSummary.model_validate(raw))
