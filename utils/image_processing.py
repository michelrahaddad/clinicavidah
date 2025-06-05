"""
Processamento de assinaturas para PDFs médicos
"""
import base64
import io
from PIL import Image, ImageOps, ImageEnhance
import logging

def create_black_signature(signature_data):
    """
    Processa assinatura para aparecer em preto visível no PDF
    
    Args:
        signature_data (str): Data URL da assinatura
    
    Returns:
        str: Data URL da assinatura processada
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
        
        # Cria uma nova imagem RGB com fundo branco
        width, height = image.size
        processed_image = Image.new('RGB', (width, height), 'white')
        
        # Processa pixel por pixel para converter transparências em preto
        for y in range(height):
            for x in range(width):
                r, g, b, a = image.getpixel((x, y))
                
                # Se o pixel tem alguma opacidade (não é totalmente transparente)
                if a > 50:  # Threshold para considerar como parte da assinatura
                    # Calcula intensidade do pixel
                    intensity = (r + g + b) / 3
                    
                    # Se o pixel é escuro ou tem boa opacidade, torna preto
                    if intensity < 200 or a > 150:
                        processed_image.putpixel((x, y), (0, 0, 0))  # Preto
                    else:
                        processed_image.putpixel((x, y), (255, 255, 255))  # Branco
                else:
                    # Pixel transparente vira branco
                    processed_image.putpixel((x, y), (255, 255, 255))
        
        # Salva como PNG
        output_buffer = io.BytesIO()
        processed_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        processed_data = base64.b64encode(output_buffer.getvalue()).decode()
        return f"data:image/png;base64,{processed_data}"
        
    except Exception as e:
        logging.error(f"Erro ao processar assinatura: {e}")
        return signature_data  # Retorna original se houver erro