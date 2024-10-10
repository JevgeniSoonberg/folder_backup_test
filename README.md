#Description
This program provides a graphical interface for synchronizing the contents of two folders (source and replica). It copies new or modified files from the source folder to the replica folder and deletes files that are no longer present in the source folder. The program also supports periodic synchronization with a specified interval. The code is designed to work on the Windows platform and supports logging of all operations to a file.

#Imports
`
import os
import shutil
import time
import logging
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
`
#Modules:

-os — provides functions for working with the file system, such as creating directories, handling paths, and checking if they exist.
-shutil — used for copying files and directories.
-time — for delaying the execution of the synchronization cycle.
-logging — for logging actions such as copying, deleting files, and errors.
-hashlib — for calculating file hashes (used to check if a file has changed).
-tkinter — the library for creating graphical user interfaces (GUI).
-filedialog, messagebox — modules for opening folder selection dialogs and displaying messages.
-subprocess — for launching the synchronization process in a new terminal (Windows).
-sys — for accessing command-line arguments and determining the platform.

#Functions:

##sync_folders(source, replica)
This function synchronizes the contents of two folders — the source (source) and the replica folder (replica). It:

1. Copies new and modified files from the source folder to the replica.
2. Deletes files and folders that are no longer present in the source folder from the replica.

###Arguments:
-source (str): path to the source folder.
-replica (str): path to the replica folder.
###Logic:
-Compares the contents of both folders.
-Copies new and modified files from the source to the replica.
-Deletes any files or folders in the replica that no longer exist in the source folder.

##files_are_equal(file1, file2)
Checks if two files are identical by comparing their sizes and hash values (MD5).

###Arguments:
-file1 (str): path to the first file.
-file2 (str): path to the second file.
###Returns:
-bool: True if the files are identical; False if they differ.
##get_file_checksum(file_path)
Calculates the hash (MD5) of a file to compare it with other files.

###Arguments:
-file_path (str): path to the file.
###Returns:
-str: The file's hash as a string.
###Logic:
-The file is opened in read mode.
-The file is read in 4096-byte chunks to reduce memory load.
-The hash is updated for each chunk, and the result is returned at the end.

#Class FolderSyncApp
This class manages the graphical user interface (GUI) of the application. It implements the main interface for selecting folders, setting the synchronization interval, and starting/stopping the synchronization process.

##Constructor __init__(self, root)
Initializes the graphical window, sets variables for storing the folder paths, the interval, and the log file name. It also creates the interface elements.

###Arguments:
-root (tk.Tk): the main window of the application.
###Methods:
-check_existing_log_file(self)
-Checks for any existing .log files in the script's directory. If such files are found, one of them is set as the log file name.

##create_widgets(self)
Creates interface elements (Label, Entry, Button), such as fields for selecting the source and replica folders, setting the synchronization interval, the log file name, and buttons for starting and stopping the process.

##browse_source_folder(self)
Opens a dialog to select the source folder and saves its path.

##browse_replica_folder(self)
Opens a dialog to select the replica folder and saves its path.

##start_sync(self)
Starts the synchronization process in a separate terminal window if the program is running on Windows. If the synchronization is already running, it stops the process.

##stop_sync(self)
Stops the synchronization process if it was started and updates the interface.

##validate_inputs(self)
Checks if the user inputs are valid: whether the source folder exists, whether the replica folder can be created, if the synchronization interval is positive, and if the log file name is provided.

##run_sync_process(self)
Starts the synchronization process. For Windows, it opens a new terminal window and runs the script with the provided parameters (folders, interval, log file). For other OSes, it displays an error message.

##on_closing(self)
On closing the window, it stops the synchronization process (if running) and closes the window.

##Main Function main()
This function starts the application. If the program is run with the --sync parameter, it performs folder synchronization via the command line. Otherwise, it launches the graphical interface.

###Logic:
-If the script is run with the --sync flag, it reads the command-line arguments (source folder, replica folder, interval, log file) and starts the synchronization cycle with the specified delay.
-Logging is performed both to a file and to the console.
-If the program is launched without the --sync flag, a graphical window is created with the interface to operate the application.

##Usage Example
To launch the program with the GUI:

```bash
  python sync.py
```
This opens the graphical interface where you can select the source and replica folders, set the synchronization interval, and specify the log file.

You can also run the program via the command line with synchronization parameters:

```bash
  python sync.py --sync /path/to/source /path/to/replica 60 sync.log
```
This starts synchronization between the source and replica folders every 60 seconds, and logs the operations to the sync.log file.

##Requirements:
-Python 3.x
-Python's standard library modules:
-os
-shutil
-time
-logging
-hashlib
-tkinter
-subprocess
-sys
