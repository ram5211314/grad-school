USE grad_school_platform;

INSERT INTO university (id, name, province, city, university_level, is_double_first_class)
VALUES
  (1, '北京邮电大学', '北京', '北京', '211', 1),
  (2, '杭州电子科技大学', '浙江', '杭州', '省属重点', 0),
  (3, '南京信息工程大学', '江苏', '南京', '双一流', 1);

INSERT INTO major_program
  (id, university_id, college_name, major_code, major_name, degree_type, study_mode, subject_category, exam_subjects)
VALUES
  (1, 1, '计算机学院', '081200', '计算机科学与技术', '学术学位', 'FULL_TIME', '工学', '政治、英语一、数学一、数据结构'),
  (2, 2, '计算机学院', '085404', '计算机技术', '专业学位', 'FULL_TIME', '工学', '政治、英语二、数学二、程序设计'),
  (3, 3, '计算机学院', '085411', '大数据技术与工程', '专业学位', 'FULL_TIME', '工学', '政治、英语二、数学二、数据结构与算法'),
  (4, 2, '网络空间安全学院', '083900', '网络空间安全', '学术学位', 'FULL_TIME', '工学', '政治、英语一、数学一、408 计算机学科专业基础');

INSERT INTO admission_stat
  (program_id, admission_year, planned_enrollment, actual_enrollment, registration_count, national_line, reexamination_line, average_admission_score, data_source, collected_at)
VALUES
  (1, 2025, 80, 78, 860, 273, 345, 372, '院校研究生院公开数据', NOW()),
  (2, 2025, 120, 118, 640, 273, 310, 335, '院校研究生院公开数据', NOW()),
  (3, 2025, 90, 88, 520, 273, 300, 326, '院校研究生院公开数据', NOW()),
  (4, 2025, 30, 28, 210, 273, 315, 334, '院校研究生院公开数据', NOW());
