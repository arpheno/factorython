from pydantic import BaseModel


class Solver(BaseModel):
    time_limit: int
