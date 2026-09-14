from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.catalog.models import Color, Spec, Trim, VehicleModel
from api.core.db import get_session

router = APIRouter(prefix="/catalog", tags=["catalog"])


class SpecOut(BaseModel):
    """Thông số có kiểu. `ai/` đọc đúng schema này, không đọc văn bản mô tả."""

    motor_count: int | None = None
    max_power_w: int | None = None
    max_torque_nm: int | None = None
    range_nedc_km: int | None = None
    range_per_charge_km: int | None = None
    fast_charge_minutes: int | None = None
    top_speed_kmh: int | None = None
    drivetrain: str | None = None


class TrimOut(BaseModel):
    id: int
    code: str
    name: str
    spec: SpecOut | None = None


class ColorOut(BaseModel):
    code: str
    name: str
    exterior: bool


class ModelOut(BaseModel):
    id: int
    code: str
    name: str
    category: str
    segment: str | None
    seats: int | None
    trims: list[TrimOut]
    colors: list[ColorOut]


@router.get("/models", response_model=list[ModelOut])
def list_models(session: Session = Depends(get_session)) -> list[ModelOut]:
    models = session.scalars(select(VehicleModel)).all()
    return [_to_out(session, m) for m in models]


@router.get("/models/{code}", response_model=ModelOut)
def get_model(code: str, session: Session = Depends(get_session)) -> ModelOut:
    model = session.scalar(select(VehicleModel).where(VehicleModel.code == code))
    if model is None:
        raise HTTPException(status_code=404, detail=f"không có dòng xe {code}")
    return _to_out(session, model)


def _to_out(session: Session, model: VehicleModel) -> ModelOut:
    trims = session.scalars(select(Trim).where(Trim.model_id == model.id)).all()
    colors = session.scalars(select(Color).where(Color.model_id == model.id)).all()
    out_trims = []
    for t in trims:
        spec = session.scalar(select(Spec).where(Spec.trim_id == t.id))
        out_trims.append(
            TrimOut(
                id=t.id,
                code=t.code,
                name=t.name,
                spec=SpecOut.model_validate(spec, from_attributes=True) if spec else None,
            )
        )
    return ModelOut(
        id=model.id,
        code=model.code,
        name=model.name,
        category=model.category.value,
        segment=model.segment,
        seats=model.seats,
        trims=out_trims,
        colors=[ColorOut.model_validate(c, from_attributes=True) for c in colors],
    )
