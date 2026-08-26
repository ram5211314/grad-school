package cn.edu.gradschool.flink;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;

import java.time.Duration;
import java.time.Instant;

public class RealtimeMetricsJob {
    private static final Duration OUT_OF_ORDERNESS = Duration.ofMinutes(1);

    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            throw new IllegalArgumentException("Usage: RealtimeMetricsJob <events-file>");
        }

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(1);

        SingleOutputStreamOperator<BehaviorEvent> events = env.readTextFile(args[0])
                .filter(line -> !line.isBlank() && !line.startsWith("#"))
                .map(BehaviorEvent::parse)
                .returns(TypeInformation.of(BehaviorEvent.class))
                .assignTimestampsAndWatermarks(
                        WatermarkStrategy.<BehaviorEvent>forBoundedOutOfOrderness(OUT_OF_ORDERNESS)
                                .withTimestampAssigner((event, ignored) -> event.getEventTime().toEpochMilli()));

        DataStream<ProgramHeatMetric> programHeat = events
                .filter(BehaviorEvent::isProgramEvent)
                .keyBy((KeySelector<BehaviorEvent, String>) BehaviorEvent::programKey)
                .timeWindow(Time.minutes(5))
                .process(new ProgramHeatWindow());

        DataStream<SearchKeywordMetric> keywordHeat = events
                .filter(BehaviorEvent::isSearchEvent)
                .keyBy(BehaviorEvent::getKeyword)
                .timeWindow(Time.minutes(5))
                .process(new SearchKeywordWindow());

        programHeat.print("hot-program");
        keywordHeat.print("hot-keyword");
        env.execute("grad-school-realtime-metrics");
    }

    private static class ProgramHeatWindow
            extends ProcessWindowFunction<BehaviorEvent, ProgramHeatMetric, String, TimeWindow> {
        @Override
        public void process(String key, Context context, Iterable<BehaviorEvent> events,
                            Collector<ProgramHeatMetric> out) {
            long eventCount = 0;
            long heatScore = 0;
            BehaviorEvent first = null;
            for (BehaviorEvent event : events) {
                if (first == null) {
                    first = event;
                }
                eventCount++;
                heatScore += MetricCalculator.heatWeight(event.getEventType());
            }
            if (first != null && heatScore > 0) {
                out.collect(new ProgramHeatMetric(
                        Instant.ofEpochMilli(context.window().getStart()),
                        Instant.ofEpochMilli(context.window().getEnd()),
                        first.getProgramId(),
                        first.getUniversityName(),
                        first.getMajorName(),
                        eventCount,
                        heatScore));
            }
        }
    }

    private static class SearchKeywordWindow
            extends ProcessWindowFunction<BehaviorEvent, SearchKeywordMetric, String, TimeWindow> {
        @Override
        public void process(String keyword, Context context, Iterable<BehaviorEvent> events,
                            Collector<SearchKeywordMetric> out) {
            long searchCount = 0;
            for (BehaviorEvent ignored : events) {
                searchCount++;
            }
            out.collect(new SearchKeywordMetric(
                    Instant.ofEpochMilli(context.window().getStart()),
                    Instant.ofEpochMilli(context.window().getEnd()),
                    keyword,
                    searchCount));
        }
    }
}
