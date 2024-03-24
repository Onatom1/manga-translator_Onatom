import os
import cv2
import numpy as np
import json
from PIL import Image
from manga_ocr import MangaOcr
import easyocr  # Importar easyocr
import re


def preprocess_image(image, clip_limit=2.0, grid_size=(8, 8)):
    if len(image.shape) == 3 and image.shape[2] == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
        enhanced = clahe.apply(gray)
        return enhanced
    else:
        return image


def improve_ocr_result(text):
    # Converter todas as letras maiúsculas para minúsculas
    text = text.lower()
    # Remover pontuação extra usando expressões regulares
    text = re.sub(r'[^\w\s]', '', text)
    return text


def extract_text_to_json(image_folder, coordinates_path, output_json_path, language):
    # Escolher o leitor OCR com base no idioma
    if language == 'ja':
        reader = MangaOcr()
    elif language == 'en':
        reader = easyocr.Reader(['en'], gpu=False)
    else:
        raise ValueError(f'Unsupported language: {language}')

    extracted_text = []
    with open(coordinates_path, 'r', encoding='utf-8') as file:
        coordinates = file.readlines()

        for idx, coord in enumerate(coordinates):
            data = coord.strip().split()
            label = int(data[0])
            coords = list(map(float, data[1:]))

            if len(coords) >= 5:
                x, y, w, h = coords[:4]

                # Verificar se o diretório manga_text existe
                manga_text_dir = os.path.join(image_folder, 'manga_text')
                if not os.path.exists(manga_text_dir):
                    os.makedirs(manga_text_dir)

                crop_path = os.path.join(manga_text_dir, f"image{idx + 1}.jpg")
                if idx == 0:
                    crop_path = os.path.join(manga_text_dir, "image.jpg")

                # Obter as dimensões da imagem de crop
                cropped_image = Image.open(crop_path)
                box_width, box_height = cropped_image.size

                img_array = np.array(cropped_image)
                img_processed = preprocess_image(img_array)

                # Converter o array numpy de volta para um objeto PIL.Image
                img_processed = Image.fromarray(img_processed)

                # Usar o leitor OCR apropriado com base no idioma
                if language == 'ja':
                    result = reader(crop_path)  # Passar o caminho do arquivo diretamente
                    text = result.replace('\n', ' ')
                elif language == 'en':
                    result = reader.readtext(crop_path)  # Passar o caminho do arquivo diretamente
                    text = ' '.join([entry[1] for entry in result])

                text = improve_ocr_result(text)  # Aplicar pós-processamento do texto

                extracted_text.append({
                    'coordinates': (x, y),
                    'text': text.strip(),
                    'box_size': (box_width, box_height)
                })

    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_text, json_file, indent=4, ensure_ascii=False)

    print(f"Texto extraído: {output_json_path}")


if __name__ == "__main__":
    image_folder = 'runs/detect/predict/crops'
    coordinates_path = 'runs/detect/predict/labels/image.txt'
    output_json_path = 'json/coordinates_box_text.json'
    language = 'ja'  # Definir o idioma aqui

    extract_text_to_json(image_folder, coordinates_path, output_json_path, language)
