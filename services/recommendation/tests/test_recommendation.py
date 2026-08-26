from services.recommendation.recommendation import rank_programs


def test_programs_are_ranked_by_score():
    profile = {
        "estimated_score": 340,
        "target_major": "大数据技术与工程",
        "preferred_provinces": ["江苏"],
        "risk_preference": "BALANCED",
    }
    programs = [
        {
            "major_name": "计算机科学与技术",
            "province": "北京",
            "reexamination_line": 345,
            "registration_count": 860,
            "actual_enrollment": 78,
        },
        {
            "major_name": "大数据技术与工程",
            "province": "江苏",
            "reexamination_line": 300,
            "registration_count": 520,
            "actual_enrollment": 88,
        },
    ]
    result = rank_programs(profile, programs)
    assert result[0]["major_name"] == "大数据技术与工程"
    assert result[0]["tier"] == "保底"
