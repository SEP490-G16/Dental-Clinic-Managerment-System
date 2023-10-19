CREATE DATABASE IF NOT EXISTS `nguyen_tran_clinic`;

USE `nguyen_tran_clinic`;

CREATE TABLE `patient` (
    `patient_id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_name` VARCHAR(255) NOT NULL,
    `date_of_birth` DATE,
    `gender` TINYINT, 
    `phone_number` VARCHAR(15) NOT NULL, 
    `full_medical_history` TEXT,
    `dental_medical_history` TEXT,
    `email` VARCHAR(255),
    `address` VARCHAR(500),
    `description` TEXT,
    `profile_image` VARCHAR(100),
    `created_date` DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX `idx_patient_name` ON `patient`(`patient_name`);
