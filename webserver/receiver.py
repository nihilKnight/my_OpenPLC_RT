import socket
import os
import random
import struct
import time

from db_manager import insert_st_file


DESTINATION_DIR = '/home/went/ZGCLab/plc/OpenPLC_v3/webserver/st_files'

def generate_random_string(length=8, chars='0123456789abcdef'):
    return ''.join(random.choice(chars) for _ in range(length))


def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server started，listen on {host}:{port} ...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        command_len = struct.unpack('I', client_socket.recv(4))[0]
        command = client_socket.recv(command_len).decode()

        if command == '__U__':
            receive_file(client_socket, client_address)
        elif command == '__D__':
            send_file(client_socket)

        client_socket.close()


def receive_file(client_socket, client_address):

    file_name_len = struct.unpack('I', client_socket.recv(4))[0]
    file_name = client_socket.recv(file_name_len).decode()

    file_size = struct.unpack('Q', client_socket.recv(8))[0]

    # file_name = generate_random_string(16) + '.st'
    print(f"Prepare to receive: {file_name}, size: {file_size} bytes")

    with open(os.path.join(DESTINATION_DIR, file_name), 'wb') as f:
        remaining = file_size
        while remaining:
            data = client_socket.recv(min(1024, remaining))
            f.write(data)
            remaining -= len(data)

    print(f"File {file_name} received.")

    prog_name = generate_random_string(16) + '_downloaded.st'
    prog_descr = f'Downloaded file {file_name} from [{client_address}]'
    prog_file = file_name
    epoch_time = str(int(time.time()))

    insert_st_file(prog_name, prog_descr, prog_file, epoch_time)

    print(f"File {file_name} inserted into database.")

def send_file(client_socket):
    file_name = client_socket.recv(1024).decode()
    if os.path.exists(file_name):
        client_socket.send(file_name.encode())
        file_size = os.path.getsize(file_name)
        client_socket.send(str(file_size).encode())
        with open(file_name, 'rb') as f:
            while (data := f.read(1024)):
                client_socket.send(data)
        print(f"File {file_name} sent successfully.")
    else:
        print(f"File {file_name} not exists，failed to send.")
        client_socket.send(b'File not found')


if __name__ == "__main__":
    start_server('0.0.0.0', 5000)
