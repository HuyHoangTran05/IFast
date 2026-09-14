from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.db import get_session
from api.pricing.models import (
    ElectricityPriceReference,
    FuelPriceReference,
    FuelType,
    OwnershipModel,
    PriceBookEntry,
    RegistrationFeeSchedule,
)
from api.pricing.service import (
    PricingUnavailable,
    compare_running_cost,
    quote_on_road_cost,
    resolve_price,
)
from api.promotions.models import Promotion
from api.promotions.service import resolve_promotions

router = APIRouter(prefix="/pricing", tags=["pricing"])


class LineItemOut(BaseModel):
    code: str
    label: str
    amount_vnd: int


class AppliedPromotionOut(BaseModel):
    code: str
    name: str
    discount_vnd: int
    terms_url: str | None


class OnRoadQuoteOut(BaseModel):
    as_of: date
    province_code: str
    ownership_model: str
    vehicle_price_vnd: int
    discount_vnd: int
    monthly_battery_fee_vnd: int | None
    items: list[LineItemOut]
    promotions: list[AppliedPromotionOut]
    total_vnd: int


@router.get("/on-road", response_model=OnRoadQuoteOut)
def on_road_quote(
    trim_id: int,
    province_code: str,
    ownership_model: OwnershipModel = OwnershipModel.BATTERY_INCLUDED,
    as_of: date | None = Query(
        default=None,
        description="Mốc thời gian tính giá. Bỏ trống thì lấy hôm nay; báo giá "
        "cho một đơn cũ phải truyền đúng ngày của đơn đó.",
    ),
    session: Session = Depends(get_session),
) -> OnRoadQuoteOut:
    as_of = as_of or date.today()
    prices = list(session.scalars(select(PriceBookEntry)))
    schedules = list(session.scalars(select(RegistrationFeeSchedule)))
    promotions = list(session.scalars(select(Promotion)))

    try:
        price = resolve_price(prices, trim_id, ownership_model, as_of)
        outcome = resolve_promotions(
            promotions,
            trim_id=trim_id,
            province_code=province_code,
            ownership_model=ownership_model.value,
            list_price_vnd=price.list_price_vnd,
            as_of=as_of,
        )
        quote = quote_on_road_cost(
            price_entry=price,
            fee_schedules=schedules,
            province_code=province_code,
            as_of=as_of,
            discount_vnd=outcome.total_discount_vnd,
        )
    except PricingUnavailable as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return OnRoadQuoteOut(
        as_of=quote.as_of,
        province_code=quote.province_code,
        ownership_model=quote.ownership_model.value,
        vehicle_price_vnd=quote.vehicle_price_vnd,
        discount_vnd=quote.discount_vnd,
        monthly_battery_fee_vnd=quote.monthly_battery_fee_vnd,
        items=[LineItemOut(**i.__dict__) for i in quote.items],
        promotions=[AppliedPromotionOut(**p.__dict__) for p in outcome.applied],
        total_vnd=quote.total_vnd,
    )


class RunningCostOut(BaseModel):
    as_of: date
    monthly_km: int
    ev_monthly_cost_vnd: int
    ice_monthly_cost_vnd: int
    monthly_saving_vnd: int
    electricity_price_as_of: date
    fuel_price_as_of: date


@router.get("/running-cost", response_model=RunningCostOut)
def running_cost(
    monthly_km: int,
    ev_consumption_kwh_per_100km_x10: int,
    ice_consumption_litres_per_100km_x10: int,
    fuel_type: FuelType = FuelType.GASOLINE,
    as_of: date | None = None,
    session: Session = Depends(get_session),
) -> RunningCostOut:
    as_of = as_of or date.today()
    try:
        result = compare_running_cost(
            monthly_km=monthly_km,
            ev_consumption_kwh_per_100km_x10=ev_consumption_kwh_per_100km_x10,
            ice_consumption_litres_per_100km_x10=ice_consumption_litres_per_100km_x10,
            electricity_prices=list(session.scalars(select(ElectricityPriceReference))),
            fuel_prices=list(session.scalars(select(FuelPriceReference))),
            fuel_type=fuel_type,
            as_of=as_of,
        )
    except PricingUnavailable as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return RunningCostOut(
        as_of=result.as_of,
        monthly_km=result.monthly_km,
        ev_monthly_cost_vnd=result.ev_monthly_cost_vnd,
        ice_monthly_cost_vnd=result.ice_monthly_cost_vnd,
        monthly_saving_vnd=result.monthly_saving_vnd,
        electricity_price_as_of=result.electricity_price_as_of,
        fuel_price_as_of=result.fuel_price_as_of,
    )
