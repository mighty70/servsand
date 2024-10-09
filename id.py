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

# Функция для таймера сброса состояния
def start_reset_timer(pc):
    global timeout_timers
    if timeout_timers[pc] is not None:
        timeout_timers[pc].cancel()
    timeout_timers[pc] = threading.Timer(6.0, reset_pc_states)
    timeout_timers[pc].start()

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
            start_reset_timer("pc1")
        elif data["pc"] == "pc2":
            pc_states["pc2"] = True
            pc_timestamps["pc2"] = time.time()
            start_reset_timer("pc2")

        # Проверяем, пришли ли запросы от обоих ПК в течение 6 секунд
        if pc_states["pc1"] and pc_states["pc2"]:
            if abs(pc_timestamps["pc1"] - pc_timestamps["pc2"]) <= 6:
                reset_pc_states()
                return jsonify({"status": "accepted"})

        return jsonify({"status": "waiting for other PC"})

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

# Маршрут для принятия игры от ПК
@app.route("/accept_game", methods=["POST"])
def accept_game():
    data = request.json

    with global_lock:
        if data["pc"] in pc_states:
            pc_states[data["pc"]] = True
            pc_timestamps[data["pc"]] = time.time()
            start_reset_timer(data["pc"])
            return jsonify({"status": "game_accepted"})
        else:
            return jsonify({"status": "error", "message": "Неверный ПК"}), 400

# Маршрут для сброса состояния
@app.route("/reset", methods=["POST"])
def reset():
    reset_pc_states()
    return jsonify({"status": "reset"})

# Основной запуск сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
