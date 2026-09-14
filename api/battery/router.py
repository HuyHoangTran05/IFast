from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.battery.models import BatteryAsset, BatteryListPrice, BatteryWarrantyPolicy
from api.battery.service import BatteryPolicyUnavailable, compute_compensation
from api.core.db import get_session

router = APIRouter(prefix="/battery", tags=["battery"])


class CompensationOut(BaseModel):
    """Số tiền đòi khách trả, nên trả kèm toàn bộ căn cứ đã dùng."""

    compensation_vnd: int
    list_price_vnd: int
    list_price_as_of: date
    months_used: int
    warranty_months: int
    warranty_policy_as_of: date
    floor_applied: bool


@router.get("/assets/{serial}/compensation", response_model=CompensationOut)
def compensation_for_asset(
    serial: str,
    incident_on: date,
    session: Session = Depends(get_session),
) -> CompensationOut:
    asset = session.scalar(select(BatteryAsset).where(BatteryAsset.serial == serial))
    if asset is None:
        raise HTTPException(status_code=404, detail=f"không có pin số {serial}")

    try:
        result = compute_compensation(
            formed_on=asset.formed_on,
            incident_on=incident_on,
            list_prices=list(session.scalars(select(BatteryListPrice))),
            warranty_policies=list(session.scalars(select(BatteryWarrantyPolicy))),
            trim_id=asset.trim_id,
        )
    except BatteryPolicyUnavailable as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return CompensationOut(**result.__dict__)
