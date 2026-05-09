-- Cloud Cost Monitoring Database Schema
-- SQLite Database for Cloud Cost Management

-- Services table to store different cloud services
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL UNIQUE,
    service_category TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regions table to store cloud regions
CREATE TABLE IF NOT EXISTS regions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE,
    region_code TEXT NOT NULL UNIQUE,
    provider TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cost records table to store daily cost data
CREATE TABLE IF NOT EXISTS cost_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    date DATE NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    usage_hours DECIMAL(8, 2),
    resource_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services (id),
    FOREIGN KEY (region_id) REFERENCES regions (id)
);

-- Resource utilization table for idle resource tracking
CREATE TABLE IF NOT EXISTS resource_utilization (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    resource_id TEXT NOT NULL,
    utilization_percentage DECIMAL(5, 2),
    last_active_date DATE,
    is_idle BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services (id),
    FOREIGN KEY (region_id) REFERENCES regions (id)
);

-- Optimization recommendations table
CREATE TABLE IF NOT EXISTS optimization_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    recommendation_type TEXT NOT NULL,
    description TEXT NOT NULL,
    potential_savings DECIMAL(10, 2),
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services (id),
    FOREIGN KEY (region_id) REFERENCES regions (id)
);

-- Cost anomalies table
CREATE TABLE IF NOT EXISTS cost_anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    date DATE NOT NULL,
    expected_cost DECIMAL(10, 2),
    actual_cost DECIMAL(10, 2),
    variance_percentage DECIMAL(5, 2),
    anomaly_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services (id),
    FOREIGN KEY (region_id) REFERENCES regions (id)
);

-- Insert sample data for services
INSERT OR IGNORE INTO services (service_name, service_category, description) VALUES
('EC2', 'Compute', 'Elastic Compute Cloud instances'),
('S3', 'Storage', 'Simple Storage Service'),
('RDS', 'Database', 'Relational Database Service'),
('Lambda', 'Compute', 'Serverless computing'),
('CloudFront', 'Network', 'Content Delivery Network'),
('DynamoDB', 'Database', 'NoSQL Database'),
('EKS', 'Compute', 'Kubernetes Service'),
('ElastiCache', 'Database', 'In-memory caching'),
('SQS', 'Messaging', 'Simple Queue Service'),
('SNS', 'Messaging', 'Simple Notification Service');

-- Insert sample data for regions
INSERT OR IGNORE INTO regions (region_name, region_code, provider) VALUES
('US East (N. Virginia)', 'us-east-1', 'AWS'),
('US West (Oregon)', 'us-west-2', 'AWS'),
('Europe (Ireland)', 'eu-west-1', 'AWS'),
('Asia Pacific (Singapore)', 'ap-southeast-1', 'AWS'),
('Asia Pacific (Tokyo)', 'ap-northeast-1', 'AWS'),
('Canada (Central)', 'ca-central-1', 'AWS'),
('Europe (Frankfurt)', 'eu-central-1', 'AWS'),
('US West (N. California)', 'us-west-1', 'AWS');
