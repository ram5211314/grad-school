RISK_CONFIG = {
    "CONSERVATIVE": {"safe": 15, "steady": 0, "reach": -15},
    "BALANCED": {"safe": 10, "steady": 5, "reach": -5},
    "AGGRESSIVE": {"safe": 5, "steady": 10, "reach": 5},
}
MODEL_VERSION = "rules-v0.2"
DEFAULT_WEIGHTS = {"score": 45, "competition": 20, "region": 15, "major": 15}


def _tier(score_gap):
    if score_gap >= 20: return "保底"
    if score_gap >= 0: return "稳妥"
    return "冲刺"


def _competition_score(program):
    registration_count = program.get("registration_count")
    actual_enrollment = program.get("actual_enrollment")
    if not registration_count or not actual_enrollment:
        return 10, "报名人数未官方公开，竞争度不作为强结论"
    ratio = registration_count / max(actual_enrollment, 1)
    if ratio <= 5: return 20, "官方公开报名录取比显示竞争强度较低"
    if ratio <= 10: return 12, "官方公开报名录取比显示竞争强度适中"
    return 4, "官方公开报名录取比显示竞争强度较高"


def score_program(profile, program, weights=None):
    weights = {**DEFAULT_WEIGHTS, **(weights or {})}
    estimated_score = float(profile.get("estimated_score", 0))
    line = program.get("reexamination_line")
    if not line or line == 0:
        line = program.get("national_line") or 0
    line = float(line)
    has_line = line > 0
    score_gap = estimated_score - line if has_line else 0
    tier = _tier(score_gap) if has_line else "未知"
    risk_bonus = RISK_CONFIG.get(profile.get("risk_preference", "BALANCED"), RISK_CONFIG["BALANCED"])[{"保底": "safe", "稳妥": "steady", "冲刺": "reach"}.get(tier, "steady")]
    if has_line:
        score_match = max(0, min(weights["score"], weights["score"] * (0.55 + score_gap / 100)))
    else:
        score_match = weights["score"] * 0.5
    competition, competition_reason = _competition_score(program)
    competition = competition * weights["competition"] / DEFAULT_WEIGHTS["competition"]
    region_match = weights["region"] if program.get("province") in profile.get("preferred_provinces", []) else weights["region"] / 3
    target = profile.get("target_major", "")
    major_code = program.get("major_code") or program.get("majorName") or ""
    major_match = weights["major"] if target and target in str(major_code) else weights["major"] / 2
    total = round(max(0, min(100, score_match + competition + region_match + major_match + risk_bonus)), 1)
    reason_score = f"预估分与复试线相差 {score_gap:.1f} 分，属于{tier}目标" if has_line else "暂无复试线数据，评分仅供参考"
    return {**program, "recommendation_score": total, "tier": tier, "model_version": MODEL_VERSION,
            "reasons": [reason_score, competition_reason,
                        "符合目标地区偏好" if region_match == weights["region"] else "地区不在优先范围内",
                        "目标专业完全匹配" if major_match == weights["major"] else "专业为相近或备选方向"]}


def rank_programs(profile, programs, weights=None):
    return sorted([score_program(profile, p, weights) for p in programs], key=lambda item: item["recommendation_score"], reverse=True)