import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QDialog, QLineEdit, QFormLayout, QDialogButtonBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QFileDialog  # Import QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QIcon
from Sakinah import PhotoEditor

class CanvasDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Canvas")
        layout = QFormLayout()
        self.width_input = QLineEdit()
        self.height_input = QLineEdit()
        self.width_input.setPlaceholderText("Enter width in pixels")
        self.height_input.setPlaceholderText("Enter height in pixels")
        layout.addRow("Width:", self.width_input)
        layout.addRow("Height:", self.height_input)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.setLayout(layout)
        
    def get_dimensions(self):
        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
            return width, height
        except ValueError:
            return None, None

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhotoLab - Main Screen")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\icon_resize.png"))
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_widget.setStyleSheet("background-color: #FFFFCC;")
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.video_label)
        new_canvas_button = QPushButton("NEW CANVAS")
        load_image_button = QPushButton("LOAD IMAGE")
        button_style = "background-color: #FF4500; color: white; font-weight: bold; padding: 10px; font-size: 18px;"
        new_canvas_button.setStyleSheet(button_style)
        load_image_button.setStyleSheet(button_style)
        new_canvas_button.clicked.connect(self.open_canvas_dialog)
        button_layout = QHBoxLayout()
        button_layout.addWidget(new_canvas_button)
        button_layout.addWidget(load_image_button)
        main_layout.addSpacing(40)
        main_layout.addLayout(button_layout)
        self.setCentralWidget(main_widget)
        self.capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.start_video()
        load_image_button.clicked.connect(self.load_image)  # Connect load image button to method
        self.open_editors = []

    def start_video(self):
        video_path = r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\Ph.mp4"
        self.capture = cv2.VideoCapture(video_path)
        if not self.capture.isOpened():
            print("Error: Could not open video.")
            return
        self.timer.start(30)
    
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            print("Image path:", file_path)  # Debug print
            self.open_editor_with_image(file_path)

    def open_editor_with_image(self, image_path):
        # Open PhotoEditor and load the selected image
        print(f"Opening editor with image: {image_path}")  # Debug print
        self.editor_window = PhotoEditor(image_path=image_path, create_tabs=True)  # Pass image path to PhotoEditor
        self.editor_window.show()
        self.open_editors.append(self.editor_window)  # Keep track of the editor
        print("Editor window opened")  # Debug print
        self.editor_window.update_status_bar(image_path)  # Ensure status bar is updated after window is shown
    
    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_image))
        else:
            self.timer.stop()
            self.capture.release()

    def open_canvas_dialog(self):
        dialog = CanvasDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            width, height = dialog.get_dimensions()
            if width and height:
                self.open_editor_with_canvas(width, height)
            else:
                print("Invalid input for width or height.")
    
    def open_editor_with_canvas(self, width, height):
        # Open PhotoEditor with width and height for a new blank canvas
        self.editor_window = PhotoEditor(width=width, height=height, image_path=None)  # Ensure image_path is None
        self.editor_window.show()
        self.open_editors.append(self.editor_window)  # Keep track of the editor

    def closeEvent(self, event):
            # Close all open PhotoEditor windows when the main window is closed
            for editor in self.open_editors:
                editor.close()
            event.accept()  # Accept the event to close the main window

app = QApplication(sys.argv)
window = VideoPlayer()
window.show()
sys.exit(app.exec_())
