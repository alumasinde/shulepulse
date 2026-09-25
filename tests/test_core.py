from app.core.security import hash_password,verify_password
from app.core.tenant import extract_tenant_slug
def test_password_roundtrip():
    h=hash_password('StrongPassword123!'); assert h!='StrongPassword123!'; assert verify_password('StrongPassword123!',h); assert not verify_password('wrong',h)
def test_tenant_slug():
    assert extract_tenant_slug('majimazuri.shulepulse.localhost:8000')=='majimazuri'; assert extract_tenant_slug('shulepulse.localhost:8000') is None
