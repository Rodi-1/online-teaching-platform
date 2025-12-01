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

-- You can add initialization for other services here as they are developed
-- Example:
-- CREATE DATABASE homework_service_db OWNER homework_service;
-- CREATE DATABASE gradebook_service_db OWNER gradebook_service;
-- etc.

