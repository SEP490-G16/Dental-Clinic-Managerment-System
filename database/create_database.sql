CREATE DATABASE IF NOT EXISTS `nguyen_tran_clinic`;

USE `nguyen_tran_clinic`;

CREATE TABLE `patient` (
    `patient_id` VARCHAR(8) NOT NULL,
    `patient_name` VARCHAR(255) NOT NULL,
    `date_of_birth` DATE NOT NULL,
    `gender` TINYINT NOT NULL, 
    `phone_number` VARCHAR(15) NOT NULL, 
    `full_medical_history` TEXT DEFAULT NULL,
    `dental_medical_history` TEXT DEFAULT NULL,
    `email` VARCHAR(255) DEFAULT NULL,
    `address` VARCHAR(500) NOT NULL,
    `description` TEXT DEFAULT NULL,
    `profile_image` VARCHAR(100) DEFAULT NULL,
    `created_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `active` TINYINT(1) DEFAULT 1,
    PRIMARY KEY (`patient_id`)
);

DELIMITER //
CREATE TRIGGER patient_before_insert 
BEFORE INSERT ON patient 
FOR EACH ROW 
BEGIN
    DECLARE last_id VARCHAR(8);
    DECLARE int_id INT;
    
    SELECT patient_id INTO last_id FROM patient ORDER BY patient_id DESC LIMIT 1;
    
    IF last_id IS NOT NULL THEN
        SET int_id = CAST(SUBSTRING(last_id, 3) AS UNSIGNED) + 1;
    ELSE
        SET int_id = 1;
    END IF;
    
    SET NEW.patient_id = CONCAT('P-', LPAD(int_id, 6, '0'));
END;
//
DELIMITER ;