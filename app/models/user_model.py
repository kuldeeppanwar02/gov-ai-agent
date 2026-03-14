from pydantic import BaseModel
from typing import Optional

class UserProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    income: Optional[float] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    category: Optional[str] = None   # SC / ST / OBC / General
    disability: Optional[bool] = None
