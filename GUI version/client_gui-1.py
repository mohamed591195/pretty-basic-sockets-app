import socket
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import tqdm
# import time


class GUI(object):
    def __init__(self, root):
        self.root = root
        self.root.title('File Transfer')
        self.root.geometry('400x400')
        self.root.resizable(False, False)
        self.root.configure(background="#C4E4F2")

        self.empty_label = tk.Label(self.root, width=5, text='', bg='#C4E4F2')
        self.empty_label.grid(row=0, column=0)

        self.list_files_button = tk.Button(self.root, text='List Files', command=self.list_files)
        self.list_files_button.grid(row=0, column=1, padx=10, pady=10)

        self.upload_file_button = tk.Button(self.root, text='Upload File', command=self.upload_file)
        self.upload_file_button.grid(row=0, column=2, pady=10)

        self.download_file_button = tk.Button(self.root, text='Download File', command=self.download_file)
        self.download_file_button.grid(row=0, column=3, padx=10, pady=10)

        self.delete_file_button = tk.Button(self.root, text='Delete File', command=self.delete_file)    
        self.delete_file_button.grid(row=0, column=4, pady=10)

        #show list of the files
        self.files_list = tk.Listbox(self.root, height=10, width=40)
        self.files_list.grid(row=1, column=1, columnspan=3, padx=10, pady=10)

        try:
            self.server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_conn.connect(('localhost', 9000))
            tk.messagebox.showinfo('Connection', 'Connected to the server')

        except Exception as e:
            print('Socket creation error: ', e)
            
            messagebox.showerror('Error', f'Error: {e}')
            self.server_conn.close()
            self.root.destroy()

    def list_files(self):
        try:
            self.server_conn.send('list_files'.encode())
            files_list = eval(self.server_conn.recv(1024).decode())
            self.files_list.delete(0, tk.END)
            for f in files_list:
                self.files_list.insert(tk.END, f)
        except Exception as e:
            print("Client Error: ", e)
            self.server_conn.close()

    def upload_file(self):
        try:
            self.server_conn.send('upload_file'.encode())
            #selecting file to upload using file dialog
            file_path = filedialog.askopenfilename(title="Select File to Upload")
            if file_path:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                print('File size in Bytes: ', file_size)
                print(f'{file_name}::{file_size}'.encode())

                self.server_conn.send(f'{file_name}::{file_size}'.encode())

                # Create a progress bar
                progress = ttk.Progressbar(self.root, length=100, mode='determinate')
                progress.grid(row=2, column=0, padx=10, pady=10)
                
                with open(file_path, 'rb') as file:
                    data = file.read(1024)
                    while data:
                        # time.sleep(0.0001) # To simulate a slow connection
                        self.server_conn.send(data)
                        data = file.read(1024)
                        # Update the progress bar
                        progress['value'] += (1024 / file_size) * 100
                        self.root.update_idletasks()
                    self.server_conn.send(b'EOF')

                messagebox.showinfo("Upload Success", f"File '{file_name}' uploaded successfully.")
                progress.destroy() # Destroy the progress bar
                self.list_files()
        except Exception as e:
            messagebox.showerror('Error', f'Error: {e}')
            self.server_conn.close()

    def download_file(self):
        try:
            self.server_conn.send('download_file'.encode())
            file_name = self.files_list.get(self.files_list.curselection())
            print(file_name)

            self.server_conn.send(file_name.encode())
            print('File name sent')
            received = self.server_conn.recv(1024).decode()
            file_name, file_size = received.split('::')
            file_size = int(file_size)
            print(f'File size in Bytes: {file_size}')

            # Create a progress bar
            progress = ttk.Progressbar(self.root, length=100, mode='determinate')
            progress.grid(row=2, column=0, padx=10, pady=10)
            
            # select path to save the file
            file_path = filedialog.asksaveasfilename(title="Save File As", initialfile=file_name)
            with open(file_path, 'wb') as file:
                while True:
                    data = self.server_conn.recv(1024)
                    if data.endswith(b'EOF'):  # Check for end-of-file marker
                        data = data[:-3]  # Remove the end-of-file marker
                        file.write(data)
                        progress['value'] = 100
                        break
                    file.write(data)
                    # Update the progress bar
                    progress['value'] += (1024 / file_size) * 100
                    self.root.update_idletasks()
            messagebox.showinfo("Download Success", f"File '{file_name}' downloaded successfully.")
            progress.destroy() # Destroy the progress bar

        except Exception as e:
            messagebox.showerror('Error', f'Error: {e}')
            self.server_conn.close()

    def delete_file(self):
        try:
            self.server_conn.send('delete_file'.encode())
            file_name = self.files_list.get(self.files_list.curselection())
            self.server_conn.send(file_name.encode())
            response = self.server_conn.recv(1024).decode()

            # Refresh the list of files
            self.list_files()
            messagebox.showinfo('Delete File', response)
        except Exception as e:
            messagebox.showerror('Error', f'Error: {e}')
            self.server_conn.close()

root = tk.Tk()
gui = GUI(root)
root.mainloop()