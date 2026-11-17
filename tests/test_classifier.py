"""
Bộ kiểm thử tự động toàn diện (TC01 - TC60) cho Track A: Rule Engine.
Bao phủ 100% các test case trong docs/TEST_REPORT.md và các ca biên rà soát chéo.
"""
import copy
import itertools
import statistics
import time
import uuid
import pytest

from rule_engine.classifier import (
    REASON_MESSAGES,
    classify,
    clear_audit_logs,
    get_audit_logs,
)


def make_b0(**overrides):
    base = {
        "tuoi": 30,
        "huyet_ap_tam_thu": 120,
        "huyet_ap_tam_thu_nen": None,
        "co_di_nguyen_nghi_ngo": False,
        "di_nguyen_qua_duong_hit": False,
        "co_ton_thuong_da_niem_mac": False,
        "co_trieu_chung_ho_hap": False,
        "co_trieu_chung_tuan_hoan": False,
        "co_trieu_chung_tieu_hoa_nang": False,
    }
    base.update(overrides)
    return base


def make_p3(**overrides):
    base = make_b0(co_di_nguyen_nghi_ngo=True, co_trieu_chung_tuan_hoan=True)
    base.update(overrides)
    return base


def test_tc01_valid_full_9_fields():
    res = classify(make_b0())
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None
    assert res["ly_do"] == REASON_MESSAGES["THEO_DOI"]


def test_tc02_missing_tuoi():
    clear_audit_logs()
    data = make_p3()
    del data["tuoi"]
    res = classify(data)
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None
    assert res["ly_do"] == REASON_MESSAGES["INVALID_INPUT"]
    assert get_audit_logs()[-1]["Status"] == "INVALID_INPUT"


def test_tc03_missing_bool_branch_3a_and_3b():
    data_3a = make_p3()
    del data_3a["co_trieu_chung_ho_hap"]
    res_3a = classify(data_3a)
    assert res_3a["muc_do"] == "PHAN_VE"
    assert res_3a["rule_id"] == "R03-PV"

    data_3a_soc = make_p3(huyet_ap_tam_thu=80)
    del data_3a_soc["co_trieu_chung_ho_hap"]
    res_3a_soc = classify(data_3a_soc)
    assert res_3a_soc["muc_do"] == "SOC_PHAN_VE"
    assert res_3a_soc["rule_id"] == "R-SOC"

    data_3b = make_b0(co_di_nguyen_nghi_ngo=True)
    del data_3b["co_trieu_chung_ho_hap"]
    res_3b = classify(data_3b)
    assert res_3b["muc_do"] == "THEO_DOI"
    assert res_3b["rule_id"] is None
    assert res_3b["ly_do"] == REASON_MESSAGES["INVALID_INPUT"]


def test_tc04_missing_nullable_bp_keys_on_b0():
    data = make_b0()
    del data["huyet_ap_tam_thu"]
    del data["huyet_ap_tam_thu_nen"]
    res = classify(data)
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None
    assert res["ly_do"] == REASON_MESSAGES["THEO_DOI"]


@pytest.mark.parametrize("bad_bool", ["true", "false", 1, 0, 1.0, []])
def test_tc05_bool_wrong_type_and_null_no_downgrade(bad_bool):
    res_bad = classify(make_p3(co_trieu_chung_ho_hap=bad_bool))
    assert res_bad["muc_do"] == "THEO_DOI"
    assert res_bad["rule_id"] is None
    assert res_bad["ly_do"] == REASON_MESSAGES["INVALID_INPUT"]

    res_null_p3 = classify(make_p3(co_trieu_chung_ho_hap=None))
    assert res_null_p3["muc_do"] == "PHAN_VE"
    assert res_null_p3["rule_id"] == "R03-PV"


def test_tc06_tuoi_string():
    res = classify(make_p3(tuoi="30"))
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None
    assert res["ly_do"] == REASON_MESSAGES["INVALID_INPUT"]


@pytest.mark.parametrize("bool_age", [True, False])
def test_tc07_tuoi_boolean_rejected(bool_age):
    res = classify(make_p3(tuoi=bool_age))
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None
    assert res["ly_do"] == REASON_MESSAGES["INVALID_INPUT"]


@pytest.mark.parametrize("bad_bp", [True, False, 85.5, "85", [85]])
def test_tc08_bp_wrong_type_on_b0_and_p3(bad_bp):
    res_b0 = classify(make_b0(huyet_ap_tam_thu=bad_bp))
    assert res_b0["muc_do"] == "THEO_DOI"
    assert res_b0["rule_id"] is None
    assert res_b0["ly_do"] == REASON_MESSAGES["INVALID_INPUT"]

    res_p3 = classify(make_p3(huyet_ap_tam_thu=bad_bp))
    assert res_p3["muc_do"] == "PHAN_VE"
    assert res_p3["rule_id"] == "R03-PV"


def test_tc09_tuoi_negative():
    res = classify(make_p3(tuoi=-1))
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None
    assert res["ly_do"] == REASON_MESSAGES["INVALID_INPUT"]


@pytest.mark.parametrize(
    "extreme_age",
    [float("nan"), float("inf"), float("-inf"), 10**400, -(10**400), None],
)
def test_tc10_tuoi_nan_inf_and_huge_int_overflow(extreme_age):
    res = classify(make_p3(tuoi=extreme_age))
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None
    assert res["ly_do"] == REASON_MESSAGES["INVALID_INPUT"]


def test_tc11_unknown_field_sanitized_no_downgrade():
    clear_audit_logs()
    data = make_p3(ho_ten="Nguyen Van Test", cccd="001206000001")
    res = classify(data)
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R03-PV"
    assert "Nguyen Van Test" not in str(res)
    assert "ho_ten" not in str(res)
    assert "Nguyen Van Test" not in str(get_audit_logs())


def test_tc12_tuoi_int_valid():
    res = classify(make_p3(tuoi=30))
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R03-PV"


def test_tc13_tuoi_boundaries():
    for valid_age in (0, 0.0, 120, 120.0):
        res = classify(make_p3(tuoi=valid_age))
        assert res["muc_do"] == "PHAN_VE"
        assert res["rule_id"] == "R03-PV"

    for invalid_age in (-0.01, 120.01):
        res = classify(make_p3(tuoi=invalid_age))
        assert res["muc_do"] == "THEO_DOI"
        assert res["rule_id"] is None
        assert res["ly_do"] == REASON_MESSAGES["INVALID_INPUT"]


def test_tc14_bp_boundaries_1_to_300():
    assert classify(make_p3(huyet_ap_tam_thu=1))["muc_do"] == "SOC_PHAN_VE"
    assert classify(make_p3(huyet_ap_tam_thu=300))["muc_do"] == "PHAN_VE"
    assert classify(make_p3(huyet_ap_tam_thu=120, huyet_ap_tam_thu_nen=1))["muc_do"] == "PHAN_VE"
    res_nen300 = classify(make_p3(huyet_ap_tam_thu=120, huyet_ap_tam_thu_nen=300))
    assert res_nen300["muc_do"] == "SOC_PHAN_VE"
    assert res_nen300["rule_id"] == "R-SOC"

    for out_bp in (0, 301, -10):
        res_p3 = classify(make_p3(huyet_ap_tam_thu=out_bp))
        assert res_p3["muc_do"] == "PHAN_VE"
        assert res_p3["rule_id"] == "R03-PV"

        res_b0 = classify(make_b0(huyet_ap_tam_thu=out_bp))
        assert res_b0["muc_do"] == "THEO_DOI"
        assert res_b0["rule_id"] is None
        assert res_b0["ly_do"] == REASON_MESSAGES["INVALID_INPUT"]


def test_tc15_r01_da_and_hh():
    res = classify(make_b0(co_ton_thuong_da_niem_mac=True, co_trieu_chung_ho_hap=True))
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"


def test_tc16_r01_da_and_th():
    res = classify(make_b0(co_ton_thuong_da_niem_mac=True, co_trieu_chung_tuan_hoan=True))
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"


def test_tc17_r01_negative_only_da():
    res = classify(make_b0(co_ton_thuong_da_niem_mac=True))
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None


def test_tc18_r01_negative_no_da_with_hh_and_th():
    res = classify(make_b0(co_trieu_chung_ho_hap=True, co_trieu_chung_tuan_hoan=True))
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None


def test_tc19_r02_da_and_td():
    res = classify(
        make_b0(
            co_di_nguyen_nghi_ngo=True,
            co_ton_thuong_da_niem_mac=True,
            co_trieu_chung_tieu_hoa_nang=True,
        )
    )
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R02-PV"


def test_tc20_r02_with_inhalation_da_and_hh():
    res = classify(
        make_b0(
            co_di_nguyen_nghi_ngo=True,
            di_nguyen_qua_duong_hit=True,
            co_ton_thuong_da_niem_mac=True,
            co_trieu_chung_ho_hap=True,
        )
    )
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R02-PV"


def test_tc21_r02_negative_only_1_organ_td():
    res = classify(make_b0(co_di_nguyen_nghi_ngo=True, co_trieu_chung_tieu_hoa_nang=True))
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None


def test_tc22_r03_non_inhalation_hh():
    res = classify(
        make_b0(
            co_di_nguyen_nghi_ngo=True,
            di_nguyen_qua_duong_hit=False,
            co_trieu_chung_ho_hap=True,
        )
    )
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R03-PV"


def test_tc23_r03_only_th():
    res = classify(make_p3())
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R03-PV"


def test_tc24_r03_negative_inhalation_only_hh():
    res = classify(
        make_b0(
            co_di_nguyen_nghi_ngo=True,
            di_nguyen_qua_duong_hit=True,
            co_trieu_chung_ho_hap=True,
        )
    )
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None


def test_tc25_r03_negative_no_allergen_only_th():
    res = classify(make_b0(co_di_nguyen_nghi_ngo=False, co_trieu_chung_tuan_hoan=True))
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None


def test_tc26_no_rule_matched():
    res = classify(make_b0())
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None
    assert res["ly_do"] == REASON_MESSAGES["THEO_DOI"]


def test_tc27_rsoc_from_r01():
    res = classify(
        make_b0(
            co_di_nguyen_nghi_ngo=False,
            co_ton_thuong_da_niem_mac=True,
            co_trieu_chung_ho_hap=True,
            huyet_ap_tam_thu=80,
        )
    )
    assert res["muc_do"] == "SOC_PHAN_VE"
    assert res["rule_id"] == "R-SOC"


def test_tc28_rsoc_from_r02():
    res = classify(
        make_b0(
            co_di_nguyen_nghi_ngo=True,
            co_ton_thuong_da_niem_mac=True,
            co_trieu_chung_tieu_hoa_nang=True,
            huyet_ap_tam_thu=80,
        )
    )
    assert res["muc_do"] == "SOC_PHAN_VE"
    assert res["rule_id"] == "R-SOC"


def test_tc29_rsoc_from_r03():
    res = classify(
        make_b0(
            co_di_nguyen_nghi_ngo=True,
            di_nguyen_qua_duong_hit=False,
            co_trieu_chung_ho_hap=True,
            huyet_ap_tam_thu=80,
        )
    )
    assert res["muc_do"] == "SOC_PHAN_VE"
    assert res["rule_id"] == "R-SOC"


def test_tc30_isolated_hypotension_without_tier2():
    res = classify(make_b0(huyet_ap_tam_thu=80))
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None


def test_tc31_tier2_with_null_hatt():
    res = classify(make_p3(huyet_ap_tam_thu=None))
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R03-PV"


def test_tc32_b0_with_null_hatt():
    res = classify(make_b0(huyet_ap_tam_thu=None))
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None


def test_tc33_priority_r02_over_r03():
    res = classify(
        make_b0(
            co_di_nguyen_nghi_ngo=True,
            di_nguyen_qua_duong_hit=False,
            co_ton_thuong_da_niem_mac=True,
            co_trieu_chung_ho_hap=True,
            huyet_ap_tam_thu=120,
        )
    )
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R02-PV"


def test_tc34_priority_all_4_organs_positive():
    res = classify(
        make_b0(
            co_di_nguyen_nghi_ngo=True,
            di_nguyen_qua_duong_hit=False,
            co_ton_thuong_da_niem_mac=True,
            co_trieu_chung_ho_hap=True,
            co_trieu_chung_tuan_hoan=True,
            co_trieu_chung_tieu_hoa_nang=True,
            huyet_ap_tam_thu=120,
        )
    )
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R02-PV"


def test_tc35_priority_rsoc_over_r02_and_r03():
    res = classify(
        make_b0(
            co_di_nguyen_nghi_ngo=True,
            di_nguyen_qua_duong_hit=False,
            co_ton_thuong_da_niem_mac=True,
            co_trieu_chung_ho_hap=True,
            huyet_ap_tam_thu=80,
        )
    )
    assert res["muc_do"] == "SOC_PHAN_VE"
    assert res["rule_id"] == "R-SOC"


def test_tc36_r01_mutually_exclusive_with_r02_r03():
    for bits in itertools.product([False, True], repeat=6):
        nn, hit, da, hh, th, td = bits
        r01 = (not nn) and da and (hh or th)
        r02 = nn and (sum([da, hh, th, td]) >= 2)
        r03 = nn and (((not hit) and hh) or th)
        assert not (r01 and (r02 or r03))


@pytest.mark.parametrize("age", [0, 0.99])
def test_tc37_age_under_1_threshold_70(age):
    assert classify(make_p3(tuoi=age, huyet_ap_tam_thu=69))["rule_id"] == "R-SOC"
    assert classify(make_p3(tuoi=age, huyet_ap_tam_thu=70))["rule_id"] == "R03-PV"


@pytest.mark.parametrize("age,shock_bp,normal_bp", [(1.0, 71, 72), (5, 79, 80)])
def test_tc38_age_1_to_5_formula_70_plus_2age(age, shock_bp, normal_bp):
    assert classify(make_p3(tuoi=age, huyet_ap_tam_thu=shock_bp))["rule_id"] == "R-SOC"
    assert classify(make_p3(tuoi=age, huyet_ap_tam_thu=normal_bp))["rule_id"] == "R03-PV"


def test_tc39_age_10_99_boundary():
    assert classify(make_p3(tuoi=10.99, huyet_ap_tam_thu=91))["rule_id"] == "R-SOC"
    assert classify(make_p3(tuoi=10.99, huyet_ap_tam_thu=92))["rule_id"] == "R03-PV"


@pytest.mark.parametrize("age", [11.0, 17.99])
def test_tc40_age_11_to_under_18_threshold_90(age):
    assert classify(make_p3(tuoi=age, huyet_ap_tam_thu=89))["rule_id"] == "R-SOC"
    assert classify(make_p3(tuoi=age, huyet_ap_tam_thu=90))["rule_id"] == "R03-PV"


def test_tc41_age_18_threshold_90_null_nen():
    assert classify(make_p3(tuoi=18, huyet_ap_tam_thu=89, huyet_ap_tam_thu_nen=None))["rule_id"] == "R-SOC"
    assert classify(make_p3(tuoi=18, huyet_ap_tam_thu=90, huyet_ap_tam_thu_nen=None))["rule_id"] == "R03-PV"


def test_tc42_adult_30_percent_drop_exact_boundary():
    res_140 = classify(make_p3(tuoi=30, huyet_ap_tam_thu=140, huyet_ap_tam_thu_nen=200))
    assert res_140["muc_do"] == "PHAN_VE"
    assert res_140["rule_id"] == "R03-PV"

    res_139 = classify(make_p3(tuoi=30, huyet_ap_tam_thu=139, huyet_ap_tam_thu_nen=200))
    assert res_139["muc_do"] == "SOC_PHAN_VE"
    assert res_139["rule_id"] == "R-SOC"


def test_tc43_adult_hatt_above_90_but_drop_over_30_percent():
    res = classify(make_p3(tuoi=30, huyet_ap_tam_thu=95, huyet_ap_tam_thu_nen=140))
    assert res["muc_do"] == "SOC_PHAN_VE"
    assert res["rule_id"] == "R-SOC"


def test_tc44_adult_hatt_100_null_nen():
    res = classify(make_p3(tuoi=30, huyet_ap_tam_thu=100, huyet_ap_tam_thu_nen=None))
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R03-PV"


def test_tc45_under_18_ignores_nen_30_percent_drop():
    res = classify(make_p3(tuoi=15, huyet_ap_tam_thu=95, huyet_ap_tam_thu_nen=200))
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R03-PV"


def test_tc46_output_structure_all_branches():
    samples = [
        make_p3(huyet_ap_tam_thu=80),
        make_p3(huyet_ap_tam_thu=120),
        make_b0(),
        {"tuoi": -5},
    ]
    for s in samples:
        res = classify(s)
        assert set(res.keys()) == {"muc_do", "rule_id", "ly_do"}
        assert res["muc_do"] in {"SOC_PHAN_VE", "PHAN_VE", "THEO_DOI"}


def test_tc47_rule_id_matches_triggered_rule():
    assert classify(make_b0(co_ton_thuong_da_niem_mac=True, co_trieu_chung_ho_hap=True))["rule_id"] == "R01-PV"
    assert classify(make_b0(co_di_nguyen_nghi_ngo=True, co_ton_thuong_da_niem_mac=True, co_trieu_chung_tieu_hoa_nang=True))["rule_id"] == "R02-PV"
    assert classify(make_p3())["rule_id"] == "R03-PV"
    assert classify(make_p3(huyet_ap_tam_thu=80))["rule_id"] == "R-SOC"


def test_tc48_rule_id_null_on_theo_doi_and_invalid():
    assert classify(make_b0())["rule_id"] is None
    assert classify({"tuoi": "bad"})["rule_id"] is None


def test_tc49_ly_do_does_not_leak_raw_clinical_values():
    res = classify(make_p3(tuoi=47, huyet_ap_tam_thu=137, huyet_ap_tam_thu_nen=193))
    assert "47" not in res["ly_do"]
    assert "137" not in res["ly_do"]
    assert "193" not in res["ly_do"]


def test_tc50_ly_do_no_treatment_advice_and_length_bound():
    forbidden = ["tiêm", "adrenalin", "epinephrine", "điều trị", "dùng thuốc", "mg", "ml"]
    for msg in REASON_MESSAGES.values():
        assert 0 < len(msg) <= 200
        low = msg.lower()
        for word in forbidden:
            assert word not in low


def test_tc51_ly_do_invalid_differs_from_insufficient_criteria():
    res_invalid = classify({"tuoi": -1})
    res_normal = classify(make_b0())
    assert res_invalid["ly_do"] != res_normal["ly_do"]


def test_tc52_no_pii_in_outputs():
    res = classify(make_p3(ho_ten="Le Van Test", so_dien_thoai="0912345678"))
    assert "Le Van Test" not in str(res)
    assert "0912345678" not in str(res)


def test_tc53_determinism_100_runs_and_no_input_mutation():
    inp = make_p3(ho_ten="KeepUnchanged")
    snapshot = copy.deepcopy(inp)
    first = classify(inp)
    for _ in range(99):
        assert classify(inp) == first
    assert inp == snapshot


def _oracle_classify(data):
    nn = data["co_di_nguyen_nghi_ngo"]
    hit = data["di_nguyen_qua_duong_hit"]
    da = data["co_ton_thuong_da_niem_mac"]
    hh = data["co_trieu_chung_ho_hap"]
    th = data["co_trieu_chung_tuan_hoan"]
    td = data["co_trieu_chung_tieu_hoa_nang"]
    tuoi = data["tuoi"]
    hatt = data["huyet_ap_tam_thu"]
    nen = data["huyet_ap_tam_thu_nen"]

    if (not nn) and da and (hh or th):
        t2 = "R01-PV"
    elif nn and sum([da, hh, th, td]) >= 2:
        t2 = "R02-PV"
    elif nn and (((not hit) and hh) or th):
        t2 = "R03-PV"
    else:
        return ("THEO_DOI", None)

    shock = False
    if hatt is not None:
        if tuoi < 1:
            shock = hatt < 70
        elif tuoi < 11:
            shock = hatt < 70 + 2 * tuoi
        elif tuoi < 18:
            shock = hatt < 90
        else:
            shock = (hatt < 90) or (nen is not None and 10 * hatt < 7 * nen)

    if shock:
        return ("SOC_PHAN_VE", "R-SOC")
    return ("PHAN_VE", t2)


def test_tc54_exhaustive_64_bool_combinations_against_oracle():
    ages_bps = [
        (0.5, 65, None),
        (0.5, 75, None),
        (5, 75, None),
        (5, 85, None),
        (14, 85, None),
        (14, 95, 200),
        (30, 85, None),
        (30, 95, 140),
        (30, 120, 150),
        (30, None, None),
    ]
    for bits in itertools.product([False, True], repeat=6):
        nn, hit, da, hh, th, td = bits
        for tuoi, hatt, nen in ages_bps:
            sample = {
                "tuoi": tuoi,
                "huyet_ap_tam_thu": hatt,
                "huyet_ap_tam_thu_nen": nen,
                "co_di_nguyen_nghi_ngo": nn,
                "di_nguyen_qua_duong_hit": hit,
                "co_ton_thuong_da_niem_mac": da,
                "co_trieu_chung_ho_hap": hh,
                "co_trieu_chung_tuan_hoan": th,
                "co_trieu_chung_tieu_hoa_nang": td,
            }
            res = classify(sample)
            expected = _oracle_classify(sample)
            assert (res["muc_do"], res["rule_id"]) == expected


def test_tc55_no_not_implemented_error_on_custom_values():
    res = classify(make_p3(tuoi=37.5, huyet_ap_tam_thu=113))
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R03-PV"


def test_tc56_and_tc57_audit_4_fields_and_format():
    clear_audit_logs()
    custom_uuid = str(uuid.uuid4())
    classify(make_p3(), user_uuid=custom_uuid)
    logs = get_audit_logs()
    assert len(logs) == 1
    entry = logs[0]
    assert set(entry.keys()) == {"Timestamp", "User_UUID", "Action_Type", "Status"}
    assert entry["User_UUID"] == custom_uuid
    assert entry["Status"] == "CLASSIFIED_PHAN_VE"
    assert "T" in entry["Timestamp"]


def test_tc58_audit_zero_pii_and_no_clinical_values():
    clear_audit_logs()
    classify(make_p3(tuoi=43, huyet_ap_tam_thu=133, cccd="001099000111"))
    raw = str(get_audit_logs())
    assert "133" not in raw
    assert "001099000111" not in raw
    assert "cccd" not in raw


def test_tc59_audit_on_invalid_input():
    clear_audit_logs()
    classify({"tuoi": "invalid"})
    logs = get_audit_logs()
    assert len(logs) == 1
    assert logs[0]["Status"] == "INVALID_INPUT"


def test_tc60_performance_p95_under_100ms():
    clear_audit_logs()
    sample = make_p3(huyet_ap_tam_thu=80)
    for _ in range(100):
        classify(sample)

    clear_audit_logs()
    times_ms = []
    for _ in range(1000):
        t0 = time.perf_counter()
        classify(sample)
        t1 = time.perf_counter()
        times_ms.append((t1 - t0) * 1000.0)

    times_ms.sort()
    p50 = statistics.median(times_ms)
    p95 = times_ms[int(0.95 * len(times_ms)) - 1]
    assert p50 < 100.0
    assert p95 < 100.0