import os
import socket
import threading
import time
import tqdm

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 9000))
server.listen(5)


def receive_file(client):
    try:
        received = client.recv(1024).decode()
        file_name, file_size = received.split('::')
        file_size = int(file_size)
        print(f'File size in Bytes: {file_size}')

        progress = tqdm.tqdm(range(file_size), f'Receiving {file_name}', unit='B', unit_scale=True, unit_divisor=1024)
        
        with open(f'Server Data/{file_name}', 'wb') as file:
            while True:
                data = client.recv(1024)
                if data.endswith(b'EOF'):  # Check for end-of-file marker
                    data = data[:-3]  # Remove the end-of-file marker
                    file.write(data)
                    progress.update(len(data))
                    break
                file.write(data)
                progress.update(len(data))
    except Exception as e:
        print("Server Error: ", e)
        client.close()

def send_file(client):
    try:
        file_name = client.recv(1024).decode()
        file_size = os.path.getsize(f'Server Data/{file_name}')
        print('File size in Bytes: ', file_size)
        print(f'{file_name}::{file_size}')
        client.send(f'{file_name}::{file_size}'.encode())

        with open(f'Server Data/{file_name}', 'rb') as file:
            data = file.read(1024)
            while data:
                time.sleep(0.0001) # To simulate a slow connection
                client.send(data)
                data = file.read(1024)
            client.send(b'EOF')
    except Exception as e:
        print("Server Error: ", e)
        client.close()

def list_files(client):
    try:
        files = '\n'.join(os.listdir('Server Data'))
        client.send(files.encode())
    except Exception as e:
        print("Server Error: ", e)
        client.close()

def delete_file(client):
    try:   
        file_name = client.recv(1024).decode()
        try:
            os.remove(f'Server Data/{file_name}')
            client.send(f'{file_name} deleted successfully'.encode())
        except Exception as e:
            client.send(f'Server Error: {e}'.encode())
    except Exception as e:
        print("Server Error: ", e)
        client.close()

actions = '''
    1) upload_file
    2) download_file
    3) list_files
    4) delete_file
'''

def handle_client(client):
    while True:
        try:
            client.send(actions.encode())
            action = client.recv(1024).decode()
            if action == '1':
                receive_file(client)
            elif action == '2':
                send_file(client)
            elif action == '3':
                list_files(client)
            elif action == '4':
                delete_file(client)
            elif action == 'exit':
                print('Client disconnected')
                client.close()
                break
            else:
                client.close()
                break

        except Exception as e:
            print("Server Error: ", e)
            client.close()
            break

while True:
    try:
        client, addr = server.accept()
        print('new client connected')
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

    except Exception as e:
        print("Server Error: ", e)
        server.close()
        break
