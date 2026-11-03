from fastapi import APIRouter,Depends,Request
from fastapi.routing import APIRoute
from backend.api import routes as original
from backend.demonstration.routes import experiment
from backend.demonstration.registration import public_status


def select_live(request:Request):
    request.state.dataset_store=request.app.state.live_muse_store
    request.state.is_demonstration=True


router=APIRouter(prefix='/api/live-muse',dependencies=[Depends(select_live)])


@router.get('/study')
def study():
    return {**public_status(),'rehearsal':True,'inference_policy':'Post-study AI rehearsal; operation-local live/fallback provenance. Frozen study decisions unchanged.'}


router.add_api_route('/cases/{case_id}/experiment',experiment,methods=['POST'],status_code=202)
for route in original.router.routes:
    if not isinstance(route,APIRoute) or route.path in ['/api/health','/api/benchmarks/evaluate','/api/cases/{case_id}/experiment']:continue
    router.add_api_route(route.path.removeprefix('/api'),route.endpoint,methods=sorted(route.methods),status_code=route.status_code,name='live_muse_'+route.name)
