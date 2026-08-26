CREATE DATABASE IF NOT EXISTS grad_school_dw;
USE grad_school_dw;

CREATE EXTERNAL TABLE IF NOT EXISTS ods_admission_stat (
  university_name STRING,
  province STRING,
  major_code STRING,
  major_name STRING,
  admission_year INT,
  planned_enrollment INT,
  actual_enrollment INT,
  registration_count INT,
  national_line DECIMAL(5,1),
  reexamination_line DECIMAL(5,1),
  average_admission_score DECIMAL(5,1),
  data_source STRING,
  collected_at TIMESTAMP
)
STORED AS PARQUET
LOCATION '/grad-school/ods/admission_stat';

CREATE TABLE IF NOT EXISTS dwd_admission_stat (
  university_name STRING,
  province STRING,
  major_code STRING,
  major_name STRING,
  admission_year INT,
  planned_enrollment INT,
  actual_enrollment INT,
  registration_count INT,
  registration_admission_ratio DECIMAL(10,2),
  reexamination_line DECIMAL(5,1),
  average_admission_score DECIMAL(5,1),
  data_source STRING
)
STORED AS PARQUET;

INSERT OVERWRITE TABLE dwd_admission_stat
SELECT
  university_name,
  province,
  major_code,
  major_name,
  admission_year,
  planned_enrollment,
  actual_enrollment,
  registration_count,
  CAST(registration_count / CASE WHEN actual_enrollment > 0 THEN actual_enrollment ELSE 1 END AS DECIMAL(10,2)),
  reexamination_line,
  average_admission_score,
  data_source
FROM ods_admission_stat
WHERE university_name IS NOT NULL
  AND major_name IS NOT NULL
  AND admission_year >= 2020;

CREATE TABLE IF NOT EXISTS dws_program_recommendation_feature (
  university_name STRING,
  province STRING,
  major_code STRING,
  major_name STRING,
  latest_year INT,
  latest_reexamination_line DECIMAL(5,1),
  latest_ratio DECIMAL(10,2),
  avg_admission_score DECIMAL(5,1)
)
STORED AS PARQUET;

CREATE TABLE IF NOT EXISTS dws_program_year_metric (
  university_name STRING,
  province STRING,
  major_code STRING,
  major_name STRING,
  admission_year INT,
  program_count BIGINT,
  total_planned_enrollment BIGINT,
  total_actual_enrollment BIGINT,
  total_registration_count BIGINT,
  avg_registration_admission_ratio DECIMAL(10,2),
  avg_reexamination_line DECIMAL(5,1),
  avg_admission_score DECIMAL(5,1)
)
STORED AS PARQUET;

INSERT OVERWRITE TABLE dws_program_year_metric
SELECT
  university_name,
  province,
  major_code,
  major_name,
  admission_year,
  COUNT(1) AS program_count,
  SUM(planned_enrollment) AS total_planned_enrollment,
  SUM(actual_enrollment) AS total_actual_enrollment,
  SUM(registration_count) AS total_registration_count,
  CAST(AVG(registration_admission_ratio) AS DECIMAL(10,2)) AS avg_registration_admission_ratio,
  CAST(AVG(reexamination_line) AS DECIMAL(5,1)) AS avg_reexamination_line,
  CAST(AVG(average_admission_score) AS DECIMAL(5,1)) AS avg_admission_score
FROM dwd_admission_stat
GROUP BY
  university_name,
  province,
  major_code,
  major_name,
  admission_year;

WITH ranked_programs AS (
  SELECT
    university_name,
    province,
    major_code,
    major_name,
    admission_year,
    reexamination_line,
    registration_admission_ratio,
    average_admission_score,
    ROW_NUMBER() OVER (
      PARTITION BY university_name, major_code, major_name
      ORDER BY admission_year DESC
    ) AS year_rank
  FROM dwd_admission_stat
)
INSERT OVERWRITE TABLE dws_program_recommendation_feature
SELECT
  university_name,
  province,
  major_code,
  major_name,
  admission_year AS latest_year,
  reexamination_line AS latest_reexamination_line,
  registration_admission_ratio AS latest_ratio,
  average_admission_score AS avg_admission_score
FROM ranked_programs
WHERE year_rank = 1;
