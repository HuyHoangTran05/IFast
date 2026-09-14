from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.clock import today
from api.core.db import get_session
from api.core.effective import is_effective_on
from api.promotions.models import Promotion

router = APIRouter(prefix="/promotions", tags=["promotions"])


class PromotionOut(BaseModel):
    code: str
    name: str
    kind: str
    terms_url: str | None
    effective_from: date
    effective_to: date | None


@router.get("", response_model=list[PromotionOut])
def list_promotions(
    as_of: date | None = None,
    session: Session = Depends(get_session),
) -> list[PromotionOut]:
    """Ưu đãi còn hiệu lực tại một mốc thời gian.

    Mặc định là hôm nay, nhưng tra cứu lại một đơn cũ phải truyền đúng ngày của
    đơn — ưu đãi đã hết hạn vẫn phải giải thích được vì sao từng được áp.
    """
    as_of = as_of or today()
    promos = [p for p in session.scalars(select(Promotion)) if is_effective_on(p, as_of)]
    return [
        PromotionOut(
            code=p.code,
            name=p.name,
            kind=p.kind.value,
            terms_url=p.terms_url,
            effective_from=p.effective_from,
            effective_to=p.effective_to,
        )
        for p in promos
    ]
