package cn.edu.gradschool.flink;

import java.time.Instant;

public record ProgramHeatMetric(
        Instant windowStart,
        Instant windowEnd,
        Long programId,
        String universityName,
        String majorName,
        long eventCount,
        long heatScore) {
}
