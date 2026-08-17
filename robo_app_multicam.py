import cv2
from flask import Flask, render_template, Response, request, jsonify
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import os
from datetime import datetime

app = Flask(__name__)

# Configuração dos Servos
factory = PiGPIOFactory()
pan = Servo(12, pin_factory=factory, min_pulse_width=0.0006, max_pulse_width=0.0024)
tilt = Servo(13, pin_factory=factory, min_pulse_width=0.0006, max_pulse_width=0.0024)

# Estado inicial
pos_pan = 0.0
pos_tilt = 0.0
passo = 0.15

# Verifique se suas câmeras não estão usando os índices 0 e 2 
# (Alguns modelos USB ocupam o 0 e 1 para a mesma câmera)
cam_inspecao = cv2.VideoCapture(0)
cam_direcao = cv2.VideoCapture(1) 

def gerar_frames():
    global camera_ativa
    while True:
        # Seleciona o objeto de captura correto a cada iteração
        if camera_ativa == "inspecao":
            success, frame = cam_inspecao.read()
        else:
            success, frame = cam_direcao.read()

        if not success:
            continue

        # Codificação JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
@app.route('/')
def index():
    return render_template('indexmc.html')

@app.route('/video_feed')
def video_feed():
    return Response(gerar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control')
def control():
    global pos_pan, pos_tilt
    direction = request.args.get('direction')
    
    if direction == 'up': pos_tilt = min(1.0, pos_tilt + passo)
    elif direction == 'down': pos_tilt = max(-1.0, pos_tilt - passo)
    elif direction == 'left': pos_pan = min(1.0, pos_pan + passo)
    elif direction == 'right': pos_pan = max(-1.0, pos_pan - passo)
    elif direction == 'center': pos_pan, pos_tilt = 0.0, 0.0
    
    pan.value = pos_pan
    tilt.value = pos_tilt
    return "OK"

@app.route('/status')
def status():
    # Converte o valor de -1.0 a 1.0 para graus (-90 a 90)
    angulo_pan = round(pan.value * 90) if pan.value is not None else 0
    angulo_tilt = round(tilt.value * 90) if tilt.value is not None else 0
    
    return jsonify({
        'pan': angulo_pan,
        'tilt': angulo_tilt
    })
    
@app.route('/snapshot')
def snapshot():
    global pos_pan, pos_tilt
    
    # Captura um frame limpo da câmera
    success, frame = camera.read()
    
    if success:
        # Converte valores para graus para o nome do arquivo
        ang_p = round(pos_pan * 90)
        ang_t = round(pos_tilt * 90)
        
        # Gera nome do arquivo com data, hora e ângulos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"snap_{timestamp}_P{ang_p}_T{ang_t}.jpg"
        caminho = os.path.join(os.path.expanduser("~"), "projeto00/capturas", nome_arquivo)
        
        # Salva a imagem
        cv2.imwrite(caminho, frame)
        print(f"Foto salva: {nome_arquivo}")
        return jsonify({'status': 'sucesso', 'arquivo': nome_arquivo})
    
    return jsonify({'status': 'erro'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
