package cn.edu.gradschool.business;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.time.Instant;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ProgramRepository programRepository;

    @Override
    public void run(String... args) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

        // 创建默认用户
        if (userRepository.findByUsername("admin") == null) {
            User admin = new User("admin", encoder.encode("123456"), "admin@grad.cn", "ADMIN");
            userRepository.save(admin);
            System.out.println("[INIT] 管理员账号: admin / 123456");
        }
        if (userRepository.findByUsername("student") == null) {
            User student = new User("student", encoder.encode("123456"), "stu@grad.cn", "USER");
            userRepository.save(student);
            System.out.println("[INIT] 用户账号: student / 123456");
        }
        if (userRepository.findByUsername("test") == null) {
            User test = new User("test", encoder.encode("123456"), "test@grad.cn", "TEST");
            userRepository.save(test);
            System.out.println("[INIT] 测试账号: test / 123456");
        }

        // 如果数据库为空，自动导入CPEER数据
        if (programRepository.count() == 0) {
            System.out.println("[INIT] 数据库为空，开始导入CPEER数据...");
            importCpeerData();
            System.out.println("[INIT] 数据导入完成，共 " + programRepository.count() + " 条记录");
        } else {
            System.out.println("[INIT] 数据库已有 " + programRepository.count() + " 条记录，跳过导入");
        }
    }

    private void importCpeerData() {
        try (InputStream is = getClass().getClassLoader().getResourceAsStream("data/cpeer_programs_import.csv");
             BufferedReader reader = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8))) {

            String header = reader.readLine(); // 跳过表头
            String line;
            int success = 0, failed = 0;

            while ((line = reader.readLine()) != null) {
                String[] f = line.split(",", -1);
                if (f.length < 18) { failed++; continue; }
                try {
                    Program item = new Program(
                        f[0],                    // universityName
                        f[1],                    // province
                        f[2],                    // majorCode
                        f[3],                    // majorName
                        f[4],                    // degreeType
                        f[5],                    // studyMode
                        f[6],                    // examSubjects
                        integer(f[7]),           // reexaminationLine
                        integer(f[8]),           // actualEnrollment
                        integer(f[9]),           // registrationCount
                        integer(f[10]),          // admissionYear
                        f[11],                   // universityLevel
                        integer(f[12]),          // plannedEnrollment
                        integer(f[13]),          // nationalLine
                        f[14],                   // sourceName
                        f[15],                   // sourceUrl
                        integer(f[16]),          // sourceYear
                        Instant.now(),           // collectedAt
                        "PUBLISHED",             // publishStatus
                        f[17]                    // remarks
                    );
                    programRepository.save(item);
                    success++;
                } catch (RuntimeException ex) {
                    failed++;
                }
            }
            System.out.println("[INIT] 导入完成: 成功 " + success + " 条, 失败 " + failed + " 条");

        } catch (IOException | NullPointerException e) {
            System.out.println("[INIT] 导入失败: " + e.getMessage());
            System.out.println("[INIT] 请确保 data/cpeer_programs_import.csv 文件存在于 classpath 中");
        }
    }

    private Integer integer(String value) {
        if (value == null || value.isBlank()) return null;
        try {
            return Integer.valueOf(value.trim());
        } catch (NumberFormatException e) {
            return null;
        }
    }
}
