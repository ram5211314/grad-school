package cn.edu.gradschool.business;

import java.time.Instant;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class BusinessServiceApplication {
    public static void main(String[] args) { SpringApplication.run(BusinessServiceApplication.class, args); }

    @Bean
    CommandLineRunner demoData(ProgramRepository programs) {
        return args -> {
            if (programs.count() != 0) return;
            programs.save(new Program("\u5317\u4eac\u90ae\u7535\u5927\u5b66", "\u5317\u4eac", "081200", "\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f", "\u5b66\u672f\u5b66\u4f4d", "FULL_TIME", "\u653f\u6cbb\u3001\u82f1\u8bed\u4e00\u3001\u6570\u5b66\u4e00\u3001\u6570\u636e\u7ed3\u6784", 345, 78, null, 2025, "211", 80, 273, "\u5386\u53f2\u516c\u5f00\u57fa\u7ebf\u6570\u636e", "https://yz.chsi.com.cn/", 2025, Instant.parse("2026-08-25T00:00:00Z"), "PUBLISHED", "\u62a5\u540d\u4eba\u6570\u672a\u5b98\u65b9\u516c\u5f00"));
            programs.save(new Program("\u676d\u5dde\u7535\u5b50\u79d1\u6280\u5927\u5b66", "\u6d59\u6c5f", "085404", "\u8ba1\u7b97\u673a\u6280\u672f", "\u4e13\u4e1a\u5b66\u4f4d", "FULL_TIME", "\u653f\u6cbb\u3001\u82f1\u8bed\u4e8c\u3001\u6570\u5b66\u4e8c\u3001\u7a0b\u5e8f\u8bbe\u8ba1", 310, 118, null, 2025, "\u7701\u5c5e\u91cd\u70b9", 120, 273, "\u5386\u53f2\u516c\u5f00\u57fa\u7ebf\u6570\u636e", "https://yz.chsi.com.cn/", 2025, Instant.parse("2026-08-25T00:00:00Z"), "PUBLISHED", "\u62a5\u540d\u4eba\u6570\u672a\u5b98\u65b9\u516c\u5f00"));
            programs.save(new Program("\u5357\u4eac\u4fe1\u606f\u5de5\u7a0b\u5927\u5b66", "\u6c5f\u82cf", "085411", "\u5927\u6570\u636e\u6280\u672f\u4e0e\u5de5\u7a0b", "\u4e13\u4e1a\u5b66\u4f4d", "FULL_TIME", "\u653f\u6cbb\u3001\u82f1\u8bed\u4e8c\u3001\u6570\u5b66\u4e8c\u3001\u6570\u636e\u7ed3\u6784\u4e0e\u7b97\u6cd5", 300, 88, null, 2025, "\u53cc\u4e00\u6d41", 90, 273, "\u5386\u53f2\u516c\u5f00\u57fa\u7ebf\u6570\u636e", "https://yz.chsi.com.cn/", 2025, Instant.parse("2026-08-25T00:00:00Z"), "PUBLISHED", "\u62a5\u540d\u4eba\u6570\u672a\u5b98\u65b9\u516c\u5f00"));
            programs.save(new Program("\u676d\u5dde\u7535\u5b50\u79d1\u6280\u5927\u5b66", "\u6d59\u6c5f", "083900", "\u7f51\u7edc\u7a7a\u95f4\u5b89\u5168", "\u5b66\u672f\u5b66\u4f4d", "FULL_TIME", "\u653f\u6cbb\u3001\u82f1\u8bed\u4e00\u3001\u6570\u5b66\u4e00\u3001408 \u8ba1\u7b97\u673a\u5b66\u79d1\u4e13\u4e1a\u57fa\u7840", 315, 28, null, 2025, "\u7701\u5c5e\u91cd\u70b9", 30, 273, "\u5386\u53f2\u516c\u5f00\u57fa\u7ebf\u6570\u636e", "https://yz.chsi.com.cn/", 2025, Instant.parse("2026-08-25T00:00:00Z"), "PUBLISHED", "\u62a5\u540d\u4eba\u6570\u672a\u5b98\u65b9\u516c\u5f00"));
        };
    }
}