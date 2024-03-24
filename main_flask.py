import json
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from utils.manga_coordinates_balloon import detect_and_save_balloons
from utils.text_extract import extract_text_to_json
from utils.inserir_imagem import insert_text_on_image
from utils.translator import translate_json
import os
import shutil
import base64

app = Flask(__name__)

# Configurações para o upload de arquivos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota para renderizar o formulário de upload
@app.route('/')
def upload_form():
    return render_template('upload.html')

# Rota para processar a imagem
@app.route('/process_image', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nome do arquivo vazio'}), 400

    if file and allowed_file(file.filename):
        filename = "image.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Caminho para salvar os resultados
        save_path = 'runs/detect'

        # Verificar se a pasta de saída existe e removê-la
        predict_path = os.path.join(save_path, 'predict')
        if os.path.exists(predict_path):
            shutil.rmtree(predict_path)

        # Chamar a função para detectar e salvar balões
        detect_and_save_balloons(filepath, save_path)

        # Caminho do arquivo de coordenadas
        coordinates_path = os.path.join(save_path, 'predict', 'labels', os.path.splitext(filename)[0] + '.txt')

        # Caminho de saída do arquivo JSON com os dados extraídos
        output_json_path = os.path.join('json', 'coordinates_box_text.json')
        
        # Obter o idioma selecionado
        language = request.form.get('language')

        # Chamar a função para extrair o texto das coordenadas e salvar em um arquivo JSON
        extract_text_to_json('runs/detect/predict/crops', coordinates_path, output_json_path, language)

        json_file_path = 'json/coordinates_box_text.json'
        translate_json(json_file_path)
        
        # Gerar o nome do arquivo de imagem combinada
        combined_image_path = filepath

        # Chamar a função para inserir o texto na imagem
        insert_text_on_image(filepath, output_json_path, combined_image_path)

        # Codificar a imagem processada como base64
        with open(combined_image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        # Retorna a imagem processada como um dado base64 codificado em URL
        return render_template('upload.html', img_data=encoded_string)
    else:
        return jsonify({'error': 'Formato de arquivo não suportado'}), 400

if __name__ == "__main__":
    app.run(debug=True)
