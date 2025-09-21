-- Database initialization script for Code Analysis Agent
-- This script creates the database and necessary tables

-- Create database (run this as postgres superuser)
-- CREATE DATABASE code_analysis_db;

-- Connect to the database
\c code_analysis_db;

-- Create the analysis_history table
CREATE TABLE IF NOT EXISTS analysis_history (
    id SERIAL PRIMARY KEY,
    code_snippet TEXT NOT NULL,
    suggestions TEXT NOT NULL, -- JSON string containing suggestions
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    agent_version VARCHAR(50) DEFAULT '1.0.0',
    processing_time INTEGER -- processing time in milliseconds
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at ON analysis_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_history_agent_version ON analysis_history(agent_version);

-- Create a table for agent statistics (optional, for monitoring)
CREATE TABLE IF NOT EXISTS agent_statistics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2),
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial statistics
INSERT INTO agent_statistics (metric_name, metric_value) VALUES 
('total_analyses', 0),
('avg_processing_time', 0),
('uptime_hours', 0)
ON CONFLICT DO NOTHING;

-- Create a view for analysis summary
CREATE OR REPLACE VIEW analysis_summary AS
SELECT 
    DATE(created_at) as analysis_date,
    COUNT(*) as total_analyses,
    AVG(processing_time) as avg_processing_time,
    MIN(processing_time) as min_processing_time,
    MAX(processing_time) as max_processing_time
FROM analysis_history
GROUP BY DATE(created_at)
ORDER BY analysis_date DESC;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- Display table information
\d analysis_history;
\d agent_statistics;

-- Display the view
SELECT * FROM analysis_summary LIMIT 5;