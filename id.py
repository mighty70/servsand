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

        # Проверяем состояние обоих ПК
        if pc_states["pc1"] and pc_states["pc2"]:
            if abs(pc_timestamps["pc1"] - pc_timestamps["pc2"]) <= 6:
                # Сначала выполняем действие, затем сбрасываем состояние
                response = {"status": "game_accepted"}
                print("Оба ПК готовы. Выполняем действие game_accepted.")
                reset_pc_states()  # Выполняем сброс состояния после отправки ответа
                return jsonify(response)

        # Если один из ПК готов, но второй еще нет
        if pc_states["pc1"] or pc_states["pc2"]:
            return jsonify({"status": "game_found"})

        return jsonify({"status": "no PC ready"})

# Маршрут для принятия игры от ПК
@app.route("/accept_game", methods=["POST"])
def accept_game():
    global pc_states, pc_timestamps
    data = request.json

    with global_lock:
        # Обновляем состояние ПК, который отправил запрос
        if data["pc"] in pc_states:
            pc_states[data["pc"]] = True
            pc_timestamps[data["pc"]] = time.time()
            start_reset_timer(data["pc"])

            # Проверяем, готовы ли оба ПК
            if pc_states["pc1"] and pc_states["pc2"]:
                if abs(pc_timestamps["pc1"] - pc_timestamps["pc2"]) <= 6:
                    # Сначала выполняем действие, затем сбрасываем состояние
                    response = {"status": "game_accepted"}
                    print("Оба ПК готовы. Выполняем действие game_accepted.")
                    reset_pc_states()  # Выполняем сброс состояния после отправки ответа
                    return jsonify(response)

            # Если второй ПК еще не готов
            return jsonify({"status": "game_found"})
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
