import re
from pydantic import BaseModel,EmailStr,Field,field_validator
RESERVED={'www','api','admin','app','mail','support','billing','login','register','dashboard','static','assets','cdn','status','help','docs','shulepulse'}
class SchoolRegisterRequest(BaseModel):
    school_name:str=Field(min_length=2,max_length=255); slug:str=Field(min_length=3,max_length=100)
    first_name:str=Field(min_length=1,max_length=100); last_name:str=Field(min_length=1,max_length=100)
    email:EmailStr|None=None; phone:str|None=Field(default=None,max_length=30); password:str=Field(min_length=8,max_length=128)
    @field_validator('slug')
    @classmethod
    def validate_slug(cls,v):
        v=v.strip().lower()
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',v): raise ValueError('Use lowercase letters, numbers and hyphens only')
        if v in RESERVED: raise ValueError('That school handle is reserved')
        return v
