from PIL import Image, ImageDraw, ImageFont
import json
import textwrap

def calculate_font_size(text, box_width, box_height):
    # Define o tamanho máximo da fonte
    max_font_size = min(box_width, box_height) * 0.8

    # Inicializa o tamanho da fonte
    fontsize = 1

    # Cria uma imagem temporária para usar o objeto ImageDraw
    temp_img = Image.new('RGB', (1, 1))

    # Cria um objeto ImageDraw associado à imagem temporária
    draw = ImageDraw.Draw(temp_img)

    # Define a fonte padrão
    font = ImageFont.truetype("fonts/ComicNeue-Bold.ttf", fontsize)

    # Divide o texto em linhas
    lines = textwrap.wrap(text, width=15)

    # Loop para encontrar o tamanho de fonte apropriado
    while True:
        # Calcula a largura total do texto
        text_width = max(draw.textlength(line, font=font) for line in lines)

        # Calcula a altura total do texto
        text_height = fontsize * len(lines)

        # Verifica se o tamanho da fonte é apropriado
        if text_width > box_width or text_height > box_height or fontsize >= max_font_size:
            break

        fontsize += 1
        font = ImageFont.truetype("fonts/ComicNeue-Bold.ttf", fontsize)

    return fontsize

def calculate_line_spacing(text, box_height):
    # Define o espaçamento máximo entre linhas
    max_line_spacing = box_height * 0.1

    # Calcula o número de linhas
    num_lines = len(textwrap.wrap(text, width=15))

    # Ajusta o espaçamento entre linhas
    line_spacing = max_line_spacing / (num_lines - 1) if num_lines > 1 else 0

    return line_spacing

def insert_text_on_image(image_path, json_path, save_path):
    # Carrega a imagem original
    original_image = Image.open(image_path)

    # Carrega o arquivo JSON com coordenadas, texto e tamanho da caixa
    with open(json_path, 'r', encoding='utf-8') as json_file:
        extracted_data = json.load(json_file)

    # Obtém as dimensões da imagem original
    original_width, original_height = original_image.size

    # Para cada texto extraído, cria uma caixa em branco com o texto
    for item in extracted_data:
        text = item['text']
        if text is None or text.strip() == '':
            continue  # Pula para o próximo item se o texto estiver vazio
        coordinates = item['coordinates']
        box_size = item['box_size']
        x, y = coordinates
        box_width, box_height = box_size

        # Calcula a posição onde o texto deve ser colocado na imagem original
        x_pos = int(x * original_width)
        y_pos = int(y * original_height)

        # Ajusta a posição para que a caixa de texto fique centralizada em relação às coordenadas
        x_pos -= box_width // 2
        y_pos -= box_height // 2

        # Cria uma nova imagem com fundo transparente
        text_image = Image.new('RGBA', (box_width, box_height), (255, 255, 255, 0))
        draw_text = ImageDraw.Draw(text_image)

        # Quebra o texto em linhas
        lines = textwrap.wrap(text, width=15)

        # Define o tamanho da fonte
        fontsize = calculate_font_size(text, box_width, box_height)

        # Ajusta o espaçamento entre linhas
        line_spacing = calculate_line_spacing(text, box_height)

        # Define a fonte e o tamanho da fonte
        font = ImageFont.truetype("fonts/ComicNeue-Bold.ttf", fontsize)

        # Calcula a altura total do texto
        text_height = fontsize * len(lines)

        # Desenha a caixa com cantos arredondados
        roundness = 20  # Ajuste esse valor para alterar a curvatura dos cantos
        draw_text.polygon([(roundness, 0), (box_width-roundness, 0), (box_width, roundness), 
                           (box_width, box_height-roundness), (box_width-roundness, box_height), 
                           (roundness, box_height), (0, box_height-roundness), (0, roundness)], 
                          fill=(255, 255, 255, 255))

        # Desenha o texto na imagem
        y_text = (box_height - text_height - (len(lines) - 1) * line_spacing) / 2
        for line in lines:
            # Calcula a posição horizontal do texto para centralizá-lo na caixa
            x_text = (box_width - draw_text.textlength(line, font=font)) / 2

            # Desenha o texto na imagem
            draw_text.text((x_text, y_text), line, fill='black', font=font)

            # Atualiza a posição vertical para a próxima linha
            y_text += fontsize + line_spacing

        # Cola a caixa de texto na imagem original
        original_image.paste(text_image, (x_pos, y_pos), mask=text_image)

    # Salva a imagem final
    original_image.save(save_path)


