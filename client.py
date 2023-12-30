import socket
import json
import sys


def connect_to_server(host, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        return client_socket
    except ConnectionRefusedError:
        print("Failed to connect to the server.")
        sys.exit(1)


def send_toggle_request(client_socket, username):
    client_socket.send(f"{username},toggle".encode())
    response = client_socket.recv(1024).decode()
    return json.loads(response)


def main(host, port, username):
    client_socket = connect_to_server(host, port)
    torch_state = send_toggle_request(client_socket, username)
    print(
        f"{torch_state['timestamp']}: {torch_state['user']} set torch to: {torch_state['state']}"
    )
    client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 client.py [username]")
        sys.exit(1)

    main(host="localhost", port=12345, username=sys.argv[1])
