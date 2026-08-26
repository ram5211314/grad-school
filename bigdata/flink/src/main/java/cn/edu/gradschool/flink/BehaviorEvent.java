package cn.edu.gradschool.flink;

import java.time.Instant;
import java.util.Locale;

public class BehaviorEvent {
    private Instant eventTime;
    private String eventType;
    private Long programId;
    private String universityName;
    private String majorName;
    private String keyword;

    public BehaviorEvent() {
    }

    public BehaviorEvent(Instant eventTime, String eventType, Long programId,
                         String universityName, String majorName, String keyword) {
        this.eventTime = eventTime;
        this.eventType = eventType;
        this.programId = programId;
        this.universityName = universityName;
        this.majorName = majorName;
        this.keyword = keyword;
    }

    public static BehaviorEvent parse(String line) {
        String[] fields = line.split("\\|", -1);
        if (fields.length != 6) {
            throw new IllegalArgumentException("Expected six pipe-delimited fields");
        }
        Long programId = fields[2].isBlank() ? null : Long.parseLong(fields[2]);
        return new BehaviorEvent(
                Instant.parse(fields[0].trim()),
                fields[1].trim().toUpperCase(Locale.ROOT),
                programId,
                fields[3].trim(),
                fields[4].trim(),
                fields[5].trim().toLowerCase(Locale.ROOT));
    }

    public boolean isProgramEvent() {
        return programId != null && !universityName.isBlank() && !majorName.isBlank();
    }

    public boolean isSearchEvent() {
        return "SEARCH".equals(eventType) && !keyword.isBlank();
    }

    public String programKey() {
        return programId + "|" + universityName + "|" + majorName;
    }

    public Instant getEventTime() { return eventTime; }
    public void setEventTime(Instant eventTime) { this.eventTime = eventTime; }
    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }
    public Long getProgramId() { return programId; }
    public void setProgramId(Long programId) { this.programId = programId; }
    public String getUniversityName() { return universityName; }
    public void setUniversityName(String universityName) { this.universityName = universityName; }
    public String getMajorName() { return majorName; }
    public void setMajorName(String majorName) { this.majorName = majorName; }
    public String getKeyword() { return keyword; }
    public void setKeyword(String keyword) { this.keyword = keyword; }
}
