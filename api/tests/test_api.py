"""Test mức HTTP, chạy trên dữ liệu seed thật của VF 2."""

from __future__ import annotations


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_lay_thong_so_vf2_dung_kieu_du_lieu(client):
    """`ai/` đọc đúng schema này — sai kiểu là sai câu trả lời cho khách."""
    body = client.get("/catalog/models/VF2").json()
    assert body["name"] == "VinFast VF 2"
    assert body["seats"] == 4
    spec = body["trims"][0]["spec"]
    assert spec["range_nedc_km"] == 210
    assert spec["max_power_w"] == 30_000
    assert spec["max_torque_nm"] == 65
    assert spec["fast_charge_minutes"] == 34
    assert isinstance(spec["range_nedc_km"], int)


def test_dong_xe_khong_ton_tai_tra_404(client):
    assert client.get("/catalog/models/VF999").status_code == 404


def test_du_toan_lan_banh_ha_noi(client):
    r = client.get(
        "/pricing/on-road",
        params={"trim_id": 1, "province_code": "HN", "as_of": "2026-06-01"},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["vehicle_price_vnd"] == 188_000_000
    assert body["discount_vnd"] == 9_400_000  # ưu đãi ra mắt
    assert body["total_vnd"] == sum(i["amount_vnd"] for i in body["items"])
    assert [p["code"] for p in body["promotions"]] == ["VF2-LAUNCH"]


def test_cung_xe_khac_tinh_ra_tong_khac(client):
    params = {"trim_id": 1, "as_of": "2026-06-01"}
    hn = client.get("/pricing/on-road", params={**params, "province_code": "HN"}).json()
    hcm = client.get("/pricing/on-road", params={**params, "province_code": "HCM"}).json()
    assert hn["total_vnd"] != hcm["total_vnd"]


def test_tinh_chua_ho_tro_tra_404_chu_khong_tra_gia_bang_gia_xe(client):
    r = client.get(
        "/pricing/on-road",
        params={"trim_id": 1, "province_code": "DN", "as_of": "2026-06-01"},
    )
    assert r.status_code == 404


def test_thue_pin_ra_gia_khac_va_co_phi_hang_thang(client):
    kem = client.get(
        "/pricing/on-road",
        params={"trim_id": 1, "province_code": "HN", "as_of": "2026-06-01"},
    ).json()
    thue = client.get(
        "/pricing/on-road",
        params={
            "trim_id": 1,
            "province_code": "HN",
            "as_of": "2026-06-01",
            "ownership_model": "battery_lease",
        },
    ).json()
    assert kem["monthly_battery_fee_vnd"] is None
    assert thue["monthly_battery_fee_vnd"] == 1_400_000
    assert kem["total_vnd"] != thue["total_vnd"]


def test_bieu_phi_2027_lam_tong_tang(client):
    """Sau 01/03/2027 lệ phí trước bạ về 6% theo dòng có ngày hiệu lực trong seed."""
    truoc = client.get(
        "/pricing/on-road",
        params={"trim_id": 1, "province_code": "HN", "as_of": "2026-06-01"},
    ).json()
    sau = client.get(
        "/pricing/on-road",
        params={"trim_id": 1, "province_code": "HN", "as_of": "2027-06-01"},
    ).json()
    assert sau["total_vnd"] > truoc["total_vnd"]


def test_uu_dai_mien_phi_sac_chua_chay_truoc_10_02_2026(client):
    truoc = client.get("/promotions", params={"as_of": "2026-02-09"}).json()
    sau = client.get("/promotions", params={"as_of": "2026-02-10"}).json()
    assert "FREE-CHARGING-2026" not in [p["code"] for p in truoc]
    assert "FREE-CHARGING-2026" in [p["code"] for p in sau]


def test_so_sanh_chi_phi_dan_duoc_ngay_cua_gia(client):
    body = client.get(
        "/pricing/running-cost",
        params={
            "monthly_km": 1000,
            "ev_consumption_kwh_per_100km_x10": 120,
            "ice_consumption_litres_per_100km_x10": 65,
            "as_of": "2026-09-01",
        },
    ).json()
    assert body["fuel_price_as_of"] == "2026-08-27"
    assert body["monthly_saving_vnd"] > 0


def test_dat_coc_roi_doi_gia_khong_lam_doi_don(client):
    created = client.post(
        "/orders",
        json={
            "code": "DH-TEST-001",
            "trim_id": 1,
            "province_code": "HN",
            "deposit_vnd": 10_000_000,
            "as_of": "2026-06-01",
        },
    )
    assert created.status_code == 201
    total = created.json()["total_vnd"]

    again = client.get("/orders/DH-TEST-001").json()
    assert again["total_vnd"] == total
    assert again["price_snapshot"]["as_of"] == "2026-06-01"
    assert again["status"] == "deposit_pending"


def test_tien_coc_lon_hon_gia_tri_don_bi_tu_choi(client):
    r = client.post(
        "/orders",
        json={
            "code": "DH-TEST-002",
            "trim_id": 1,
            "province_code": "HN",
            "deposit_vnd": 999_000_000_000,
            "as_of": "2026-06-01",
        },
    )
    assert r.status_code == 422
