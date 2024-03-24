from ultralytics import YOLO
import os
import shutil

def detect_and_save_balloons(image_path, save_path):
    # Inicializar o modelo YOLO com o arquivo best.pt
    model = YOLO('dataset/manga_balloon2.pt')

    # Realizar a detecção na imagem especificada
    results_img = model.predict(source=image_path,
                                 conf=0.25,
                                 iou=0.7,
                                 imgsz=640,
                                 show=False,
                                 save=True,
                                 save_txt=True,
                                 save_conf=True,
                                 save_crop=True,
                                 stream=False,
                                 name='predict')  # Nome do arquivo de saída

    return results_img

# Exemplo de uso da função
if __name__ == "__main__":
    # Caminho da imagem a ser processada
    image_path = 'manga.png'

    # Caminho para salvar os resultados
    save_path = 'runs/detect'

    # Verificar se a pasta de saída existe e removê-la
    predict_path = os.path.join(save_path, 'predict')
    if os.path.exists(predict_path):
        shutil.rmtree(predict_path)

    # Chamar a função para detectar e salvar balões
    results = detect_and_save_balloons(image_path, save_path)

    print(results)
