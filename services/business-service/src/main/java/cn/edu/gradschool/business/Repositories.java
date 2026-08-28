package cn.edu.gradschool.business;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Map;

interface ProgramRepository extends JpaRepository<Program, Long>, JpaSpecificationExecutor<Program> {
    Page<Program> findByPublishStatus(String publishStatus, Pageable pageable);
    long countByPublishStatus(String publishStatus);

    @Query("SELECT DISTINCT p.majorCode AS code, p.majorName AS name FROM Program p WHERE p.publishStatus = 'PUBLISHED' ORDER BY p.majorCode")
    List<Map<String, String>> findDistinctMajors();

    @Query("SELECT DISTINCT p.province FROM Program p WHERE p.publishStatus = 'PUBLISHED' ORDER BY p.province")
    List<String> findDistinctProvinces();

    @Query("SELECT p.province AS name, COUNT(p) AS value FROM Program p WHERE p.publishStatus='PUBLISHED' GROUP BY p.province ORDER BY COUNT(p) DESC")
    List<Object[]> countByProvince();

    @Query("SELECT SUBSTRING(p.majorCode,1,2) AS name, COUNT(p) AS value FROM Program p WHERE p.publishStatus='PUBLISHED' GROUP BY SUBSTRING(p.majorCode,1,2) ORDER BY COUNT(p) DESC")
    List<Object[]> countByMajorCategory();

    @Query("SELECT p.admissionYear AS name, COUNT(p) AS value, COALESCE(SUM(p.plannedEnrollment),0) AS totalEnroll, COALESCE(SUM(p.registrationCount),0) AS totalReg FROM Program p WHERE p.publishStatus='PUBLISHED' GROUP BY p.admissionYear ORDER BY p.admissionYear")
    List<Object[]> yearStats();

    @Query("SELECT p.universityName AS name, COALESCE(SUM(p.plannedEnrollment),0) AS value FROM Program p WHERE p.publishStatus='PUBLISHED' AND p.plannedEnrollment IS NOT NULL GROUP BY p.universityName ORDER BY SUM(p.plannedEnrollment) DESC")
    List<Object[]> topUniversitiesByEnroll();

    @Query("SELECT COUNT(DISTINCT p.universityName) FROM Program p WHERE p.publishStatus='PUBLISHED'")
    long countDistinctUniversities();
}

interface StudentProfileRepository extends JpaRepository<StudentProfile, Long> {}

interface FavoriteProgramRepository extends JpaRepository<FavoriteProgram, Long> {
    java.util.List<FavoriteProgram> findByUserId(Long userId);
    boolean existsByUserIdAndProgramId(Long userId, Long programId);
}
