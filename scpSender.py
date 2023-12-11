import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import paramiko
from scp import SCPClient
from threading import Thread
import traceback
import json

class ScpUploadApp:
    def __init__(self, master, config):
        self.master = master
        self.config = config
        master.title("SCP Upload")

        # Variables
        self.local_folder = tk.StringVar()
        self.remote_path = tk.StringVar(value="/home/chacaltordu/media/jellyfin/data")
        self.server_address = self.config["server_address"]
        self.username = self.config["username"]
        self.password = self.config["password"]
        self.upload_type = tk.StringVar(value="")  # Valeur par défaut
        self.progress_var = tk.StringVar()

        # Widgets
        tk.Label(master, text="Dossier local à envoyer:").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(master, textvariable=self.local_folder, width=50).grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Button(master, text="Sélectionner un dossier", command=self.select_folder).grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

        tk.Label(master, text="Adresse IP du serveur:").grid(row=3, column=0, sticky=tk.W)
        tk.Entry(master, textvariable=tk.StringVar(value=self.server_address), state='readonly', width=20).grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)

        tk.Label(master, text="Nom d'utilisateur:").grid(row=5, column=0, sticky=tk.W)
        tk.Entry(master, textvariable=tk.StringVar(value=self.username), state='readonly', width=20).grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)

        # tk.Label(master, text="Mot de passe:").grid(row=11, column=0, sticky=tk.W)
        # tk.Entry(master, textvariable=self.password, show='*', state='readonly').grid(row=12, column=0, padx=10, pady=5, sticky=tk.W)

        tk.Label(master, text="Chemin distant sur le serveur:").grid(row=7, column=0, sticky=tk.W)
        tk.Label(master, textvariable=self.remote_path, wraplength=400, justify="left").grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)

        tk.Label(master, text="Type d'envoi:").grid(row=9, column=0, sticky=tk.W)
        upload_type_combobox = ttk.Combobox(master, textvariable=self.upload_type, values=["Série", "Film", "Anime Japonais", "Dessin Animé"])
        upload_type_combobox.grid(row=10, column=0, padx=10, pady=5, sticky=tk.W)
        upload_type_combobox.bind("<<ComboboxSelected>>", lambda event: self.update_remote_path())

        tk.Button(master, text="Envoyer le dossier", command=self.upload_folder).grid(row=13, column=0, pady=10, sticky=tk.W)

        # Barre de progression
        tk.Label(master, text="Progression:").grid(row=14, column=0, sticky=tk.W)
        ttk.Label(master, textvariable=self.progress_var).grid(row=15, column=0, padx=10, pady=5, sticky=tk.W)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.local_folder.set(folder)
            self.update_remote_path()

    def update_remote_path(self):
        local_folder = self.local_folder.get()

        if self.upload_type.get() == "Série":
            self.remote_path.set(f"/home/{self.username}/media/jellyfin/data/series")
        elif self.upload_type.get() == "Film":
            self.remote_path.set(f"/home/{self.username}/media/jellyfin/data/films")
        elif self.upload_type.get() == "Anime Japonais":
            self.remote_path.set(f"/home/{self.username}/media/jellyfin/data/animeJap")
        elif self.upload_type.get() == "Dessin Animé":
            self.remote_path.set(f"/home/{self.username}/media/jellyfin/data/dessinAnimes")

    def update_progress(self, filename, size, sent, peername=None):
        if peername:
            progress_message = f"({peername[0]}:{peername[1]}) {filename}'s progress: {float(sent) / float(size) * 100:.2f}%"
        else:
            progress_message = f"{filename}'s progress: {float(sent) / float(size) * 100:.2f}%"
        self.progress_var.set(progress_message)

    def upload_folder(self):
        local_folder = self.local_folder.get()

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.server_address, username=self.username, password=self.password)

            Thread(target=lambda: self.upload_with_progress(ssh, local_folder)).start()
        except Exception as e:
            print(f"Une erreur s'est produite: {e}")
            traceback.print_exc()

    def upload_with_progress(self, ssh, local_folder):
        try:
            with SCPClient(ssh.get_transport(), progress4=self.update_progress) as scp:
                scp.put(local_folder, recursive=True, remote_path=self.remote_path.get())

            print(f"Transfert du dossier '{local_folder}' vers '{self.remote_path.get()}' réussi.")
        except Exception as e:
            print(f"Une erreur s'est produite: {e}")

if __name__ == "__main__":
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    root = tk.Tk()
    app = ScpUploadApp(root, config)
    root.mainloop()

