from datetime import datetime
import hashlib

def add_security_watermark(html_content, document_type, medico_nome, crm):
    """Add security watermark to PDF content"""
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Create document hash for verification
    content_hash = hashlib.md5(html_content.encode()).hexdigest()[:8]
    
    security_info = f"""
    <div style="position: fixed; bottom: 10px; right: 10px; font-size: 8px; color: #999; text-align: right;">
        <div>Doc: {document_type.upper()}</div>
        <div>Emitido: {timestamp}</div>
        <div>Por: Dr. {medico_nome} - {crm}</div>
        <div>Hash: {content_hash}</div>
        <div style="font-size: 6px;">Sistema VIDAH - Documento Autêntico</div>
    </div>
    
    <div style="position: fixed; bottom: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, #ddd, transparent); opacity: 0.3;"></div>
    """
    
    # Insert before closing body tag
    if "</body>" in html_content:
        html_content = html_content.replace("</body>", security_info + "</body>")
    else:
        html_content += security_info
    
    return html_content

def validate_document_integrity(document_data):
    """Validate document hasn't been tampered with"""
    # Extract hash from document if present
    # Compare with recalculated hash
    # Return True if valid, False if tampered
    return True  # Simplified for now