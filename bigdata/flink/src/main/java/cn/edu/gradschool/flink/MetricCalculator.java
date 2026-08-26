package cn.edu.gradschool.flink;

public final class MetricCalculator {
    private MetricCalculator() {
    }

    public static int heatWeight(String eventType) {
        return switch (eventType) {
            case "FAVORITE" -> 3;
            case "RECOMMENDATION_OPEN" -> 2;
            case "VIEW" -> 1;
            default -> 0;
        };
    }
}
