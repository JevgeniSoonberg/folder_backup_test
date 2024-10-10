import os
import shutil
import time
import logging
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys

def sync_folders(source, replica):
    source_items = set(os.listdir(source))
    replica_items = set(os.listdir(replica))

    # Copy new and updated files from source to replica
    for item in source_items:
        source_path = os.path.join(source, item)
        replica_path = os.path.join(replica, item)

        if os.path.isdir(source_path):
            if not os.path.exists(replica_path):
                shutil.copytree(source_path, replica_path)
                logging.info(f'Copied folder: {replica_path}')
            else:
                sync_folders(source_path, replica_path)
        else:
            if not os.path.exists(replica_path) or not files_are_equal(source_path, replica_path):
                shutil.copy2(source_path, replica_path)
                logging.info(f'Copied file: {replica_path}')

    # Delete files and folders that are not in source
    for item in replica_items - source_items:
        replica_path = os.path.join(replica, item)
        if os.path.isdir(replica_path):
            shutil.rmtree(replica_path)
            logging.info(f'Deleted folder: {replica_path}')
        else:
            os.remove(replica_path)
            logging.info(f'Deleted file: {replica_path}')

def files_are_equal(file1, file2):
    return os.path.getsize(file1) == os.path.getsize(file2) and \
           get_file_checksum(file1) == get_file_checksum(file2)

def get_file_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

class FolderSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Synchronization")

        self.source_folder = tk.StringVar()
        self.replica_folder = tk.StringVar()
        self.sync_interval = tk.IntVar(value=60)
        self.log_filename = tk.StringVar(value="sync.log")
        self.is_running = False
        self.sync_process = None  # Sync Process

        self.check_existing_log_file()
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def check_existing_log_file(self):
        # Check if there any .log files in source app directory
        script_directory = os.path.dirname(os.path.abspath(__file__))
        log_files = [f for f in os.listdir(script_directory) if f.endswith('.log')]
        if log_files:
            # If at least one .log file found use his name
            self.log_filename.set(log_files[0])

    def create_widgets(self):
        padding = {'padx': 10, 'pady': 5}

        # Source folder
        tk.Label(self.root, text="Source folder:").grid(row=0, column=0, sticky='e', **padding)
        tk.Entry(self.root, textvariable=self.source_folder, width=50).grid(row=0, column=1, **padding)
        tk.Button(self.root, text="Browse...", command=self.browse_source_folder).grid(row=0, column=2, **padding)

        # Replica folder
        tk.Label(self.root, text="Replica folder:").grid(row=1, column=0, sticky='e', **padding)
        tk.Entry(self.root, textvariable=self.replica_folder, width=50).grid(row=1, column=1, **padding)
        tk.Button(self.root, text="Browse...", command=self.browse_replica_folder).grid(row=1, column=2, **padding)

        # Synchronization interval
        tk.Label(self.root, text="Interval (sec):").grid(row=2, column=0, sticky='e', **padding)
        tk.Entry(self.root, textvariable=self.sync_interval, width=10).grid(row=2, column=1, sticky='w', **padding)

        # Log file name
        tk.Label(self.root, text="Log file name:").grid(row=3, column=0, sticky='e', **padding)
        tk.Entry(self.root, textvariable=self.log_filename, width=50).grid(row=3, column=1, **padding)

        # Control buttons
        self.start_button = tk.Button(self.root, text="Start Synchronization", command=self.start_sync)
        self.start_button.grid(row=4, column=0, columnspan=3, pady=10)

        self.status_label = tk.Label(self.root, text="Status: Stopped")
        self.status_label.grid(row=5, column=0, columnspan=3, **padding)

    def browse_source_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.source_folder.set(path)

    def browse_replica_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.replica_folder.set(path)

    def start_sync(self):
        if self.is_running:
            self.stop_sync()
        else:
            if not self.validate_inputs():
                return
            self.is_running = True
            self.start_button.config(text="Stop Synchronization")
            self.status_label.config(text="Status: Synchronization Running")
            self.run_sync_process()

    def stop_sync(self):
        if self.sync_process:
            self.sync_process.terminate()
            self.sync_process = None
        self.is_running = False
        self.start_button.config(text="Start Synchronization")
        self.status_label.config(text="Status: Stopped")

    def validate_inputs(self):
        if not os.path.exists(self.source_folder.get()):
            messagebox.showerror("Error", "Source folder does not exist.")
            return False
        if not os.path.exists(self.replica_folder.get()):
            try:
                os.makedirs(self.replica_folder.get())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create replica folder: {e}")
                return False
        if self.sync_interval.get() <= 0:
            messagebox.showerror("Error", "Synchronization interval must be greater than zero.")
            return False
        if not self.log_filename.get():
            messagebox.showerror("Error", "Please enter a log file name.")
            return False
        return True

    def run_sync_process(self):
        source = os.path.abspath(self.source_folder.get())
        replica = os.path.abspath(self.replica_folder.get())
        interval = str(self.sync_interval.get())
        log_file = self.log_filename.get()

        script_path = os.path.abspath(__file__)

        if sys.platform == "win32":
            command = [
                sys.executable,
                script_path,
                "--sync",
                source,
                replica,
                interval,
                log_file
            ]
            # Open new terminal window
            self.sync_process = subprocess.Popen(
                command,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            logging.error("This script currently supports only Windows platform.")
            messagebox.showerror("Error", "This script supports only Windows platform.")
            return

    def on_closing(self):
        if self.is_running:
            self.stop_sync()
        self.root.destroy()

def main():
    # If scrict running with --sync parameter, run syncronization
    if '--sync' in sys.argv:
        idx = sys.argv.index('--sync')
        try:
            source_folder = sys.argv[idx + 1]
            replica_folder = sys.argv[idx + 2]
            sync_interval = int(sys.argv[idx + 3])
            log_filename = sys.argv[idx + 4]
        except (IndexError, ValueError):
            print("Invalid arguments for synchronization.")
            sys.exit(1)

        # Setting upp logging
        script_directory = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(script_directory, log_filename)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path, encoding='utf-8', mode='a'),
                logging.StreamHandler(stream=sys.stdout)
            ]
        )
        logging.info("=== Synchronization started ===")

        try:
            while True:
                sync_folders(source_folder, replica_folder)
                time.sleep(sync_interval)
        except KeyboardInterrupt:
            logging.info("=== Synchronization stopped ===")
            sys.exit(0)
    else:
        root = tk.Tk()
        app = FolderSyncApp(root)
        root.mainloop()

if __name__ == "__main__":
    main()
