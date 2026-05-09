import sqlite3
import random
from datetime import datetime, timedelta
import os

def init_database():
    # Create database directory if it doesn't exist
    os.makedirs('../database', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('../database/cloud_costs.db')
    cursor = conn.cursor()
    
    # Read and execute schema
    with open('../database/schema.sql', 'r') as f:
        schema = f.read()
    
    cursor.executescript(schema)
    
    # Generate sample cost data for the last 12 months
    services = list(range(1, 11))  # 10 services
    regions = list(range(1, 8))    # 7 regions
    
    start_date = datetime.now() - timedelta(days=365)
    
    for day in range(365):
        current_date = start_date + timedelta(days=day)
        
        for service_id in services:
            for region_id in regions:
                # Generate random cost data
                base_cost = random.uniform(10, 500)
                usage_multiplier = random.uniform(0.5, 2.0)
                cost = round(base_cost * usage_multiplier, 2)
                
                cursor.execute('''
                    INSERT INTO cost_records (service_id, region_id, date, cost, usage_hours, resource_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (service_id, region_id, current_date.date(), cost, 
                      random.uniform(1, 24), random.randint(1, 10)))
    
    # Generate sample idle resources
    for service_id in services[:5]:  # First 5 services
        for region_id in regions:
            if random.random() > 0.7:  # 30% chance of idle resource
                cursor.execute('''
                    INSERT INTO resource_utilization 
                    (service_id, region_id, resource_id, utilization_percentage, last_active_date, is_idle)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (service_id, region_id, f'res-{random.randint(1000, 9999)}',
                      random.uniform(0, 20),  # Low utilization
                      (datetime.now() - timedelta(days=random.randint(1, 30))).date(),
                      True))
    
    # Generate sample optimization recommendations
    recommendation_types = [
        'Resize instances', 'Delete unused resources', 'Switch to reserved instances',
        'Optimize storage', 'Implement auto-scaling', 'Use spot instances'
    ]
    
    for service_id in services:
        for region_id in regions:
            if random.random() > 0.6:  # 40% chance of recommendation
                cursor.execute('''
                    INSERT INTO optimization_recommendations 
                    (service_id, region_id, recommendation_type, description, potential_savings, priority)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (service_id, region_id, random.choice(recommendation_types),
                      f'Optimize {random.choice(["compute", "storage", "network"])} resources',
                      round(random.uniform(50, 500), 2),
                      random.choice(['high', 'medium', 'low'])))
    
    # Generate sample cost anomalies
    for service_id in services:
        for region_id in regions:
            if random.random() > 0.8:  # 20% chance of anomaly
                expected_cost = random.uniform(100, 1000)
                actual_cost = expected_cost * random.uniform(1.5, 3.0)
                variance = ((actual_cost - expected_cost) / expected_cost) * 100
                
                cursor.execute('''
                    INSERT INTO cost_anomalies 
                    (service_id, region_id, date, expected_cost, actual_cost, variance_percentage, anomaly_type, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (service_id, region_id, 
                      (datetime.now() - timedelta(days=random.randint(1, 60))).date(),
                      round(expected_cost, 2), round(actual_cost, 2),
                      round(variance, 2), 'spike', 'Unusual cost increase detected'))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully with sample data!")

if __name__ == '__main__':
    init_database()
