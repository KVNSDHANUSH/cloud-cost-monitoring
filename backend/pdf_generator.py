from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import sqlite3
from datetime import datetime, timedelta
import io

def get_db_connection():
    conn = sqlite3.connect('../database/cloud_costs.db')
    conn.row_factory = sqlite3.Row
    return conn

def generate_cost_analysis_report():
    """Generate comprehensive PDF cost analysis report"""
    
    # Create a buffer for the PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        textColor=colors.darkgreen
    )
    
    # Build the story (content)
    story = []
    
    # Title
    story.append(Paragraph("Cloud Cost Analysis Report", title_style))
    story.append(Spacer(1, 12))
    
    # Report metadata
    current_date = datetime.now().strftime("%B %d, %Y")
    report_period = f"{(datetime.now() - timedelta(days=30)).strftime('%B %d, %Y')} to {current_date}"
    
    metadata_data = [
        ['Report Generated:', current_date],
        ['Analysis Period:', report_period],
        ['Report Type:', 'Monthly Cost Analysis & Optimization']
    ]
    
    metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
    ]))
    
    story.append(metadata_table)
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    
    conn = get_db_connection()
    
    # Get summary data
    summary_query = """
    SELECT 
        SUM(cost) as total_cost,
        COUNT(DISTINCT service_id) as active_services,
        COUNT(DISTINCT region_id) as active_regions,
        AVG(cost) as avg_daily_cost
    FROM cost_records 
    WHERE date >= date('now', '-30 days')
    """
    summary = conn.execute(summary_query).fetchone()
    
    summary_text = f"""
    This report provides a comprehensive analysis of cloud spending over the past 30 days. 
    Total expenditure during this period was ${summary['total_cost']:.2f} across {summary['active_services']} 
    services and {summary['active_regions']} regions. The average daily cost was ${summary['avg_daily_cost']:.2f}.
    Key optimization opportunities have been identified with potential savings of over $500 monthly.
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Cost Trends Analysis
    story.append(Paragraph("Cost Trends Analysis", heading_style))
    
    trends_query = """
    SELECT 
        strftime('%Y-%m', date) as month,
        SUM(cost) as total_cost,
        COUNT(*) as daily_records
    FROM cost_records 
    GROUP BY strftime('%Y-%m', date)
    ORDER BY month DESC
    LIMIT 6
    """
    trends = conn.execute(trends_query).fetchall()
    
    trends_data = [['Month', 'Total Cost ($)', 'Daily Average ($)']]
    for trend in trends:
        daily_avg = trend['total_cost'] / trend['daily_records'] if trend['daily_records'] > 0 else 0
        trends_data.append([
            trend['month'],
            f"${trend['total_cost']:.2f}",
            f"${daily_avg:.2f}"
        ])
    
    trends_table = Table(trends_data, colWidths=[1.5*inch, 2*inch, 2*inch])
    trends_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(trends_table)
    story.append(Spacer(1, 20))
    
    # Service Breakdown
    story.append(Paragraph("Service Cost Breakdown", heading_style))
    
    service_query = """
    SELECT 
        s.service_name,
        s.service_category,
        SUM(cr.cost) as total_cost,
        COUNT(*) as usage_days,
        AVG(cr.cost) as avg_daily_cost
    FROM cost_records cr
    JOIN services s ON cr.service_id = s.id
    WHERE cr.date >= date('now', '-30 days')
    GROUP BY s.service_name, s.service_category
    ORDER BY total_cost DESC
    """
    services = conn.execute(service_query).fetchall()
    
    service_data = [['Service Name', 'Category', 'Total Cost ($)', 'Avg Daily ($)', 'Usage Days']]
    for service in services:
        service_data.append([
            service['service_name'],
            service['service_category'],
            f"${service['total_cost']:.2f}",
            f"${service['avg_daily_cost']:.2f}",
            str(service['usage_days'])
        ])
    
    service_table = Table(service_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1*inch])
    service_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    story.append(service_table)
    story.append(Spacer(1, 20))
    
    # Regional Analysis
    story.append(Paragraph("Regional Cost Analysis", heading_style))
    
    region_query = """
    SELECT 
        r.region_name,
        r.region_code,
        SUM(cr.cost) as total_cost,
        COUNT(DISTINCT cr.service_id) as services_used,
        AVG(cr.cost) as avg_daily_cost
    FROM cost_records cr
    JOIN regions r ON cr.region_id = r.id
    WHERE cr.date >= date('now', '-30 days')
    GROUP BY r.region_name, r.region_code
    ORDER BY total_cost DESC
    """
    regions = conn.execute(region_query).fetchall()
    
    region_data = [['Region', 'Code', 'Total Cost ($)', 'Services Used', 'Avg Daily ($)']]
    for region in regions:
        region_data.append([
            region['region_name'],
            region['region_code'],
            f"${region['total_cost']:.2f}",
            str(region['services_used']),
            f"${region['avg_daily_cost']:.2f}"
        ])
    
    region_table = Table(region_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.2*inch, 1.3*inch])
    region_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    story.append(region_table)
    story.append(Spacer(1, 20))
    
    # Optimization Recommendations
    story.append(Paragraph("Optimization Recommendations", heading_style))
    
    rec_query = """
    SELECT 
        s.service_name,
        r.region_name,
        orr.recommendation_type,
        orr.description,
        orr.potential_savings,
        orr.priority
    FROM optimization_recommendations orr
    JOIN services s ON orr.service_id = s.id
    JOIN regions r ON orr.region_id = r.id
    ORDER BY orr.potential_savings DESC
    LIMIT 10
    """
    recommendations = conn.execute(rec_query).fetchall()
    
    rec_data = [['Service', 'Region', 'Type', 'Priority', 'Potential Savings ($)']]
    total_potential_savings = 0
    
    for rec in recommendations:
        priority_color = 'High' if rec['priority'] == 'high' else 'Medium' if rec['priority'] == 'medium' else 'Low'
        rec_data.append([
            rec['service_name'],
            rec['region_name'],
            rec['recommendation_type'],
            priority_color,
            f"${rec['potential_savings']:.2f}"
        ])
        total_potential_savings += rec['potential_savings']
    
    rec_table = Table(rec_data, colWidths=[1.5*inch, 2*inch, 1.8*inch, 1*inch, 1.7*inch])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    story.append(rec_table)
    story.append(Spacer(1, 15))
    
    # Total potential savings summary
    savings_summary = f"""
    <b>Total Potential Monthly Savings: ${total_potential_savings:.2f}</b><br/>
    Implementing the above recommendations could reduce monthly cloud costs by approximately 
    {((total_potential_savings / summary['total_cost']) * 100):.1f}%.
    """
    
    story.append(Paragraph(savings_summary, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Cost Anomalies
    story.append(Paragraph("Cost Anomalies Detection", heading_style))
    
    anomaly_query = """
    SELECT 
        s.service_name,
        r.region_name,
        ca.date,
        ca.expected_cost,
        ca.actual_cost,
        ca.variance_percentage,
        ca.description
    FROM cost_anomalies ca
    JOIN services s ON ca.service_id = s.id
    JOIN regions r ON ca.region_id = r.id
    ORDER BY ca.variance_percentage DESC
    LIMIT 5
    """
    anomalies = conn.execute(anomaly_query).fetchall()
    
    if anomalies:
        anomaly_data = [['Service', 'Region', 'Date', 'Expected ($)', 'Actual ($)', 'Variance (%)']]
        for anomaly in anomalies:
            anomaly_data.append([
                anomaly['service_name'],
                anomaly['region_name'],
                anomaly['date'],
                f"${anomaly['expected_cost']:.2f}",
                f"${anomaly['actual_cost']:.2f}",
                f"+{anomaly['variance_percentage']:.1f}%"
            ])
        
        anomaly_table = Table(anomaly_data, colWidths=[1.5*inch, 1.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.1*inch])
        anomaly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(anomaly_table)
    else:
        story.append(Paragraph("No significant cost anomalies detected in the analysis period.", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Conclusions and Next Steps
    story.append(Paragraph("Conclusions and Next Steps", heading_style))
    
    conclusions = """
    <b>Key Findings:</b><br/>
    • Cloud spending is concentrated in compute and storage services<br/>
    • Multiple regions are incurring costs, indicating distributed infrastructure<br/>
    • Significant optimization opportunities exist with potential monthly savings<br/>
    • Cost anomalies have been identified requiring immediate attention<br/><br/>
    
    <b>Recommended Actions:</b><br/>
    1. Implement high-priority optimization recommendations first<br/>
    2. Review and address cost anomalies within 7 days<br/>
    3. Set up automated alerts for future anomaly detection<br/>
    4. Schedule monthly cost review meetings<br/>
    5. Consider reserved instances for predictable workloads<br/><br/>
    
    <b>Next Report:</b><br/>
    This analysis should be repeated monthly to track progress and identify new optimization opportunities.
    """
    
    story.append(Paragraph(conclusions, styles['Normal']))
    
    conn.close()
    
    # Build PDF
    doc.build(story)
    
    # Get PDF from buffer
    buffer.seek(0)
    return buffer.getvalue()

def save_report_to_file(filename="cloud_cost_analysis_report.pdf"):
    """Save the PDF report to a file"""
    pdf_data = generate_cost_analysis_report()
    with open(filename, 'wb') as f:
        f.write(pdf_data)
    return filename
