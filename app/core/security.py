from datetime import datetime,timedelta,timezone
import bcrypt,jwt
from app.core.config import settings
ALGORITHM='HS256'
def hash_password(password:str)->str: return bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
def verify_password(password:str,password_hash:str)->bool:
    try:return bcrypt.checkpw(password.encode(),password_hash.encode())
    except (ValueError,TypeError):return False
def create_access_token(*,user_id:int,school_id:int)->str:
    now=datetime.now(timezone.utc); payload={'sub':str(user_id),'school_id':school_id,'iat':now,'exp':now+timedelta(minutes=settings.access_token_expire_minutes),'type':'access'}
    return jwt.encode(payload,settings.secret_key,algorithm=ALGORITHM)
def decode_access_token(token:str): return jwt.decode(token,settings.secret_key,algorithms=[ALGORITHM])
