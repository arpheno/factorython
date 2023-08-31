from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, Extra


class Signal(BaseModel):
    type: str
    name: str

    class Config:
        extra = Extra.allow


class Icon(BaseModel):
    signal: Signal
    index: int
    class Config:
        extra = Extra.allow


class RequestFilter(BaseModel):
    index: int
    name: str
    count: int
    class Config:
        extra = Extra.allow


class InfinitySettings(BaseModel):
    class Config:
        extra = Extra.allow


class RedItem(BaseModel):
    entity_id: int
    class Config:
        extra = Extra.allow


class Field1(BaseModel):
    class Config:
        extra = Extra.allow


class Connections(BaseModel):
    field_1: Field1 = Field(..., alias='1')
    class Config:
        extra = Extra.allow


class FirstSignal(BaseModel):
    type: str
    name: str
    class Config:
        extra = Extra.allow


class CircuitCondition(BaseModel):
    first_signal: Optional[FirstSignal]=None
    constant: Optional[int]=None
    comparator: str
    class Config:
        extra = Extra.allow


class ControlBehavior(BaseModel):
    circuit_condition: Optional[CircuitCondition]=None
    class Config:
        extra = Extra.allow


class DropPosition(BaseModel):
    x: float
    y: float
    class Config:
        extra = Extra.allow


class PickupPosition(BaseModel):
    x: int
    y: float
    class Config:
        extra = Extra.allow


class Position1(BaseModel):
    x: int
    y: int
    class Config:
        extra = Extra.allow
