package cn.edu.gradschool.business;

import jakarta.persistence.criteria.Predicate;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;

@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "${app.cors-origin}")
public class ProgramController {
    private final ProgramRepository programs;
    private final StudentProfileRepository profiles;
    private final FavoriteProgramRepository favorites;

    public ProgramController(ProgramRepository programs, StudentProfileRepository profiles, FavoriteProgramRepository favorites) {
        this.programs = programs; this.profiles = profiles; this.favorites = favorites;
    }

    @GetMapping("/programs")
    public PageResponse<Program> searchPrograms(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String province,
            @RequestParam(required = false) String majorCode,
            @RequestParam(required = false) String examKeyword,
            @RequestParam(required = false) String studyMode,
            @RequestParam(defaultValue = "0") @Min(0) int page,
            @RequestParam(defaultValue = "24") @Min(1) @Max(100) int pageSize,
            @RequestParam(defaultValue = "admissionYear,desc") String sort) {
        String[] sortParts = sort.split(",", 2);
        String property = switch (sortParts[0]) { case "universityName", "majorCode", "admissionYear", "plannedEnrollment" -> sortParts[0]; default -> "admissionYear"; };
        Sort.Direction direction = sortParts.length > 1 && "asc".equalsIgnoreCase(sortParts[1]) ? Sort.Direction.ASC : Sort.Direction.DESC;
        var pageable = PageRequest.of(page, pageSize, Sort.by(direction, property));
        Page<Program> result = programs.findAll((root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            predicates.add(cb.equal(root.get("publishStatus"), "PUBLISHED"));
            if (keyword != null && !keyword.isBlank()) predicates.add(cb.or(cb.like(cb.lower(root.get("universityName")), like(keyword)), cb.like(cb.lower(root.get("majorName")), like(keyword))));
            if (province != null && !province.isBlank()) predicates.add(cb.equal(root.get("province"), province));
            if (majorCode != null && !majorCode.isBlank()) predicates.add(cb.like(root.get("majorCode"), majorCode + "%"));
            if (examKeyword != null && !examKeyword.isBlank()) predicates.add(cb.like(root.get("examSubjects"), "%" + examKeyword + "%"));
            if (studyMode != null && !studyMode.isBlank()) predicates.add(cb.equal(root.get("studyMode"), studyMode));
            return cb.and(predicates.toArray(Predicate[]::new));
        }, pageable);
        return new PageResponse<>(result.getContent(), result.getTotalElements(), result.getNumber(), result.getSize(), result.getTotalPages());
    }

    private String like(String value) { return "%" + value.toLowerCase(Locale.ROOT) + "%"; }

    @GetMapping("/programs/{id}")
    public Program programDetail(@PathVariable Long id) { return programs.findById(id).orElseThrow(() -> new NotFoundException("院校专业不存在")); }

    @PutMapping("/profiles/{userId}")
    public StudentProfile saveProfile(@PathVariable Long userId, @Valid @RequestBody ProfileRequest request) {
        return profiles.save(new StudentProfile(userId, request.undergraduateMajor(), request.targetMajor(), request.preferredProvinces(), request.estimatedScore(), request.riskPreference(), request.mathFoundation(), request.professionalCourseType()));
    }

    @GetMapping("/profiles/{userId}")
    public StudentProfile profile(@PathVariable Long userId) { return profiles.findById(userId).orElseThrow(() -> new NotFoundException("学生画像不存在")); }

    @PostMapping("/favorites") @ResponseStatus(HttpStatus.CREATED)
    public FavoriteProgram addFavorite(@Valid @RequestBody FavoriteRequest request) {
        if (!programs.existsById(request.programId())) throw new NotFoundException("院校专业不存在");
        if (favorites.existsByUserIdAndProgramId(request.userId(), request.programId())) throw new IllegalArgumentException("该院校专业已收藏");
        return favorites.save(new FavoriteProgram(request.userId(), request.programId(), request.priorityLevel(), request.note()));
    }

    @GetMapping("/favorites") public List<FavoriteProgram> listFavorites(@RequestParam Long userId) { return favorites.findByUserId(userId); }

    @GetMapping("/majors")
    public List<Map<String, String>> listMajors() {
        return programs.findDistinctMajors();
    }

    @GetMapping("/provinces")
    public List<String> listProvinces() {
        return programs.findDistinctProvinces();
    }

    @GetMapping("/programs/stats")
    public Map<String, Object> getStats() {
        Map<String, Object> stats = new java.util.LinkedHashMap<>();
        stats.put("total", programs.countByPublishStatus("PUBLISHED"));
        stats.put("universities", programs.countDistinctUniversities());
        stats.put("provinces", programs.countByProvince());
        stats.put("majorCategories", programs.countByMajorCategory());
        stats.put("yearStats", programs.yearStats());
        stats.put("topUniversities", programs.topUniversitiesByEnroll().stream().limit(15).toList());
        return stats;
    }

    @PostMapping("/admin/imports/programs")
    public Map<String, Object> importPrograms(@RequestParam MultipartFile file) throws IOException {
        int success = 0, failed = 0; String line;
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream(), StandardCharsets.UTF_8))) {
            reader.readLine();
            while ((line = reader.readLine()) != null) {
                String[] f = line.split(",", -1);
                if (f.length < 18) { failed++; continue; }
                try {
                    Program item = new Program(f[0], f[1], f[2], f[3], f[4], f[5], f[6], integer(f[7]), integer(f[8]), integer(f[9]), integer(f[10]), f[11], integer(f[12]), integer(f[13]), f[14], f[15], integer(f[16]), Instant.now(), "PUBLISHED", f[17]);
                    programs.save(item); success++;
                } catch (RuntimeException ex) { failed++; }
            }
        }
        return Map.of("fileName", file.getOriginalFilename(), "successRows", success, "failedRows", failed, "status", failed == 0 ? "PUBLISHED" : "PARTIAL");
    }

    private Integer integer(String value) { return value == null || value.isBlank() ? null : Integer.valueOf(value.trim()); }
    public record PageResponse<T>(List<T> items, long total, int page, int pageSize, int totalPages) {}
    public record ProfileRequest(@NotBlank String undergraduateMajor, @NotBlank String targetMajor, @NotBlank String preferredProvinces, @Min(0) @Max(500) Integer estimatedScore, @NotBlank String riskPreference, @NotBlank String mathFoundation, @NotBlank String professionalCourseType) {}
    public record FavoriteRequest(@Min(1) Long userId, @Min(1) Long programId, @NotBlank String priorityLevel, String note) {}
}
