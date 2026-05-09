from flask import Flask, render_template, jsonify, request, send_file
import sqlite3
import json
import io
from datetime import datetime, timedelta
import random
from pdf_generator import generate_cost_analysis_report

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')

def get_db_connection():
    conn = sqlite3.connect('../database/cloud_costs.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/monthly-trends')
def monthly_trends():
    conn = get_db_connection()
    query = """
    SELECT 
        strftime('%Y-%m', date) as month,
        SUM(cost) as total_cost
    FROM cost_records 
    GROUP BY strftime('%Y-%m', date)
    ORDER BY month
    """
    data = conn.execute(query).fetchall()
    conn.close()
    
    months = [row['month'] for row in data]
    costs = [float(row['total_cost']) for row in data]
    
    return jsonify({'months': months, 'costs': costs})

@app.route('/api/service-breakdown')
def service_breakdown():
    conn = get_db_connection()
    query = """
    SELECT 
        s.service_name,
        SUM(cr.cost) as total_cost
    FROM cost_records cr
    JOIN services s ON cr.service_id = s.id
    GROUP BY s.service_name
    ORDER BY total_cost DESC
    """
    data = conn.execute(query).fetchall()
    conn.close()
    
    services = [row['service_name'] for row in data]
    costs = [float(row['total_cost']) for row in data]
    
    return jsonify({'services': services, 'costs': costs})

@app.route('/api/region-analysis')
def region_analysis():
    conn = get_db_connection()
    query = """
    SELECT 
        r.region_name,
        SUM(cr.cost) as total_cost
    FROM cost_records cr
    JOIN regions r ON cr.region_id = r.id
    GROUP BY r.region_name
    ORDER BY total_cost DESC
    """
    data = conn.execute(query).fetchall()
    conn.close()
    
    regions = [row['region_name'] for row in data]
    costs = [float(row['total_cost']) for row in data]
    
    return jsonify({'regions': regions, 'costs': costs})

@app.route('/api/idle-resources')
def idle_resources():
    conn = get_db_connection()
    query = """
    SELECT 
        s.service_name,
        r.region_name,
        COUNT(*) as idle_count
    FROM resource_utilization ru
    JOIN services s ON ru.service_id = s.id
    JOIN regions r ON ru.region_id = r.id
    WHERE ru.is_idle = 1
    GROUP BY s.service_name, r.region_name
    """
    data = conn.execute(query).fetchall()
    conn.close()
    
    idle_data = []
    for row in data:
        idle_data.append({
            'service': row['service_name'],
            'region': row['region_name'],
            'count': row['idle_count']
        })
    
    return jsonify(idle_data)

@app.route('/api/recommendations')
def recommendations():
    conn = get_db_connection()
    query = """
    SELECT 
        s.service_name,
        r.region_name,
        orr.description,
        orr.potential_savings,
        orr.priority,
        orr.status
    FROM optimization_recommendations orr
    JOIN services s ON orr.service_id = s.id
    JOIN regions r ON orr.region_id = r.id
    ORDER BY orr.potential_savings DESC
    """
    data = conn.execute(query).fetchall()
    conn.close()
    
    recommendations = []
    for row in data:
        recommendations.append({
            'service': row['service_name'],
            'region': row['region_name'],
            'description': row['description'],
            'potential_savings': float(row['potential_savings']),
            'priority': row['priority'],
            'status': row['status']
        })
    
    return jsonify(recommendations)

@app.route('/api/download-report')
def download_report():
    """Generate and download PDF cost analysis report"""
    try:
        pdf_data = generate_cost_analysis_report()
        
        # Create filename with current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"cloud_cost_analysis_report_{current_date}.pdf"
        
        # Return PDF as downloadable file
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
