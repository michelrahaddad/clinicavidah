"""
Processamento de assinaturas para PDFs médicos
"""
import base64
import io
from PIL import Image, ImageOps, ImageEnhance
import logging

def create_black_signature(signature_data):
    """
    Converte assinatura digital para preto sólido
    
    Args:
        signature_data (str): Data URL da assinatura
    
    Returns:
        str: Data URL da assinatura processada em preto
    """
    try:
        if not signature_data or not signature_data.startswith('data:image'):
            return signature_data
        
        # Extrai os dados base64 da imagem
        header, encoded = signature_data.split(',', 1)
        image_data = base64.b64decode(encoded)
        
        # Abre a imagem
        image = Image.open(io.BytesIO(image_data))
        
        # Converte para RGBA se necessário
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Converte para RGB com fundo branco
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'RGBA':
            background.paste(image, mask=image.split()[-1])
        else:
            background.paste(image)
        
        # Converte para escala de cinza
        grayscale = background.convert('L')
        
        # Aumenta contraste drasticamente
        enhancer = ImageEnhance.Contrast(grayscale)
        high_contrast = enhancer.enhance(5.0)
        
        # Aplica threshold para binarizar (preto/branco) 
        def threshold_func(pixel):
            return 0 if pixel < 200 else 255
        binary = high_contrast.point(threshold_func, mode='1')
        
        # Converte de volta para RGB
        final_image = binary.convert('RGB')
        
        # Inverte se necessário (garante que texto seja preto)
        pixels = list(final_image.getdata())
        black_count = sum(1 for r, g, b in pixels if r < 50 and g < 50 and b < 50)
        white_count = sum(1 for r, g, b in pixels if r > 200 and g > 200 and b > 200)
        
        if black_count < white_count * 0.1:  # Se quase não há preto, inverte
            final_image = ImageOps.invert(final_image)
        
        # Salva como PNG
        output_buffer = io.BytesIO()
        final_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        processed_data = base64.b64encode(output_buffer.getvalue()).decode()
        return f"data:image/png;base64,{processed_data}"
        
    except Exception as e:
        logging.error(f"Erro ao processar assinatura: {e}")
        return signature_data  # Retorna original se houver erro