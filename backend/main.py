from contextlib import asynccontextmanager
import asyncio
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import ROOT
from backend.storage.db import Store
from backend.agents.muse_agent import verify_llm_connection
from backend.simulation.lammps_runner import engine_capabilities
from backend.api.jobs import JobManager
from backend.api.routes import router


@asynccontextmanager
async def lifespan(app):
    app.state.store=Store()
    app.state.telemetry=await asyncio.to_thread(verify_llm_connection)
    app.state.capabilities=await asyncio.to_thread(engine_capabilities)
    calibration=ROOT/'runtime/calibration.json'
    if not calibration.exists():
        from benchmarks.calibrate_runtime import calibrate
        # Complete-run startup calibration off the event loop.
        app.state.calibration=await asyncio.to_thread(calibrate)
    else: app.state.calibration=json.loads(calibration.read_text())
    app.state.jobs=JobManager(app.state.store);app.state.jobs.start()
    yield
    app.state.jobs.close()


app=FastAPI(title='NanoForensics',version='1.0.0',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:3000','http://127.0.0.1:3000'],allow_methods=['GET','POST'],allow_headers=['Content-Type','X-Admin-Token'])
app.include_router(router)
