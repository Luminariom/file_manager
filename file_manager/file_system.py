import os
import sys
import socket
from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QDialog, QMainWindow, QTreeView, QPushButton, QFileSystemModel, QWidget, QInputDialog, QMessageBox, QHBoxLayout, QLineEdit, QFileDialog, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtCore


class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Explorer for Elbek")
        self.setGeometry(100, 100, 800, 600)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(('localhost', 65432))
        except socket.error as e:
            print(f"Failed to connect to server: {e}")
            sys.exit(1)  # Exits if connection to server fails

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.model = QFileSystemModel()
        root_path = "/Users/"
        self.model.setRootPath(root_path)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(root_path))
        layout.addWidget(self.tree)

        # Find File button
        find_btn_layout = QHBoxLayout()
        find_btn = QPushButton(QIcon("icons/find.png"), "Find File")
        find_btn.clicked.connect(self.open_search_window)  # Connect to a method in FileExplorer to open the search window
        find_btn_layout.addWidget(find_btn)
        layout.addLayout(find_btn_layout)

        # Buttons (Divided into two rows)
        btn_layout_1 = QHBoxLayout()
        btn_layout_2 = QHBoxLayout()

        
        copy_btn = QPushButton(QIcon("icons/copy.png"), "Copy")
        copy_btn.clicked.connect(self.copy_file)
        delete_btn = QPushButton(QIcon("icons/delete.png"), "Delete")
        delete_btn.clicked.connect(self.delete)
        rename_btn = QPushButton(QIcon("icons/rename.png"), "Rename")
        rename_btn.clicked.connect(self.rename_file)
        create_btn = QPushButton(QIcon("icons/create.png"), "Create")
        create_btn.clicked.connect(self.create_file)
        view_btn = QPushButton(QIcon("icons/view.png"), "View Content")
        view_btn.clicked.connect(self.view_content)


        btn_layout_1.addWidget(copy_btn)
        btn_layout_1.addWidget(delete_btn)
        btn_layout_1.addWidget(rename_btn)
        btn_layout_1.addWidget(create_btn)
        btn_layout_1.addWidget(view_btn)

        move_btn = QPushButton(QIcon("icons/move.png"), "Move")
        move_btn.clicked.connect(self.move_file)
        zip_btn = QPushButton(QIcon("icons/zip.png"), "Zip")
        zip_btn.clicked.connect(self.zip_file)
        unzip_btn = QPushButton(QIcon("icons/unzip.png"), "Unzip")
        unzip_btn.clicked.connect(self.unzip_file)
        chmod_btn = QPushButton(QIcon("icons/permissions.png"), "Change Permissions")
        chmod_btn.clicked.connect(self.change_permissions)

        btn_layout_2.addWidget(move_btn)
        btn_layout_2.addWidget(zip_btn)
        btn_layout_2.addWidget(unzip_btn)
        btn_layout_2.addWidget(chmod_btn)

        layout.addLayout(btn_layout_1)
        layout.addLayout(btn_layout_2)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_search_window(self):
        self.search_window = FileSearchWindow()
        self.search_window.show()

    # def view_content(self):
    #     self.view_content = FileContentViewer()
    #     self.view_content.show()        

    # Method to display message boxes with specified title and message

    def send_command(self, command):
        self.client_socket.sendall(command.encode('utf-8'))
        response = self.client_socket.recv(1024)
        QMessageBox.information(self, "Server Response", response.decode('utf-8'))

    def show_message_box(self, title, message, icon=QMessageBox.Information):
        msg_box = QMessageBox(icon, title, message, QMessageBox.Ok)
        msg_box.exec_()

    def copy_file(self):
        current_index = self.tree.currentIndex()
        file_path = self.model.filePath(current_index)
        destination_path, _ = QInputDialog.getText(self, "Copy File", "Enter destination path:")
        
        if destination_path:
            if os.path.exists(destination_path):
                confirm = QMessageBox.question(self, "Confirm Overwrite", "The destination file already exists. Do you want to overwrite it?", QMessageBox.Yes | QMessageBox.No)
                if confirm == QMessageBox.No:
                    return
            try:
                os.system(f"cp -r {file_path} {destination_path}")
                self.show_message_box("Success", "File copied successfully.")
                self.send_command(f"cp -r {file_path} {destination_path}")
            except OSError as e:
                self.show_message_box("Error", f"Failed to copy file: {str(e)}", QMessageBox.Critical)

    def delete(self):
        current_index = self.tree.currentIndex()
        file_path = self.model.filePath(current_index)
        
        if os.path.isdir(file_path):
            confirm_msg = f"Are you sure you want to delete the folder {file_path} and its contents?"
        else:
            confirm_msg = f"Are you sure you want to delete the file {file_path}?"

        confirm = QMessageBox.question(self, "Delete", confirm_msg, QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                if os.path.isdir(file_path):
                    os.system(f"rm -r {file_path}")
                    self.send_command(f"rm -r {file_path}")
                else:
                    os.remove(file_path)
                    self.send_command(f"rm {file_path}")
            except OSError as e:
                self.show_message_box("Error", f"Failed to delete: {str(e)}", QMessageBox.Critical)

    def rename_file(self):
        current_index = self.tree.currentIndex()
        file_path = self.model.filePath(current_index)
        new_name, ok = QInputDialog.getText(self, "Rename File", "Enter new name:")
        
        if ok:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            if os.path.exists(new_path):
                self.show_message_box("Error", "A file with the new name already exists in the directory. Please enter a different name.")
                #
                return
            try:
                os.rename(file_path, new_path)
                self.send_command(f"mv {file_path} {new_path}")
            except OSError as e:
                self.show_message_box("Error", f"Failed to rename: {str(e)}")

    def create_file(self):
        current_index = self.tree.currentIndex()
        folder_path = self.model.filePath(current_index)
        file_name, ok = QInputDialog.getText(self, "Create File", "Enter file name:")

        if ok:
            if '.' in file_name:
                file_path = os.path.join(folder_path, file_name)
                try:
                    with open(file_path, "w"):
                        pass
                    self.show_message_box("Success", f"File '{file_name}' created successfully.")
                    self.send_command(f"touch {file_path}")
                except OSError as e:
                    self.show_message_box("Error", f"Failed to create file: {str(e)}", QMessageBox.Critical)
            else:
                folder_path = os.path.join(folder_path, file_name)
                try:
                    os.makedirs(folder_path)
                    self.show_message_box("Success", f"Folder '{file_name}' created successfully.")
                    self.send_command(f"mkdir {file_path}")
                except OSError as e:
                    self.show_message_box("Error", f"Failed to create folder: {str(e)}", QMessageBox.Critical)

    def move_file(self):
        current_index = self.tree.currentIndex()
        file_path = self.model.filePath(current_index)
        destination_path, _ = QInputDialog.getText(self, "Move File", "Enter destination path:")
        
        if destination_path:
            try:
                os.system(f"mv {file_path} {destination_path}")
                final_destination_folder = os.path.basename(destination_path)
                self.show_message_box("Success", f"File moved successfully to '{final_destination_folder}'.")
                self.send_command(f"mv {file_path} {destination_path}")
            except OSError as e:
                self.show_message_box("Error", f"Failed to move file: {str(e)}", QMessageBox.Critical)

    def zip_file(self):
        current_index = self.tree.currentIndex()
        file_path = self.model.filePath(current_index)
        zip_name, ok = QInputDialog.getText(self, "Zip File", "Enter zip file name:")

        if ok and zip_name:
            zip_path = os.path.join(os.path.dirname(file_path), zip_name)
            if os.path.exists(zip_path):
                self.show_message_box("Error", "A file with the zip file name already exists in the directory. Please enter a different name.")
                return
            try:
                os.system(f"zip -r {zip_path} {file_path}")
                self.send_command(f"zip -r {zip_path} {file_path}")
                self.show_message_box("Success", f"File '{os.path.basename(zip_path)}' zipped successfully.")
            except OSError as e:
                self.show_message_box("Error", f"Failed to zip file: {str(e)}", QMessageBox.Critical)

    def unzip_file(self):
        zip_file, ok = QInputDialog.getText(self, "Unzip File", "Enter zip file name:")

        if ok and zip_file:
            if not os.path.exists(zip_file):
                self.show_message_box("Error", "The specified zip file does not exist.")
                return
            try:
                os.system(f"unzip {zip_file}")
                self.send_command(f"unzip {zip_file}")
                self.show_message_box("Success", "File unzipped successfully.")
            except OSError as e:
                self.show_message_box("Error", f"Failed to unzip file: {str(e)}", QMessageBox.Critical)


    def change_permissions(self):
        current_index = self.tree.currentIndex()
        file_path = self.model.filePath(current_index)
        permissions, ok = QInputDialog.getText(self, "Change Permissions", "Enter new permissions (e.g., 755):")

        if not ok:
            return
        try:
            int(permissions, 8)  # Attempt to convert permissions to an integer in octal format
        except ValueError:
            self.show_message_box("Error", "Invalid permissions format. Please enter permissions in octal format (e.g., 755).")
            return
        try:
            os.system(f"chmod {permissions} {file_path}")
            self.send_command(f"chmod {permissions} {file_path}")
            self.show_message_box("Success", "Permissions changed successfully.")
        except OSError as e:
            self.show_message_box("Error", f"Failed to change permissions: {str(e)}", QMessageBox.Critical)

    def view_content(self):
        current_index = self.tree.currentIndex()
        file_path = self.model.filePath(current_index)
        try:
            viewer = FileContentViewer(file_path)
            viewer.exec_()
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Failed to view file content: {str(e)}")



class FileContentViewer(QDialog):
    def __init__(self, file_path):
        super().__init__()
        layout = QVBoxLayout()
        self.image_label = QLabel()
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        self.setWindowTitle("File Content Viewer")
        self.setGeometry(100, 100, 600, 400)
        self.set_content(file_path)

    def set_content(self, file_path):
        pixmap = QPixmap(file_path)
        pixmap = pixmap.scaled(600, 400, aspectRatioMode=QtCore.Qt.KeepAspectRatio)
        if pixmap.isNull():
            self.image_label.setText("Failed to load image.")
        else:
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(False)

    # def view_content(self):
    #     current_index = self.tree.currentIndex()
    #     file_path = self.model.filePath(current_index)
    #     try:
    #         with open(file_path, "r") as file:
    #             content = file.read()
    #             viewer = FileContentViewer(content,file_path)
    #             viewer.show_content()
    #     except OSError as e:
    #         self.show_message_box("Error", f"Failed to view file content: {str(e)}", QMessageBox.Critical)

class FileSearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Search")
        self.setGeometry(100, 100, 400, 200)

        self.file_name_input = QLineEdit(self)
        self.file_name_input.setGeometry(20, 20, 200, 30)

        self.select_dir_button = QPushButton("Select Directory", self)
        self.select_dir_button.setGeometry(230, 20, 150, 30)
        self.select_dir_button.clicked.connect(self.select_directory)

        self.search_button = QPushButton("Search", self)
        self.search_button.setGeometry(20, 70, 100, 30)
        self.search_button.clicked.connect(self.search_file)

    def select_directory(self):
        starting_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if starting_dir:
            self.starting_dir = starting_dir
    
    def search_file(self):
        file_name = self.file_name_input.text()
        if not file_name:
            QMessageBox.warning(self, "Warning", "Please enter a file name.")
            return
        if not hasattr(self, 'starting_dir'):
            QMessageBox.warning(self, "Warning", "Please select a starting directory.")
            return

        search_command = f"find '{self.starting_dir}' -name '{file_name}'"
        result = os.popen(search_command).read()
        if result:
            QMessageBox.information(self, "Search Result", f"Found:\n{result}")
            self.send_command(f"find {self.starting_dir} -name {file_name}")
        else:
            QMessageBox.information(self, "Search Result", "File not found.")

       

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileExplorer()
    window.show()
    sys.exit(app.exec_())
