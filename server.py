import signal
import socket
import sys
import json
from datetime import datetime


def log_event(log_message):
    with open("torch_events.log", "a") as log_file:
        log_file.write(log_message + "\n")


def load_or_initialize_state():
    try:
        with open("torch_state.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Starting with default torch state.")
        return {"state": False, "timestamp": None, "user": None}


def update_and_save_state(user, state):
    state["state"] = not state["state"]
    state["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["user"] = user
    with open("torch_state.json", "w") as f:
        json.dump(state, f)


def handle_client_connection(client_socket, state):
    try:
        message = client_socket.recv(1024).decode()
        user, _ = message.split(",")

        previous_state = state["state"]
        update_and_save_state(user, state)

        log_message = f"{state['timestamp']}: {state['user']} toggled torch from {previous_state} to {state['state']}"
        log_event(log_message)

        client_socket.send(json.dumps(state).encode())
    except ValueError:
        print("Received invalid data from client.")
    finally:
        client_socket.close()


def main():
    signal.signal(
        signal.SIGINT,
        lambda sig, frame: (print("Shutting down server..."), sys.exit(0)),
    )

    state = load_or_initialize_state()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", 12345))
    server_socket.listen()

    print("Server started, waiting for clients...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} has been established.")
        handle_client_connection(client_socket, state)


if __name__ == "__main__":
    main()
