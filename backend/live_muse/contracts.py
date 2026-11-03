from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,model_validator
Repair=Literal['heal_interior_vacancy','smooth_surface_notch']

class Bounded(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)

class Mechanism(Bounded):
    intervention:Repair
    title:str=Field(min_length=1,max_length=160)
    mechanism:str=Field(min_length=1,max_length=1200)
    evidence:list[str]=Field(min_length=1,max_length=8)
    missing_evidence:str=Field(max_length=1200)
    predicted_recovery_pct:float=Field(ge=-100,le=300)
    confidence:float=Field(ge=0,le=1)

class Hypotheses(Bounded):
    hypotheses:list[Mechanism]=Field(min_length=2,max_length=2)
    @model_validator(mode='after')
    def competing(self):
        if len({x.intervention for x in self.hypotheses})!=2:raise ValueError('Both registered repairs required')
        return self

class Choice(Bounded):
    intervention:Repair
    information_gain:float=Field(ge=0,le=1)
    risk:float=Field(ge=0,le=1)
    rationale:str=Field(min_length=1,max_length=1600)

class Planning(Bounded):
    choices:list[Choice]=Field(min_length=2,max_length=2)
    @model_validator(mode='after')
    def competing(self):
        if len({x.intervention for x in self.choices})!=2:raise ValueError('Both repairs must remain available')
        return self

class Belief(Bounded):
    intervention:Repair
    confidence:float=Field(ge=0,le=1)
    predicted_recovery_pct:float=Field(ge=-100,le=300)
    explanation:str=Field(min_length=1,max_length=2000)
    evidence_ids:list[str]=Field(min_length=1,max_length=2)

class Revision(Bounded):
    beliefs:list[Belief]=Field(min_length=2,max_length=2)
    revision:str=Field(min_length=1,max_length=3000)
    @model_validator(mode='after')
    def competing(self):
        if len({x.intervention for x in self.beliefs})!=2:raise ValueError('Both beliefs required')
        return self
