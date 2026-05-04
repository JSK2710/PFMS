from flask import Blueprint, render_template, session, send_file, flash, redirect, url_for
from routes.auth import login_required
from models.reports import generate_pdf_report
from models.analysis import get_transactions_df
import pandas as pd
import io
import os

reports_bp = Blueprint('reports', __name__)


# ─────────────────────────────────────────
# REPORTS PAGE
# ─────────────────────────────────────────

@reports_bp.route('/reports')
@login_required
def reports():
    return render_template('reports.html')


# ─────────────────────────────────────────
# DOWNLOAD PDF
# ─────────────────────────────────────────

@reports_bp.route('/download-pdf')
@login_required
def download_pdf():
    try:
        user_id = session['user_id']
        pdf_path = generate_pdf_report(user_id)

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"PFMS_Report_{session['username']}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f"Failed to generate PDF: {str(e)}", "danger")
        return redirect(url_for('reports.reports'))


# ─────────────────────────────────────────
# DOWNLOAD CSV
# ─────────────────────────────────────────

@reports_bp.route('/download-csv')
@login_required
def download_csv():
    try:
        user_id = session['user_id']
        df = get_transactions_df(user_id)

        if df.empty:
            flash("No transactions to export.", "warning")
            return redirect(url_for('reports.reports'))

        # Clean up dataframe for export
        export_df = df[['date', 'category', 'type', 'amount', 'note']].copy()
        export_df.columns = ['Date', 'Category', 'Type', 'Amount (₹)', 'Note']
        export_df['Date'] = export_df['Date'].astype(str).str[:10]

        # Convert to CSV in memory
        output = io.StringIO()
        export_df.to_csv(output, index=False)
        output.seek(0)

        # Convert to bytes
        csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))

        return send_file(
            csv_bytes,
            as_attachment=True,
            download_name=f"PFMS_Transactions_{session['username']}.csv",
            mimetype='text/csv'
        )
    except Exception as e:
        flash(f"Failed to export CSV: {str(e)}", "danger")
        return redirect(url_for('reports.reports'))