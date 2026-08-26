package cn.edu.gradschool.business;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class FavoriteProgram {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long userId;
    private Long programId;
    private String priorityLevel;
    private String note;

    protected FavoriteProgram() {
    }

    public FavoriteProgram(Long userId, Long programId, String priorityLevel, String note) {
        this.userId = userId;
        this.programId = programId;
        this.priorityLevel = priorityLevel;
        this.note = note;
    }

    public Long getId() { return id; }
    public Long getUserId() { return userId; }
    public Long getProgramId() { return programId; }
    public String getPriorityLevel() { return priorityLevel; }
    public String getNote() { return note; }
}
