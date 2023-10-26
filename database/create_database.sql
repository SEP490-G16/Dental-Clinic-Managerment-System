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
    `created_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

CREATE TABLE `medical_procedure_group` (
    `medical_procedure_group_id` VARCHAR(4) NOT NULL PRIMARY KEY,
    `name` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `description` TEXT,
    `active` TINYINT(1) NOT NULL DEFAULT 1
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE `medical_procedure` (
    medical_procedure_id VARCHAR(4) NOT NULL PRIMARY KEY,
    medical_procedure_group_id VARCHAR(4) NOT NULL,
    name VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    price INT(10) NOT NULL,
    description TEXT,
    active TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (medical_procedure_group_id) REFERENCES medical_procedure_group(medical_procedure_group_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE `treatment_course` (
    `treatment_course_id` VARCHAR(10) NOT NULL PRIMARY KEY,
    `patient_id` VARCHAR(8) NOT NULL,
    `description` TEXT,
    `created_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `status` TINYINT(1) DEFAULT 1,
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    INDEX idx_created_date (created_date)
);


DELIMITER //
CREATE TRIGGER treatment_course_before_insert 
BEFORE INSERT ON treatment_course 
FOR EACH ROW 
BEGIN
    DECLARE last_id VARCHAR(10);
    DECLARE int_id INT;
    
    SELECT treatment_course_id INTO last_id FROM treatment_course ORDER BY treatment_course_id DESC LIMIT 1;
    
    IF last_id IS NOT NULL THEN
        SET int_id = CAST(SUBSTRING(last_id, 3) AS UNSIGNED) + 1;
    ELSE
        SET int_id = 1;
    END IF;
    
    SET NEW.treatment_course_id = CONCAT('T-', LPAD(int_id, 8, '0'));
END;
//
DELIMITER ;

CREATE TABLE `mp_tc` (
    `medical_procedure_id` VARCHAR(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `treatment_course_id` VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL, 
    PRIMARY KEY (`medical_procedure_id`, `treatment_course_id`),
    FOREIGN KEY (`medical_procedure_id`) REFERENCES medical_procedure(`medical_procedure_id`),
    FOREIGN KEY (treatment_course_id) REFERENCES treatment_course(treatment_course_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE `facility` (
    `facility_id` VARCHAR(4) NOT NULL PRIMARY KEY,
    `name` VARCHAR(8) NOT NULL,
    `address` TEXT NOT NULL,
    `created_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `active` TINYINT(1) DEFAULT 1,
    `manager_id` VARCHAR(64) NOT NULL
);

DELIMITER //
CREATE TRIGGER facility_before_insert 
BEFORE INSERT ON facility 
FOR EACH ROW 
BEGIN
    DECLARE last_id VARCHAR(4);
    DECLARE int_id INT;
    
    SELECT facility_id INTO last_id FROM facility ORDER BY facility_id DESC LIMIT 1;
    
    IF last_id IS NOT NULL THEN
        SET int_id = CAST(SUBSTRING(last_id, 3) AS UNSIGNED) + 1;
    ELSE
        SET int_id = 1;
    END IF;
    
    SET NEW.facility_id = CONCAT('F-', LPAD(int_id, 2, '0'));
END;
//
DELIMITER ;

CREATE TABLE `labo` (
    `labo_id` VARCHAR(6) NOT NULL PRIMARY KEY,
    `name` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `description` TEXT,
	`phone_number` VARCHAR(15) NOT NULL,
    `email` VARCHAR(255) DEFAULT NULL,
    `address` VARCHAR(500) NOT NULL,
    `active` TINYINT(1) DEFAULT 1
);

DELIMITER //
CREATE TRIGGER labo_before_insert 
BEFORE INSERT ON labo 
FOR EACH ROW 
BEGIN
    DECLARE last_id VARCHAR(6);
    DECLARE int_id INT;
    
    SELECT labo_id INTO last_id FROM labo ORDER BY labo_id DESC LIMIT 1;
    
    IF last_id IS NOT NULL THEN
        SET int_id = CAST(SUBSTRING(last_id, 3) AS UNSIGNED) + 1;
    ELSE
        SET int_id = 1;
    END IF;
    
    SET NEW.labo_id = CONCAT('L-', LPAD(int_id, 4, '0'));
END;
//
DELIMITER ;

CREATE TABLE `medical_suppy` (
    `medical_suppy_id` VARCHAR(11) NOT NULL PRIMARY KEY,
    `type` TEXT,
    `name` TEXT,
    `quantity` SMALLINT UNSIGNED,
    `unit_price` INT,
    `order_date` TIMESTAMP,
    `orderer` TEXT,
    `received_date` TIMESTAMP,
    `receiver` TEXT,
    `warranty` TIMESTAMP,
    `description` TEXT,
    `status` TINYINT(1) DEFAULT 0,
    `facility_id` VARCHAR(4),
    FOREIGN KEY (`facility_id`) REFERENCES facility(`facility_id`)
);

DELIMITER //
CREATE TRIGGER medical_suppy_before_insert 
BEFORE INSERT ON medical_suppy 
FOR EACH ROW 
BEGIN
    DECLARE last_id VARCHAR(11);
    DECLARE int_id INT;
    
    SELECT medical_suppy_id INTO last_id FROM labo ORDER BY medical_suppy_id DESC LIMIT 1;
    
    IF last_id IS NOT NULL THEN
        SET int_id = CAST(SUBSTRING(last_id, 3) AS UNSIGNED) + 1;
    ELSE
        SET int_id = 1;
    END IF;
    
    SET NEW.medical_suppy_id = CONCAT('S-', LPAD(int_id, 9, '0'));
END;
//
DELIMITER ;

CREATE TABLE `invoice_item` (
	`invoice_item_id` VARCHAR(12) NOT NULL PRIMARY KEY,
    `price` INT,
    `invoice_id` VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
    `medical_procedure_id` VARCHAR(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    `medical_supply_id` VARCHAR(11),
    `description` TEXT,
    FOREIGN KEY (invoice_id) REFERENCES invoice(invoice_id),
    FOREIGN KEY (medical_procedure_id) REFERENCES medical_procedure(medical_procedure_id),
    FOREIGN KEY (medical_supply_id) REFERENCES medical_supply(medical_supply_id)
)

DELIMITER //
CREATE TRIGGER invoice_item_before_insert 
BEFORE INSERT ON invoice_item 
FOR EACH ROW 
BEGIN
    DECLARE last_id VARCHAR(12);
    DECLARE int_id INT;
    
    SELECT invoice_item_id INTO last_id FROM invoice_item ORDER BY invoice_item_id DESC LIMIT 1;
    
    IF last_id IS NOT NULL THEN
        SET int_id = CAST(SUBSTRING(last_id, 3) AS UNSIGNED) + 1;
    ELSE
        SET int_id = 1;
    END IF;
    
    SET NEW.invoice_item_id = CONCAT('I-', LPAD(int_id, 10, '0'));
END;
//
DELIMITER ;

CREATE TABLE `examination` (
	`examination_id` VARCHAR(12) NOT NULL PRIMARY KEY,
    `diagnosis` TEXT,
    `x-ray-image` VARCHAR(255),
    `created_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `treatment_course_id` VARCHAR(10),
    `facility_id` VARCHAR(4),
    `description` TEXT,
    `staff_id` VARCHAR(255),
    FOREIGN KEY (treatment_course_id) REFERENCES treatment_course(treatment_course_id),
    FOREIGN KEY (facility_id) REFERENCES facility(facility_id)
)

DELIMITER //
CREATE TRIGGER examination_before_insert 
BEFORE INSERT ON examination 
FOR EACH ROW 
BEGIN
    DECLARE last_id VARCHAR(12);
    DECLARE int_id INT;
    
    SELECT examination_id INTO last_id FROM examination ORDER BY examination_id DESC LIMIT 1;
    
    IF last_id IS NOT NULL THEN
        SET int_id = CAST(SUBSTRING(last_id, 3) AS UNSIGNED) + 1;
    ELSE
        SET int_id = 1;
    END IF;
    
    SET NEW.examination_id = CONCAT('S-', LPAD(int_id, 10, '0'));
END;
//
DELIMITER ;

CREATE TABLE `invoice` (
	`invoice_id` VARCHAR(10) NOT NULL PRIMARY KEY,
    `treatment_course_id` VARCHAR(10),
    `facility_id` VARCHAR(4),
    `created_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (treatment_course_id) REFERENCES treatment_course(treatment_course_id),
    FOREIGN KEY (facility_id) REFERENCES facility(facility_id)
)

DELIMITER //
CREATE TRIGGER invoice_before_insert 
BEFORE INSERT ON invoice 
FOR EACH ROW 
BEGIN
    DECLARE last_id VARCHAR(10);
    DECLARE int_id INT;
    
    SELECT invoice_id INTO last_id FROM invoice ORDER BY invoice_id DESC LIMIT 1;
    
    IF last_id IS NOT NULL THEN
        SET int_id = CAST(SUBSTRING(last_id, 3) AS UNSIGNED) + 1;
    ELSE
        SET int_id = 1;
    END IF;
    
    SET NEW.invoice_id = CONCAT('I-', LPAD(int_id, 8, '0'));
END;
//
DELIMITER ;

CREATE TABLE `receipt` (
	`receipt_id` VARCHAR(12) NOT NULL PRIMARY KEY,
	`created_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `status` TINYINT(1) DEFAULT 1,
    `examination_id` VARCHAR(12),
    `invoice_id` VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
    FOREIGN KEY (invoice_id) REFERENCES invoice(invoice_id),
    FOREIGN KEY (examination_id) REFERENCES examination(examination_id)
)