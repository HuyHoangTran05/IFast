"""Ngày nghiệp vụ theo giờ Việt Nam.

`date.today()` lấy theo múi giờ của máy chủ. Máy chủ chạy UTC thì "hôm nay"
của hệ thống lệch 7 tiếng so với "hôm nay" của khách — một ưu đãi bắt đầu ngày
10/02 sẽ chỉ có hiệu lực từ 7 giờ sáng ngày 10/02 giờ Việt Nam, và một đơn đặt
lúc 23 giờ sẽ bị ghi sang ngày hôm trước.

Đây là sản phẩm bán hàng ở Việt Nam, nên ngày nghiệp vụ là ngày ở Việt Nam.
"""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

BUSINESS_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


def today() -> date:
    """Ngày hôm nay theo giờ Việt Nam, không phải theo giờ máy chủ."""
    return datetime.now(BUSINESS_TIMEZONE).date()
