from pydantic import BaseModel

class NSWCarparkParam(BaseModel):
    facility: int
    class Config:
        frozen = True  # Makes instances hashable
