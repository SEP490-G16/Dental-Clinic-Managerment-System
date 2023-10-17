IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'nguyen-tran-clinic')
BEGIN
    CREATE DATABASE [nguyen-tran-clinic];
END

USE [nguyen-tran-clinic]

CREATE TABLE Patient (
    PatientID INT IDENTITY(1,1) PRIMARY KEY,
    PatientName NVARCHAR(255) NOT NULL,
    DateOfBirth DATE,
    Gender BIT, 
    PhoneNumber NVARCHAR(15), 
    FullMedicalHistory NVARCHAR(MAX),
    DentalMedicalHistory NVARCHAR(MAX),
    Email NVARCHAR(255),
    Address NVARCHAR(500),
    Description NVARCHAR(MAX),
    CreatedDate DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_PatientName ON Patient (PatientName);