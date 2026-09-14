from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.clock import today
from api.core.db import get_session
from api.orders.models import Order
from api.orders.service import create_order
from api.pricing.models import OwnershipModel, PriceBookEntry, RegistrationFeeSchedule
from api.pricing.service import PricingUnavailable, quote_on_road_cost, resolve_price
from api.promotions.models import Promotion
from api.promotions.service import resolve_promotions

router = APIRouter(prefix="/orders", tags=["orders"])


class CreateOrderIn(BaseModel):
    code: str
    trim_id: int
    province_code: str
    ownership_model: OwnershipModel = OwnershipModel.BATTERY_INCLUDED
    deposit_vnd: int
    as_of: date | None = None


class OrderOut(BaseModel):
    code: str
    status: str
    channel: str
    trim_id: int
    province_code: str
    quoted_on: date
    total_vnd: int
    deposit_vnd: int
    price_snapshot: dict


@router.post("", response_model=OrderOut, status_code=201)
def create(payload: CreateOrderIn, session: Session = Depends(get_session)) -> OrderOut:
    """Tạo đơn và khoá snapshot.

    Sau lời gọi này, đơn không còn phụ thuộc vào bảng giá. Bảng giá đổi ngày
    mai không làm đổi con số trong đơn.
    """
    as_of = payload.as_of or today()
    try:
        price = resolve_price(
            list(session.scalars(select(PriceBookEntry))),
            payload.trim_id,
            payload.ownership_model,
            as_of,
        )
        outcome = resolve_promotions(
            list(session.scalars(select(Promotion))),
            trim_id=payload.trim_id,
            province_code=payload.province_code,
            ownership_model=payload.ownership_model.value,
            list_price_vnd=price.list_price_vnd,
            as_of=as_of,
        )
        quote = quote_on_road_cost(
            price_entry=price,
            fee_schedules=list(session.scalars(select(RegistrationFeeSchedule))),
            province_code=payload.province_code,
            as_of=as_of,
            discount_vnd=outcome.total_discount_vnd,
        )
        order = create_order(
            code=payload.code,
            trim_id=payload.trim_id,
            quote=quote,
            promotions=outcome,
            deposit_vnd=payload.deposit_vnd,
        )
    except PricingUnavailable as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    session.add(order)
    session.commit()
    session.refresh(order)
    return _out(order)


@router.get("/{code}", response_model=OrderOut)
def get_order(code: str, session: Session = Depends(get_session)) -> OrderOut:
    order = session.scalar(select(Order).where(Order.code == code))
    if order is None:
        raise HTTPException(status_code=404, detail=f"không có đơn {code}")
    return _out(order)


def _out(order: Order) -> OrderOut:
    return OrderOut(
        code=order.code,
        status=order.status.value,
        channel=order.channel.value,
        trim_id=order.trim_id,
        province_code=order.province_code,
        quoted_on=order.quoted_on,
        total_vnd=order.total_vnd,
        deposit_vnd=order.deposit_vnd,
        price_snapshot=order.price_snapshot,
    )
