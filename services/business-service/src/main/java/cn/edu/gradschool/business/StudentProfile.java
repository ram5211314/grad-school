package cn.edu.gradschool.business;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
public class StudentProfile {
    @Id
    private Long userId;
    private String undergraduateMajor;
    private String targetMajor;
    private String preferredProvinces;
    private Integer estimatedScore;
    private String riskPreference;
    private String mathFoundation;
    private String professionalCourseType;

    protected StudentProfile() {
    }

    public StudentProfile(Long userId, String undergraduateMajor, String targetMajor, String preferredProvinces,
                          Integer estimatedScore, String riskPreference, String mathFoundation,
                          String professionalCourseType) {
        this.userId = userId;
        this.undergraduateMajor = undergraduateMajor;
        this.targetMajor = targetMajor;
        this.preferredProvinces = preferredProvinces;
        this.estimatedScore = estimatedScore;
        this.riskPreference = riskPreference;
        this.mathFoundation = mathFoundation;
        this.professionalCourseType = professionalCourseType;
    }

    public Long getUserId() { return userId; }
    public String getUndergraduateMajor() { return undergraduateMajor; }
    public String getTargetMajor() { return targetMajor; }
    public String getPreferredProvinces() { return preferredProvinces; }
    public Integer getEstimatedScore() { return estimatedScore; }
    public String getRiskPreference() { return riskPreference; }
    public String getMathFoundation() { return mathFoundation; }
    public String getProfessionalCourseType() { return professionalCourseType; }
}
