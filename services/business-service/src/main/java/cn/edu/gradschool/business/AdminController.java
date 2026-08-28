package cn.edu.gradschool.business;

import jakarta.persistence.criteria.Predicate;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

@RestController
@RequestMapping("/api/v1/admin")
@CrossOrigin(origins = "${app.cors-origin}")
public class AdminController {

    private final ProgramRepository programs;
    private final UserRepository users;

    public AdminController(ProgramRepository programs, UserRepository users) {
        this.programs = programs;
        this.users = users;
    }

    // ── 操作日志（内存存储） ──
    private static final CopyOnWriteArrayList<Map<String, String>> operationLogs = new CopyOnWriteArrayList<>();

    private void log(String operator, String action, String detail) {
        Map<String, String> entry = new LinkedHashMap<>();
        entry.put("time", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        entry.put("operator", operator);
        entry.put("action", action);
        entry.put("detail", detail);
        operationLogs.add(0, entry);
        if (operationLogs.size() > 500) operationLogs.remove(operationLogs.size() - 1);
    }

    // ── 系统概览统计 ──
    @GetMapping("/stats")
    public Map<String, Object> getStats() {
        Map<String, Object> stats = new LinkedHashMap<>();
        stats.put("totalPrograms", programs.countByPublishStatus("PUBLISHED"));
        stats.put("totalUniversities", programs.countDistinctUniversities());
        stats.put("totalUsers", users.count());
        stats.put("totalProvinces", programs.findDistinctProvinces().size());
        return stats;
    }

    // ── 招生数据 CRUD ──
    @GetMapping("/programs")
    public PageResponse<Program> listPrograms(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String province,
            @RequestParam(required = false) String majorCode,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "15") int pageSize) {
        Page<Program> result = programs.findAll((root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            predicates.add(cb.equal(root.get("publishStatus"), "PUBLISHED"));
            if (keyword != null && !keyword.isBlank()) {
                predicates.add(cb.or(
                    cb.like(cb.lower(root.get("universityName")), "%" + keyword.toLowerCase() + "%"),
                    cb.like(cb.lower(root.get("majorName")), "%" + keyword.toLowerCase() + "%"),
                    cb.like(root.get("majorCode"), "%" + keyword + "%")
                ));
            }
            if (province != null && !province.isBlank()) predicates.add(cb.equal(root.get("province"), province));
            if (majorCode != null && !majorCode.isBlank()) predicates.add(cb.like(root.get("majorCode"), majorCode + "%"));
            return cb.and(predicates.toArray(Predicate[]::new));
        }, PageRequest.of(page, pageSize, Sort.by(Sort.Direction.DESC, "admissionYear")));
        return new PageResponse<>(result.getContent(), result.getTotalElements(), result.getNumber(), result.getSize(), result.getTotalPages());
    }

    @PostMapping("/programs")
    @ResponseStatus(HttpStatus.CREATED)
    public Program createProgram(@RequestBody Program program) {
        program.setCollectedAt(Instant.now());
        program.setPublishStatus("PUBLISHED");
        Program saved = programs.save(program);
        log("admin", "新增数据", saved.getUniversityName() + " " + saved.getMajorName());
        return saved;
    }

    @PutMapping("/programs/{id}")
    public Program updateProgram(@PathVariable Long id, @RequestBody Program program) {
        Program existing = programs.findById(id).orElseThrow(() -> new NotFoundException("记录不存在"));
        existing.setUniversityName(program.getUniversityName());
        existing.setProvince(program.getProvince());
        existing.setMajorCode(program.getMajorCode());
        existing.setMajorName(program.getMajorName());
        existing.setDegreeType(program.getDegreeType());
        existing.setStudyMode(program.getStudyMode());
        existing.setExamSubjects(program.getExamSubjects());
        existing.setAdmissionYear(program.getAdmissionYear());
        existing.setUniversityLevel(program.getUniversityLevel());
        existing.setReexaminationLine(program.getReexaminationLine());
        existing.setPlannedEnrollment(program.getPlannedEnrollment());
        existing.setActualEnrollment(program.getActualEnrollment());
        existing.setRegistrationCount(program.getRegistrationCount());
        existing.setNationalLine(program.getNationalLine());
        existing.setRemarks(program.getRemarks());
        Program saved = programs.save(existing);
        log("admin", "编辑数据", saved.getUniversityName() + " " + saved.getMajorName());
        return saved;
    }

    @DeleteMapping("/programs/{id}")
    public Map<String, String> deleteProgram(@PathVariable Long id) {
        Program p = programs.findById(id).orElseThrow(() -> new NotFoundException("记录不存在"));
        programs.deleteById(id);
        log("admin", "删除数据", p.getUniversityName() + " " + p.getMajorName());
        return Map.of("message", "删除成功");
    }

    // ── 用户管理 ──
    @GetMapping("/users")
    public PageResponse<Map<String, Object>> listUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int pageSize) {
        Page<User> result = users.findAll(PageRequest.of(page, pageSize, Sort.by(Sort.Direction.DESC, "createdAt")));
        List<Map<String, Object>> items = result.getContent().stream().map(u -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", u.getId());
            m.put("username", u.getUsername());
            m.put("email", u.getEmail());
            m.put("role", u.getRole());
            m.put("status", u.getStatus());
            m.put("createdAt", u.getCreatedAt());
            return m;
        }).toList();
        return new PageResponse<>(items, result.getTotalElements(), result.getNumber(), result.getSize(), result.getTotalPages());
    }

    @PutMapping("/users/{id}/role")
    public Map<String, String> updateUserRole(@PathVariable Long id, @RequestBody Map<String, String> body) {
        User user = users.findById(id).orElseThrow(() -> new NotFoundException("用户不存在"));
        String role = body.get("role");
        if (!List.of("USER", "ADMIN", "TEST").contains(role)) throw new IllegalArgumentException("无效角色");
        user.setRole(role);
        users.save(user);
        log("admin", "修改角色", user.getUsername() + " → " + role);
        return Map.of("message", "角色已更新");
    }

    @PutMapping("/users/{id}/status")
    public Map<String, String> updateUserStatus(@PathVariable Long id, @RequestBody Map<String, String> body) {
        User user = users.findById(id).orElseThrow(() -> new NotFoundException("用户不存在"));
        String status = body.get("status");
        if (!List.of("ACTIVE", "DISABLED").contains(status)) throw new IllegalArgumentException("无效状态");
        user.setStatus(status);
        users.save(user);
        log("admin", "修改状态", user.getUsername() + " → " + status);
        return Map.of("message", "状态已更新");
    }

    @DeleteMapping("/users/{id}")
    public Map<String, String> deleteUser(@PathVariable Long id) {
        User user = users.findById(id).orElseThrow(() -> new NotFoundException("用户不存在"));
        users.deleteById(id);
        log("admin", "删除用户", user.getUsername());
        return Map.of("message", "用户已删除");
    }

    // ── 操作日志 ──
    @GetMapping("/logs")
    public Map<String, Object> listLogs(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int pageSize) {
        int start = page * pageSize;
        int end = Math.min(start + pageSize, operationLogs.size());
        List<Map<String, String>> items = start < operationLogs.size() ? operationLogs.subList(start, end) : List.of();
        int totalPages = (int) Math.ceil((double) operationLogs.size() / pageSize);
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("items", items);
        result.put("total", operationLogs.size());
        result.put("page", page);
        result.put("pageSize", pageSize);
        result.put("totalPages", totalPages);
        return result;
    }

    public record PageResponse<T>(List<T> items, long total, int page, int pageSize, int totalPages) {}
}
