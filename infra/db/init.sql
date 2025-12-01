-- Database initialization script
-- This script runs automatically when PostgreSQL container starts for the first time

-- Create database for user service if it doesn't exist
-- Note: This will be executed as postgres user

-- Create user for user service
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'user_service') THEN
      
      CREATE ROLE user_service LOGIN PASSWORD 'user_service_pass123';
   END IF;
END
$do$;

-- Create database for user service
SELECT 'CREATE DATABASE user_service_db OWNER user_service'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'user_service_db')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE user_service_db TO user_service;

-- Create user for homework service
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'homework_service') THEN
      
      CREATE ROLE homework_service LOGIN PASSWORD 'homework_service_pass123';
   END IF;
END
$do$;

-- Create database for homework service
SELECT 'CREATE DATABASE homework_service_db OWNER homework_service'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'homework_service_db')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE homework_service_db TO homework_service;

-- Create user for gradebook service
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'gradebook_service') THEN
      
      CREATE ROLE gradebook_service LOGIN PASSWORD 'gradebook_service_pass123';
   END IF;
END
$do$;

-- Create database for gradebook service
SELECT 'CREATE DATABASE gradebook_service_db OWNER gradebook_service'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gradebook_service_db')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE gradebook_service_db TO gradebook_service;

-- Create user for profile service
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'profile_service') THEN
      
      CREATE ROLE profile_service LOGIN PASSWORD 'profile_service_pass123';
   END IF;
END
$do$;

-- Create database for profile service
SELECT 'CREATE DATABASE profile_service_db OWNER profile_service'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'profile_service_db')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE profile_service_db TO profile_service;

-- Create user for notifications service
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'notifications_service') THEN
      
      CREATE ROLE notifications_service LOGIN PASSWORD 'notifications_service_pass123';
   END IF;
END
$do$;

-- Create database for notifications service
SELECT 'CREATE DATABASE notifications_service_db OWNER notifications_service'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'notifications_service_db')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE notifications_service_db TO notifications_service;

-- Create user for tests service
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'tests_service') THEN
      
      CREATE ROLE tests_service LOGIN PASSWORD 'tests_service_pass123';
   END IF;
END
$do$;

-- Create database for tests service
SELECT 'CREATE DATABASE tests_service_db OWNER tests_service'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'tests_service_db')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tests_service_db TO tests_service;

-- Create user for schedule service
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'schedule_service') THEN
      
      CREATE ROLE schedule_service LOGIN PASSWORD 'schedule_service_pass123';
   END IF;
END
$do$;

-- Create database for schedule service
SELECT 'CREATE DATABASE schedule_service_db OWNER schedule_service'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'schedule_service_db')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE schedule_service_db TO schedule_service;

-- Create user for reports service
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'reports_service') THEN
      
      CREATE ROLE reports_service LOGIN PASSWORD 'reports_service_pass123';
   END IF;
END
$do$;

-- Create database for reports service
SELECT 'CREATE DATABASE reports_service_db OWNER reports_service'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'reports_service_db')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE reports_service_db TO reports_service;

