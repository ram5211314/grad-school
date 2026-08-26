package cn.edu.gradschool.business;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

interface ProgramRepository extends JpaRepository<Program, Long>, JpaSpecificationExecutor<Program> {
    Page<Program> findByPublishStatus(String publishStatus, Pageable pageable);
}

interface StudentProfileRepository extends JpaRepository<StudentProfile, Long> {}

interface FavoriteProgramRepository extends JpaRepository<FavoriteProgram, Long> {
    java.util.List<FavoriteProgram> findByUserId(Long userId);
    boolean existsByUserIdAndProgramId(Long userId, Long programId);
}
