from flask import Flask, render_template, request, jsonify
import threading
import time

app = Flask(__name__)

# Состояние ПК и время
pc_states = {"pc1": False, "pc2": False}
pc_timestamps = {"pc1": None, "pc2": None}
timeout_timers = {"pc1": None, "pc2": None}

global_lock = threading.Lock()

# Функция сброса состояния ПК
def reset_pc_states():
    global pc_states, pc_timestamps
    with global_lock:
        pc_states["pc1"] = False
        pc_states["pc2"] = False
        pc_timestamps["pc1"] = None
        pc_timestamps["pc2"] = None
        print("Состояние ПК сброшено")

# Маршрут для главной страницы
@app.route("/", methods=["GET"])
def index():
    with global_lock:
        pc1_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pc_timestamps["pc1"])) if pc_timestamps["pc1"] else "N/A"
        pc2_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pc_timestamps["pc2"])) if pc_timestamps["pc2"] else "N/A"
        return render_template("index.html", pc1_time=pc1_time, pc2_time=pc2_time, pc_states=pc_states)

# Маршрут для получения состояния готовности от ПК
@app.route("/ready", methods=["POST"])
def ready():
    global pc_states, pc_timestamps
    data = request.json

    with global_lock:
        # Обновляем состояние и время получения сигнала от ПК
        if data["pc"] == "pc1":
            pc_states["pc1"] = True
            pc_timestamps["pc1"] = time.time()
        elif data["pc"] == "pc2":
            pc_states["pc2"] = True
            pc_timestamps["pc2"] = time.time()

        return jsonify({"status": "updated"})
    
@app.route("/status")
def status():
    return jsonify({
        "pc1": {
            "status": "Ready" if pc_states["pc1"] else "Waiting",
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pc_timestamps["pc1"])) if pc_timestamps["pc1"] else None
        },
        "pc2": {
            "status": "Ready" if pc_states["pc2"] else "Waiting",
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pc_timestamps["pc2"])) if pc_timestamps["pc2"] else None
        }
    })

# Маршрут для сброса состояния
@app.route("/reset", methods=["POST"])
def reset():
    reset_pc_states()
    return jsonify({"status": "reset"})

# Основной запуск сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
