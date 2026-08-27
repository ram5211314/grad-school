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

    @Query("SELECT DISTINCT p.majorCode AS code, p.majorName AS name FROM Program p WHERE p.publishStatus = 'PUBLISHED' ORDER BY p.majorCode")
    List<Map<String, String>> findDistinctMajors();

    @Query("SELECT DISTINCT p.province FROM Program p WHERE p.publishStatus = 'PUBLISHED' ORDER BY p.province")
    List<String> findDistinctProvinces();
}

interface StudentProfileRepository extends JpaRepository<StudentProfile, Long> {}

interface FavoriteProgramRepository extends JpaRepository<FavoriteProgram, Long> {
    java.util.List<FavoriteProgram> findByUserId(Long userId);
    boolean existsByUserIdAndProgramId(Long userId, Long programId);
}
