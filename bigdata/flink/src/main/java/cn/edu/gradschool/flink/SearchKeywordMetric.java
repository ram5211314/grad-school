package cn.edu.gradschool.flink;

import java.time.Instant;

public record SearchKeywordMetric(
        Instant windowStart,
        Instant windowEnd,
        String keyword,
        long searchCount) {
}
