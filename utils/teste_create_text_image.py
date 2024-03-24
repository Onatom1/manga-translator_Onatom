import os
from PIL import Image, ImageDraw, ImageFont
import json
import textwrap

def create_images_from_json(json_path, output_folder):
    # Verificar se a pasta de saída existe, senão criar
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Carregar os dados do arquivo JSON
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Iterar sobre cada entrada no arquivo JSON
    for i, entry in enumerate(data):
        # Extrair as informações relevantes
        coordinates = entry["coordinates"]
        text = entry["text"]
        box_size = tuple(entry["box_size"])

        # Criar uma nova imagem com base no tamanho do box_size
        image = Image.new('RGB', box_size, color='white')

        # Adicionar o texto ao centro da imagem
        draw = ImageDraw.Draw(image)
        
        # Escolha da fonte e tamanho da fonte
        font_size = 16  # Ajuste o tamanho da fonte conforme desejado
        font = ImageFont.truetype("fonts/ComicNeue-Bold.ttf", font_size)

        # Quebrar o texto em linhas
        lines = textwrap.wrap(text, width=20)  # Defina o comprimento máximo da linha conforme necessário

        # Calcular as dimensões do texto para centralizá-lo verticalmente
        text_bbox = [draw.textbbox((0, 0), line, font=font) for line in lines]
        text_height = sum(box[3] - box[1] for box in text_bbox)

        # Definir um espaço maior entre as linhas
        line_spacing = 15

        # Calcular a posição vertical inicial do texto
        y_text = (box_size[1] - text_height - line_spacing * (len(lines) - 1)) / 2

        # Desenhar o texto em várias linhas
        for line, box in zip(lines, text_bbox):
            # Calcular a largura do texto
            width = box[2] - box[0]
            x_text = (box_size[0] - width) / 2
            draw.text((x_text, y_text), line, fill='black', font=font)
            y_text += box[3] - box[1] + line_spacing  # Adicionar espaço entre as linhas

        # Salvar a imagem resultante na pasta de saída
        image_path = os.path.join(output_folder, f'output_image_{i}.png')
        image.save(image_path)

    print(f"Imagens salvas na pasta '{output_folder}'.")

# Exemplo de uso da função
if __name__ == "__main__":
    json_path = 'texto_extraido.json'
    output_folder = 'boxes'
    create_images_from_json(json_path, output_folder)