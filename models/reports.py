import os
import io
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image, HRFlowable
)
from reportlab.graphics.shapes import Drawing
from datetime import datetime
from models.analysis import get_spending_analysis, get_transactions_df
from database.db_connection import get_user_by_id

# Output folder for charts
CHARTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)


# ─────────────────────────────────────────
# GENERATE CHARTS WITH MATPLOTLIB
# ─────────────────────────────────────────

def generate_pie_chart(category_breakdown, user_id):
    """Generate expense pie chart and save as PNG"""
    if not category_breakdown:
        return None

    chart_path = os.path.join(CHARTS_DIR, f'pie_{user_id}.png')

    labels = [c['category'] for c in category_breakdown]
    values = [c['total'] for c in category_breakdown]
    colors_list = [
        '#ef476f', '#f78c6b', '#ffd166', '#06d6a0',
        '#4cc9f0', '#4361ee', '#b5179e', '#7209b7',
        '#560bad', '#480ca8'
    ]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        autopct='%1.1f%%',
        colors=colors_list[:len(labels)],
        startangle=140,
        pctdistance=0.82,
        wedgeprops=dict(width=0.6, edgecolor='#1a1a2e', linewidth=2)
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(8)

    ax.legend(
        wedges, labels,
        loc='center left',
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=8,
        facecolor='#1a1a2e',
        edgecolor='none',
        labelcolor='white'
    )

    ax.set_title('Expense Distribution by Category',
                 color='white', fontsize=11, pad=15, fontweight='bold')

    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()

    return chart_path


def generate_bar_chart(monthly_trends, user_id):
    """Generate monthly income vs expense bar chart and save as PNG"""
    if not monthly_trends:
        return None

    chart_path = os.path.join(CHARTS_DIR, f'bar_{user_id}.png')

    months = [t['month'] for t in monthly_trends]
    income_vals = [t['income'] for t in monthly_trends]
    expense_vals = [t['expense'] for t in monthly_trends]

    x = range(len(months))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    bars1 = ax.bar([i - width/2 for i in x], income_vals,
                   width, label='Income', color='#06d6a0',
                   alpha=0.85, edgecolor='none')
    bars2 = ax.bar([i + width/2 for i in x], expense_vals,
                   width, label='Expense', color='#ef476f',
                   alpha=0.85, edgecolor='none')

    ax.set_xticks(list(x))
    ax.set_xticklabels(months, color='white', fontsize=8, rotation=15)
    ax.tick_params(colors='white')
    ax.yaxis.set_tick_params(labelcolor='white')

    # ✅ Fixed — use tuples instead of CSS rgba strings
    ax.spines['bottom'].set_color((1, 1, 1, 0.15))
    ax.spines['left'].set_color((1, 1, 1, 0.15))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_facecolor('#1a1a2e')
    ax.grid(axis='y', color='white', alpha=0.08, linestyle='--')

    ax.set_title('Monthly Income vs Expenses',
                 color='white', fontsize=11, pad=15, fontweight='bold')
    ax.legend(facecolor='#1a1a2e', edgecolor='none',
              labelcolor='white', fontsize=9)

    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()

    return chart_path


# ─────────────────────────────────────────
# GENERATE PDF REPORT
# ─────────────────────────────────────────

def generate_pdf_report(user_id):
    """Generate a full PDF financial report for a user"""

    # Get data
    analysis = get_spending_analysis(user_id)
    user = get_user_by_id(user_id)
    df = get_transactions_df(user_id)

    # Output path
    report_path = os.path.join(CHARTS_DIR, f'report_{user_id}.pdf')

    # Setup document
    doc = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=colors.HexColor('#4cc9f0'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#888888'),
        spaceAfter=4,
        alignment=TA_CENTER
    )

    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#ffffff'),
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#1a1a2e'),
        leftIndent=-10,
        rightIndent=-10,
        leading=20
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#cccccc'),
        spaceAfter=4
    )

    # Build content
    content = []
    generated_at = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    username = user['username'] if user else 'User'

    # ── Header ──
    content.append(Paragraph("💰 PFMS", title_style))
    content.append(Paragraph("Personal Finance Management System", subtitle_style))
    content.append(Paragraph(f"Financial Report for <b>{username}</b>", subtitle_style))
    content.append(Paragraph(f"Generated on {generated_at}", subtitle_style))
    content.append(Spacer(1, 0.3*inch))
    content.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor('#4cc9f0'), spaceAfter=16))

    if not analysis['has_data']:
        content.append(Paragraph("No transaction data available.", normal_style))
        doc.build(content)
        return report_path

    # ── Summary Section ──
    content.append(Paragraph("📊 Financial Summary", section_style))

    summary_data = [
        ['Metric', 'Amount'],
        ['Total Income', f"₹{analysis['total_income']:,.2f}"],
        ['Total Expenses', f"₹{analysis['total_expense']:,.2f}"],
        ['Balance', f"₹{analysis['balance']:,.2f}"],
        ['Savings Rate', f"{analysis['savings_rate']}%"],
        ['Total Transactions', str(analysis['total_transactions'])],
        ['Avg Daily Expense', f"₹{analysis['avg_daily_expense']:,.2f}"],
        ['Avg Monthly Expense', f"₹{analysis['avg_monthly_expense']:,.2f}"],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4cc9f0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#1a1a2e')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor('#1a1a2e'), colors.HexColor('#16213e')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    content.append(summary_table)
    content.append(Spacer(1, 0.2*inch))

    # ── Pie Chart ──
    if analysis['category_breakdown']:
        pie_path = generate_pie_chart(analysis['category_breakdown'], user_id)
        if pie_path and os.path.exists(pie_path):
            content.append(Paragraph("📈 Expense Distribution", section_style))
            img = Image(pie_path, width=5.5*inch, height=3.5*inch)
            content.append(img)
            content.append(Spacer(1, 0.2*inch))

    # ── Bar Chart ──
    if analysis['monthly_trends']:
        bar_path = generate_bar_chart(analysis['monthly_trends'], user_id)
        if bar_path and os.path.exists(bar_path):
            content.append(Paragraph("📅 Monthly Income vs Expenses", section_style))
            img = Image(bar_path, width=5.5*inch, height=3*inch)
            content.append(img)
            content.append(Spacer(1, 0.2*inch))

    # ── Category Breakdown Table ──
    if analysis['category_breakdown']:
        content.append(Paragraph("💸 Category Breakdown", section_style))
        cat_data = [['Category', 'Amount', 'Percentage']]
        for item in analysis['category_breakdown']:
            cat_data.append([
                item['category'],
                f"₹{item['total']:,.2f}",
                f"{item['percentage']}%"
            ])

        cat_table = Table(cat_data, colWidths=[3*inch, 2*inch, 2*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef476f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.HexColor('#1a1a2e'), colors.HexColor('#16213e')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        content.append(cat_table)
        content.append(Spacer(1, 0.2*inch))

    # ── Monthly Trends Table ──
    if analysis['monthly_trends']:
        content.append(Paragraph("📅 Monthly Trends", section_style))
        month_data = [['Month', 'Income', 'Expense', 'Balance']]
        for row in analysis['monthly_trends']:
            month_data.append([
                row['month'],
                f"₹{row['income']:,.2f}",
                f"₹{row['expense']:,.2f}",
                f"₹{row['balance']:,.2f}"
            ])

        month_table = Table(month_data,
                            colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
        month_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4361ee')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.HexColor('#1a1a2e'), colors.HexColor('#16213e')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        content.append(month_table)
        content.append(Spacer(1, 0.2*inch))

    # ── Recent Transactions Table ──
    if not df.empty:
        content.append(Paragraph("🕐 Recent Transactions (Last 10)", section_style))
        recent_df = df.head(10)
        trans_data = [['Date', 'Category', 'Type', 'Amount', 'Note']]
        for _, row in recent_df.iterrows():
            trans_data.append([
                str(row['date'])[:10],
                row['category'],
                row['type'].capitalize(),
                f"₹{row['amount']:,.2f}",
                str(row['note'])[:20] if row['note'] else '—'
            ])

        trans_table = Table(trans_data,
                            colWidths=[1.2*inch, 1.5*inch, 1*inch, 1.3*inch, 2*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#06d6a0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.HexColor('#1a1a2e'), colors.HexColor('#16213e')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        content.append(trans_table)
        content.append(Spacer(1, 0.2*inch))

    # ── Footer ──
    content.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor('#333333'), spaceBefore=16))
    content.append(Paragraph(
        f"Generated by PFMS — Personal Finance Management System · {generated_at}",
        subtitle_style
    ))

    # Build PDF
    doc.build(content)
    return report_path