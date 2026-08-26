package cn.edu.gradschool.flink;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class MetricCalculatorTest {
    @Test
    void assignsHigherWeightToFavorites() {
        assertEquals(1, MetricCalculator.heatWeight("VIEW"));
        assertEquals(3, MetricCalculator.heatWeight("FAVORITE"));
        assertEquals(2, MetricCalculator.heatWeight("RECOMMENDATION_OPEN"));
        assertEquals(0, MetricCalculator.heatWeight("SEARCH"));
    }

    @Test
    void parsesACompleteBehaviorEvent() {
        BehaviorEvent event = BehaviorEvent.parse(
                "2026-08-25T08:00:00Z|VIEW|3|NUIST|Big Data Technology and Engineering|");

        assertEquals(3L, event.getProgramId());
        assertEquals("VIEW", event.getEventType());
        assertEquals("", event.getKeyword());
    }
}
