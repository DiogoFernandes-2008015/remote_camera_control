import cv2
from flask import Flask, render_template, Response, request, jsonify
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import os
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Garante que a pasta de capturas exista para o Snapshot não falhar
CAPTURAS_PATH = os.path.join(os.path.expanduser("~"), "projeto00/capturas")
if not os.path.exists(CAPTURAS_PATH):
    os.makedirs(CAPTURAS_PATH)

# Configuração dos Servos
try:
    factory = PiGPIOFactory()
    pan = Servo(12, pin_factory=factory, min_pulse_width=0.0006, max_pulse_width=0.0024)
    tilt = Servo(13, pin_factory=factory, min_pulse_width=0.0006, max_pulse_width=0.0024)
    print("Servos configurados com sucesso!")
except Exception as e:
    print(f"Erro ao configurar servos: {e}")

# Variáveis de controle de posição e velocidade
pos_pan = 0.0
pos_tilt = 0.0
passo_suave = 0.02  # Altere aqui para deixar mais rápido ou mais lento (padrão: 0.02)
comando_atual = "stop"

camera = cv2.VideoCapture(0)

# Loop em segundo plano para suavizar o movimento (suporte a manter pressionado)
def loop_movimento_suave():
    global pos_pan, pos_tilt, comando_atual
    while True:
        if comando_atual == "up":
            pos_tilt = min(1.0, pos_tilt + passo_suave)
        elif comando_atual == "down":
            pos_tilt = max(-1.0, pos_tilt - passo_suave)
        elif comando_atual == "left":
            pos_pan = min(1.0, pos_pan + passo_suave)
        elif comando_atual == "right":
            pos_pan = max(-1.0, pos_pan - passo_suave)
        elif comando_atual == "center":
            pos_pan = 0.0
            pos_tilt = 0.0
            # Força os motores a irem para o centro imediatamente
            try:
                pan.value = 0.0
                tilt.value = 0.0
            except Exception:
                pass
            comando_atual = "stop" # Trava o movimento no centro

        # Aplica a posição nos motores continuamente (se não for stop)
        if comando_atual != "stop":
            try:
                pan.value = pos_pan
                tilt.value = pos_tilt
            except Exception:
                pass
        
        time.sleep(0.02)
# Inicia a thread de movimento contínuo
threading.Thread(target=loop_movimento_suave, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def gerar_frames():
        while True:
            success, frame = camera.read()
            if not success: break
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return Response(gerar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control')
def control():
    global comando_atual
    direction = request.args.get('direction')
    
    if direction in ['up', 'down', 'left', 'right', 'center', 'stop']:
        comando_atual = direction
        
    return f"Comando alterado para {direction}"

@app.route('/status')
def status():
    p = round(pan.value * 90) if pan.value is not None else 0
    t = round(tilt.value * 90) if tilt.value is not None else 0
    return jsonify({'pan': p, 'tilt': t})

# ROTA RECUPERADA: Salva os prints da inspeção
@app.route('/snapshot')
def snapshot():
    global pos_pan, pos_tilt
    success, frame = camera.read()
    if success:
        ang_p = round(pos_pan * 90)
        ang_t = round(pos_tilt * 90)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"snap_{timestamp}_P{ang_p}_T{ang_t}.jpg"
        caminho = os.path.join(CAPTURAS_PATH, nome_arquivo)
        
        cv2.imwrite(caminho, frame)
        print(f"Foto salva em: {caminho}")
        return jsonify({'status': 'sucesso', 'arquivo': nome_arquivo})
        
    return jsonify({'status': 'erro'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
