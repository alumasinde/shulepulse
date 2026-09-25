import json
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file='.env',extra='ignore')
    app_name:str='ShulePulse'; environment:str='development'; debug:bool=False
    secret_key:str=Field(min_length=32); access_token_expire_minutes:int=60
    cookie_name:str='shulepulse_access'; cookie_secure:bool=False; cookie_samesite:str='lax'
    database_url:str; root_domain:str='shulepulse.localhost'
    allowed_hosts:str='localhost,127.0.0.1,*.localhost,shulepulse.localhost'
    default_school_settings:str='{"branding":{"primary_color":"#166534","secondary_color":"#facc15"},"grading":{},"reports":{"show_position":false,"show_teacher_comments":true}}'
    @property
    def allowed_host_list(self): return [x.strip() for x in self.allowed_hosts.split(',') if x.strip()]
    @property
    def default_settings_dict(self): return json.loads(self.default_school_settings)
@lru_cache
def get_settings(): return Settings()
settings=get_settings()
