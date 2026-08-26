package cn.edu.gradschool.business;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private UserRepository userRepository;

    @Override
    public void run(String... args) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        if (userRepository.findByUsername("admin") == null) {
            User admin = new User("admin", encoder.encode("123456"), "admin@grad.cn", "ADMIN");
            userRepository.save(admin);
            System.out.println("[INIT] 默认管理员账号创建成功: admin / 123456");
        }
        if (userRepository.findByUsername("student") == null) {
            User student = new User("student", encoder.encode("123456"), "stu@grad.cn", "USER");
            userRepository.save(student);
            System.out.println("[INIT] 默认用户账号创建成功: student / 123456");
        }
    }
}
