import io
import csv as csv_module
from utils.pdf import generate_pdf_report
from utils.firebase import upload_bytes_to_storage

def get_pdf_response(entry, settings, user_info, is_inline=False):
    """
    Generate PDF report bytes and return (pdf_bytes, filename, error_msg).
    """
    pdf_bytes = generate_pdf_report(entry, settings, user_info)
    if pdf_bytes is None:
        return None, None, "PDF generation failed. ReportLab may be missing."
    
    filename = f"report_{str(entry.get('id', 'report'))[:8]}.pdf"
    return pdf_bytes, filename, None


def get_csv_summary_bytes(entry):
    """Generate CSV report summary content for download."""
    buf = io.StringIO()
    writer = csv_module.writer(buf)
    writer.writerow(['Field', 'Value'])
    writer.writerow(['Timestamp', entry.get('timestamp', '')])
    writer.writerow(['Filename', entry.get('filename', '')])
    writer.writerow(['Peak Wavelength (nm)', entry.get('peak_wavelength', '')])
    writer.writerow(['Peak Absorbance (AU)', entry.get('peak_absorbance', '')])
    writer.writerow(['Predicted Concentration (ppm)', entry.get('predicted_concentration', '')])
    writer.writerow(['ML Algorithm', entry.get('algorithm', 'Random Forest Regressor')])
    writer.writerow(['Model Accuracy (R2 %)', entry.get('accuracy_percentage', '')])
    writer.writerow(['RMSE', entry.get('rmse', '')])
    writer.writerow(['MAE', entry.get('mae', '')])
    writer.writerow(['Status', entry.get('status', '')])
    writer.writerow(['Confidence Score (%)', entry.get('confidence_score', '')])
    writer.writerow(['Interpretation', entry.get('interpretation', '')])
    writer.writerow(['Conclusion', entry.get('conclusion', '')])
    return buf.getvalue().encode('utf-8')
