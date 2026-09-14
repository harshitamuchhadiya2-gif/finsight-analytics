from fastapi import Depends, HTTPException, Header
from app.db.session import get_db

def get_current_user(authorization: str|None=Header(default=None), db=Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401,"Authentication required")
    from app.core.security import decode_token
    try: uid=decode_token(authorization.split(" ",1)[1])["sub"]
    except Exception: raise HTTPException(401,"Invalid or expired token")
    user=db.users.find_one({"_id":uid})
    if not user: raise HTTPException(401,"User not found")
    return user

def require_admin(user=Depends(get_current_user)):
    if user.get("role")!="admin": raise HTTPException(403,"Admin access required")
    return user
