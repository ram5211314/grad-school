CREATE DATABASE IF NOT EXISTS grad_school_platform
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE grad_school_platform;

CREATE TABLE university (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  province VARCHAR(50) NOT NULL,
  city VARCHAR(50) NOT NULL,
  university_level VARCHAR(30) NOT NULL,
  is_double_first_class TINYINT NOT NULL DEFAULT 0,
  website VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_university_name (name)
) ENGINE=InnoDB COMMENT='院校主数据';

CREATE TABLE major_program (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  university_id BIGINT NOT NULL,
  college_name VARCHAR(100) NOT NULL,
  major_code VARCHAR(20) NOT NULL,
  major_name VARCHAR(100) NOT NULL,
  research_direction VARCHAR(200) NULL,
  degree_type VARCHAR(20) NOT NULL,
  study_mode VARCHAR(20) NOT NULL,
  subject_category VARCHAR(50) NOT NULL,
  exam_subjects VARCHAR(500) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'PUBLISHED',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_program_university FOREIGN KEY (university_id) REFERENCES university(id),
  UNIQUE KEY uk_program (university_id, major_code, college_name, study_mode)
) ENGINE=InnoDB COMMENT='院校专业项目';

CREATE TABLE admission_stat (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  program_id BIGINT NOT NULL,
  admission_year INT NOT NULL,
  planned_enrollment INT NULL,
  actual_enrollment INT NULL,
  registration_count INT NULL,
  national_line DECIMAL(5,1) NULL,
  reexamination_line DECIMAL(5,1) NULL,
  average_admission_score DECIMAL(5,1) NULL,
  data_source VARCHAR(255) NOT NULL,
  source_url VARCHAR(500) NULL,
  collected_at DATETIME NOT NULL,
  publish_status VARCHAR(20) NOT NULL DEFAULT 'PUBLISHED',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_stat_program FOREIGN KEY (program_id) REFERENCES major_program(id),
  UNIQUE KEY uk_program_year (program_id, admission_year)
) ENGINE=InnoDB COMMENT='招生年度统计';

CREATE TABLE student_profile (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  undergraduate_major VARCHAR(100) NOT NULL,
  target_major VARCHAR(100) NOT NULL,
  preferred_provinces JSON NULL,
  estimated_score DECIMAL(5,1) NOT NULL,
  preferred_level VARCHAR(30) NULL,
  study_mode VARCHAR(20) NOT NULL DEFAULT 'FULL_TIME',
  risk_preference VARCHAR(20) NOT NULL DEFAULT 'BALANCED',
  math_foundation VARCHAR(20) NULL,
  english_foundation VARCHAR(20) NULL,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_profile_user (user_id)
) ENGINE=InnoDB COMMENT='学生择校画像';

CREATE TABLE favorite_program (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  program_id BIGINT NOT NULL,
  priority_level VARCHAR(20) NOT NULL DEFAULT 'NORMAL',
  note VARCHAR(500) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_user_program (user_id, program_id),
  CONSTRAINT fk_favorite_program FOREIGN KEY (program_id) REFERENCES major_program(id)
) ENGINE=InnoDB COMMENT='学生收藏项目';

CREATE TABLE data_import_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  file_name VARCHAR(255) NOT NULL,
  data_year INT NOT NULL,
  total_rows INT NOT NULL DEFAULT 0,
  success_rows INT NOT NULL DEFAULT 0,
  failed_rows INT NOT NULL DEFAULT 0,
  status VARCHAR(20) NOT NULL,
  error_summary TEXT NULL,
  operator_id BIGINT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='招生数据导入审计';
