import os
from pathlib import Path
from backend.config import ROOT
from backend.demonstration.storage import DemonstrationStore
from demonstrations.restore import restore_public

LIVE_DB=Path(os.getenv('NANO_LIVE_MUSE_DB',str(ROOT/'runtime/live-muse/rehearsal.db')))


def initialize(store):
    result=restore_public(store=store)
    if result['status']=='RESTORED_PUBLIC_MD_EVIDENCE':
        # Published scientific decisions are not AI-generated rehearsal decisions.
        with store.connect() as db:db.execute('DELETE FROM states')
    return result
