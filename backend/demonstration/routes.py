from fastapi import APIRouter,Depends,Request,HTTPException
from fastapi.routing import APIRoute
from backend.api import routes as original
from backend.models.schemas import ExperimentRequest
from backend.demonstration.registration import public_status


def select_study(request:Request):
    request.state.dataset_store=request.app.state.demonstration_store
    request.state.is_demonstration=True


router=APIRouter(prefix='/api/demonstrations',dependencies=[Depends(select_study)])


@router.get('/study')
def study():return public_status()


@router.post('/cases/{case_id}/experiment',status_code=202)
def experiment(case_id:str,request:Request,body:ExperimentRequest):
    if body.intervention and body.intervention.value not in ['heal_interior_vacancy','smooth_surface_notch']:raise HTTPException(422,'Only the two preregistered geometric interventions are allowed')
    if body.parameters.model_dump(exclude_none=True):raise HTTPException(422,'Registered physical protocol is fixed')
    return original.experiment(case_id,request,body)


for route in original.router.routes:
    if not isinstance(route,APIRoute) or route.path in ['/api/health','/api/benchmarks/evaluate','/api/cases/{case_id}/experiment']:continue
    router.add_api_route(route.path.removeprefix('/api'),route.endpoint,methods=sorted(route.methods),status_code=route.status_code,name='demonstration_'+route.name)
