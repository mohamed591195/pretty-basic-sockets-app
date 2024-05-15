import os
import socket
import time
import tqdm

server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def list_files(server_conn):
    try:
        files_list = server_conn.recv(1024).decode()
        print(files_list)
    except Exception as e:
        print("Client Error: ", e)
        server_conn.close()

def upload_file(server_conn):
    try:
        file_name = input('Enter the file name to upload: ')
        file_size = os.path.getsize(f'Client Data/{file_name}')
        print('File size in Bytes: ', file_size)
        print(f'{file_name}::{file_size}'.encode())

        server_conn.send(f'{file_name}::{file_size}'.encode())

        with open(f'Client Data/{file_name}', 'rb') as file:
            data = file.read(1024)
            while data:
                time.sleep(0.0001) # To simulate a slow connection
                server_conn.send(data)
                data = file.read(1024)
            server_conn.send(b'EOF')
    except Exception as e:
        print("Client Error: ", e)
        server_conn.close()

def download_file(server_conn):
    try:
        file_name = input('Enter the file name to download: ')
        print(file_name)

        server_conn.send(file_name.encode())
        print('File name sent')
        received = server_conn.recv(1024).decode()
        file_name, file_size = received.split('::')
        file_size = int(file_size)
        print(f'File size in Bytes: {file_size}')

        progress = tqdm.tqdm(range(file_size), f'Receiving {file_name}', unit='B', unit_scale=True, unit_divisor=1024)
        
        with open(f'Client Data/{file_name}', 'wb') as file:
            while True:
                data = server_conn.recv(1024)
                if data.endswith(b'EOF'):  # Check for end-of-file marker
                    data = data[:-3]  # Remove the end-of-file marker
                    file.write(data)
                    progress.update(len(data))
                    break
                file.write(data)
                progress.update(len(data))
    except Exception as e:
        print("Client Error: ", e)
        server_conn.close()

def delete_file(server_conn):
    try:
        file_name = input('Enter the file name to delete: ')
        server_conn.send(file_name.encode())
        response = server_conn.recv(1024).decode()
        print(response)

    except Exception as e:
        print("Client Error: ", e)
        server_conn.close()

try:
    server_conn.connect(('localhost', 9000))

    while True:
        actions = server_conn.recv(1024).decode()
        print(actions)
        print('To exit, enter "exit"')

        action = input('Enter the action number: ')
        server_conn.send(action.encode())

        if action == '1':
            upload_file(server_conn)
        elif action == '2':
            download_file(server_conn)
        elif action == '3':
            list_files(server_conn)
        elif action == '4':
            delete_file(server_conn)
        
        if action == 'exit':
            server_conn.send(action.encode())
            server_conn.close()
            break

except Exception as e:
    print("Client Error: ", e)
    server_conn.close()   




