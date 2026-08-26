package cn.edu.gradschool.business;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import java.time.Instant;

@Entity
public class Program {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String universityName;
    private String province;
    private String majorCode;
    private String majorName;
    private String degreeType;
    private String studyMode;
    private String examSubjects;
    private Integer reexaminationLine;
    private Integer actualEnrollment;
    private Integer registrationCount;
    private Integer admissionYear;
    private String universityLevel;
    private Integer plannedEnrollment;
    private Integer nationalLine;
    private String sourceName;
    private String sourceUrl;
    private Integer sourceYear;
    private Instant collectedAt;
    private String publishStatus;
    private String remarks;

    protected Program() {}

    public Program(String universityName, String province, String majorCode, String majorName,
                   String degreeType, String studyMode, String examSubjects, Integer reexaminationLine,
                   Integer actualEnrollment, Integer registrationCount, Integer admissionYear,
                   String universityLevel, Integer plannedEnrollment, Integer nationalLine,
                   String sourceName, String sourceUrl, Integer sourceYear, Instant collectedAt,
                   String publishStatus, String remarks) {
        this.universityName = universityName; this.province = province; this.majorCode = majorCode;
        this.majorName = majorName; this.degreeType = degreeType; this.studyMode = studyMode;
        this.examSubjects = examSubjects; this.reexaminationLine = reexaminationLine;
        this.actualEnrollment = actualEnrollment; this.registrationCount = registrationCount;
        this.admissionYear = admissionYear; this.universityLevel = universityLevel;
        this.plannedEnrollment = plannedEnrollment; this.nationalLine = nationalLine;
        this.sourceName = sourceName; this.sourceUrl = sourceUrl; this.sourceYear = sourceYear;
        this.collectedAt = collectedAt; this.publishStatus = publishStatus; this.remarks = remarks;
    }

    public Long getId() { return id; }
    public String getUniversityName() { return universityName; }
    public String getProvince() { return province; }
    public String getMajorCode() { return majorCode; }
    public String getMajorName() { return majorName; }
    public String getDegreeType() { return degreeType; }
    public String getStudyMode() { return studyMode; }
    public String getExamSubjects() { return examSubjects; }
    public Integer getReexaminationLine() { return reexaminationLine; }
    public Integer getActualEnrollment() { return actualEnrollment; }
    public Integer getRegistrationCount() { return registrationCount; }
    public Integer getAdmissionYear() { return admissionYear; }
    public String getUniversityLevel() { return universityLevel; }
    public Integer getPlannedEnrollment() { return plannedEnrollment; }
    public Integer getNationalLine() { return nationalLine; }
    public String getSourceName() { return sourceName; }
    public String getSourceUrl() { return sourceUrl; }
    public Integer getSourceYear() { return sourceYear; }
    public Instant getCollectedAt() { return collectedAt; }
    public String getPublishStatus() { return publishStatus; }
    public String getRemarks() { return remarks; }
}
