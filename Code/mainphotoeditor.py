#NAME : NUR SAKINAH BINTI MOHAMMAD ALI
#MATRIC : BS22110305
#ASSIGNMENT 1 - DIP2024/25
#OPEN IN FULL SCREEN

import cv2
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QPushButton, QTabWidget, 
    QVBoxLayout, QWidget, QStatusBar, QLabel, QHBoxLayout, QListWidget, 
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGridLayout, QSlider, QSpacerItem, QSizePolicy, QListWidgetItem
)
from PyQt5.QtWidgets import QFileDialog, QMenu, QComboBox, QToolButton, QAction, QInputDialog, QGraphicsItem, QGraphicsTextItem, QDialogButtonBox, QDialog, QFormLayout, QLineEdit, QFrame, QFontComboBox, QSpinBox, QColorDialog
from PyQt5.QtCore import Qt, QPoint, QRect, QRectF, QLineF, QPointF, QSize
from PyQt5.QtGui import QPixmap, QIcon, QImage, QTransform, QColor, QPainter, QPen, QPolygonF, QFont, QCursor, QImageReader
import numpy as np
import os  # Import os to get file details

EYE_ICON_PATH = r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\visibility.png"
CLOSED_EYE_ICON_PATH = r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\visible.png" 

# ======================================== TAB WIDGET CLASS ========================================

class CustomTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def add_tab(self, widget, title):
        self.addTab(widget, title)

    def show_context_menu(self, position):
        index = self.tabBar().tabAt(position)
        if index != -1:
            menu = QMenu()
            
            properties_action = QAction(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\info.png"), "Properties", self)
            close_action = QAction(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\close_icon.png"), "Close", self)
            
            properties_action.triggered.connect(lambda: self.show_properties(index))
            close_action.triggered.connect(lambda: self.close_tab(index))
            
            menu.addAction(properties_action)
            menu.addAction(close_action)
            
            menu.exec_(self.tabBar().mapToGlobal(position))
            
    def close_tab(self, index):
        if index >= 0:
            self.removeTab(index)

    def show_properties(self, index):
        widget = self.widget(index)
        if isinstance(widget, CanvasView):
            pixmap = widget.canvas_pixmap
            if pixmap:
                file_name = self.tabText(index)
                file_size = pixmap.size()
                width_cm = file_size.width() / 37.795275591  
                height_cm = file_size.height() / 37.795275591  
                
                # Determine the file type using QImageReader
                image_reader = QImageReader(file_name)
                file_type = image_reader.format().data().decode().upper() if image_reader.format() else "Unknown"

                properties_dialog = QDialog(self)
                properties_dialog.setWindowTitle("Properties")
                layout = QFormLayout()

                layout.addRow("File name:", QLabel(file_name))
                layout.addRow("File size:", QLabel(f"{width_cm:.2f} x {height_cm:.2f} cm"))
                layout.addRow("Image resolution:", QLabel(f"{file_size.width()} x {file_size.height()} pixels"))
                layout.addRow("File type:", QLabel(file_type))

                properties_dialog.setLayout(layout)
                properties_dialog.exec_()

# ======================================== CREATE NEW CANVAS DIALOG CLASS ========================================

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
        
# ======================================== THUMBNAIL WINDOW CLASS ========================================

class ThumbnailWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thumbnail Preview")
        self.setGeometry(100, 100, 300, 300)  
        self.thumbnail_label = QLabel(self)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.thumbnail_label)
        self.setLayout(layout)

    def update_thumbnail(self, pixmap):
        self.thumbnail_label.setPixmap(pixmap.scaled(self.thumbnail_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

# ======================================== MAIN PHOTO EDITOR CLASS ========================================

class PhotoEditor(QMainWindow):
    def __init__(self, width=800, height=600, image_path=None, create_tabs=True):
        super().__init__()
        self.setWindowTitle("PhotoLab")
        self.setGeometry(100, 100, 900, 700)
        self.setWindowIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\icon_resize.png")) 
        self.image_loaded = False
        self.current_image_pixmap = None
        self.opened_tabs = []
        self.tab_layers = {}  
        self.drawing = False
        self.eyedropper_change_color = False
        self.eyedropper_group_of_pixels = False
        self.eyedropper_active = False  
        self.eyedropper_color = None
        self.eyedropper_group_color = None
        self.eyedropper_group_pixels = []
        self.eyedropper_group_active = False
        self.crop_mode = False
        self.thumbnail_window = ThumbnailWindow()

        self.font_size = 12
        self.bold = False
        self.italic = False
        self.font_family = "Arial"
        
        self.undo_stack = []
        self.redo_stack = []
        
        self.brush_color = QColor(Qt.black)  
        self.shape_type = None
        self.shape_color = self.brush_color

        self.canvas_width = width
        self.canvas_height = height
        self.image_path = image_path
        self.create_tabs = create_tabs
        self.canvas_view = None

        self.brush_color = QColor("#000000")  
        self.brush_size = 5  

        eyedropper_pixmap = QPixmap(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\eyedropper.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.eyedropper_cursor = QCursor(eyedropper_pixmap, 0, 15)  # Set hotspot to the bottom center of the icon
        
        # Load the group of pixels icon and set the hotspot to the tip of the icon
        group_of_pixels_pixmap = QPixmap(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\eyedropper.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.group_of_pixels_cursor = QCursor(group_of_pixels_pixmap, 0, 15)  # Set hotspot to the bottom center of the icon

        # Menu Bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        filter_menu = menu_bar.addMenu("Filter")
        adjustments_menu = menu_bar.addMenu("Adjustments")

        # Add options to the "Filter" dropdown menu
        rgb_action = filter_menu.addAction("RGB")
        hsv_action = filter_menu.addAction("HSV")
        gray_action = filter_menu.addAction("GRAY")
        cie_action = filter_menu.addAction("CIE")
        hls_action = filter_menu.addAction("HLS")
        ycrcb_action = filter_menu.addAction("YCrCb")
        reset_action = filter_menu.addAction("Reset")

        # Connect actions to methods
        rgb_action.triggered.connect(lambda: self.apply_filter("RGB"))
        hsv_action.triggered.connect(lambda: self.apply_filter("HSV"))
        gray_action.triggered.connect(lambda: self.apply_filter("GRAY"))
        cie_action.triggered.connect(lambda: self.apply_filter("CIE"))
        hls_action.triggered.connect(lambda: self.apply_filter("HLS"))
        ycrcb_action.triggered.connect(lambda: self.apply_filter("YCrCb"))
        reset_action.triggered.connect(self.reset_filter)  # Connect Reset action

        # Add options to the "Adjustments" dropdown menu
        brightness_action = adjustments_menu.addAction("Brightness")
        contrast_action = adjustments_menu.addAction("Contrast")
        vibrance_action = adjustments_menu.addAction("Vibrance")
        exposure_action = adjustments_menu.addAction("Exposure")

        # Connect actions to methods
        brightness_action.triggered.connect(lambda: self.show_adjustment_dialog("Brightness"))
        contrast_action.triggered.connect(lambda: self.show_adjustment_dialog("Contrast"))
        vibrance_action.triggered.connect(lambda: self.show_adjustment_dialog("Vibrance"))
        exposure_action.triggered.connect(lambda: self.show_adjustment_dialog("Exposure"))

        # Add options to the "File" dropdown menu
        load_images_action = file_menu.addAction("Load image")
        save_image_action = file_menu.addAction("Save image")
        new_canvas_action = file_menu.addAction("New Canvas")  # Add New Canvas action
        recently_saved_action = file_menu.addAction("Recently saved")  # Add Recently saved action

        # Connect actions to methods
        load_images_action.triggered.connect(self.load_multiple_images)
        save_image_action.triggered.connect(self.save_image)
        new_canvas_action.triggered.connect(self.open_canvas_dialog)  # Connect New Canvas action
        recently_saved_action.triggered.connect(self.open_recently_saved_image)  # Connect Recently saved action
        
        # Toolbar
        tool_bar = QToolBar("Tools", self)
        tool_bar.setMovable(False)
        tool_bar.setStyleSheet("QToolBar { border: none; }")  
        tool_bar.setFixedHeight(90) 
        tool_bar_layout = tool_bar.layout()
        tool_bar_layout.setSpacing(10)  
        tool_bar_layout.setContentsMargins(5, 0, 50, 0) 

        # Create a spacer widget
        spacer = QWidget()
        spacer.setFixedSize(9, 9)  

        tool_bar.addWidget(spacer)

        # container widget for the undo, redo, and reset buttons
        button_container = QWidget()
        button_layout = QGridLayout(button_container)
        button_layout.setContentsMargins(0, 0, -10, 0)  
        button_layout.setSpacing(2)  

        undo_icon = QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\undo.png")  
        redo_icon = QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\redo.png")  

        undo_button = QPushButton()
        undo_button.setIcon(undo_icon)
        undo_button.setFixedSize(51, 30)  # Adjust the size as needed
        undo_button.clicked.connect(self.undo_action)
        button_layout.addWidget(undo_button, 0, 0)

        redo_button = QPushButton()
        redo_button.setIcon(redo_icon)
        redo_button.setFixedSize(51, 30)  # Adjust the size as needed
        redo_button.clicked.connect(self.redo_action)
        button_layout.addWidget(redo_button, 0, 1)

        # Add a "Reset All Changes" button below the undo and redo buttons
        reset_all_button = QPushButton("Reset All Changes")
        reset_all_button.setFixedSize(110, 30)  # Adjust the size as needed
        reset_all_button.clicked.connect(self.reset_all_changes)
        button_layout.addWidget(reset_all_button, 1, 0, 1, 2)  # Span across two columns

        # Add the button container to the toolbar
        tool_bar.addWidget(button_container)

        # Add a fixed-size spacer to create space between the Redo button and the Brush tools
        fixed_spacer = QWidget()
        fixed_spacer.setFixedSize(0, 0)  # Adjust the size to control the gap
        tool_bar.addWidget(fixed_spacer)

        # Container for Brush and Brush Size Buttons
        brush_container = QWidget()
        brush_layout = QVBoxLayout(brush_container)
        brush_layout.setContentsMargins(0, -35, 0, -35)  # Remove margins
        brush_layout.setSpacing(5)  # Adjust spacing as needed

        # Brush Button
        brush_button = QPushButton()
        brush_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\paint-brush.png"))  # Replace with the path to your brush icon
        brush_button.setIconSize(QSize(12, 12))  # Set the icon size
        brush_button.setFixedSize(60, 22)
        brush_button.setToolTip("Brush")
        brush_button.clicked.connect(self.activate_brush)
        brush_layout.addWidget(brush_button, alignment=Qt.AlignTop)

        # Brush Size Button with an image icon
        brush_size_button = QToolButton()
        brush_size_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\line.png"))  # Replace with the path to your image file
        brush_size_button.setFixedSize(59, 22)
        brush_size_button.setIconSize(QSize(25, 25))  # Set the icon size
        brush_size_button.setPopupMode(QToolButton.InstantPopup)  # Show menu on click
        brush_size_button.setAutoRaise(False)  # Ensure the button has a visible 3D-like container
        brush_size_button.setStyleSheet("QToolButton { border: 1px solid #adadad; background-color: #e1e1e1; }")
        brush_size_button.setToolTip("Brush Size")

        # Create the menu for the Brush Size button
        brush_size_menu = QMenu()

        # Add brush size options to the menu
        thin_action = QAction("Thin", self)
        thin_action.triggered.connect(lambda: self.set_brush_size(1))
        brush_size_menu.addAction(thin_action)

        medium_action = QAction("Medium", self)
        medium_action.triggered.connect(lambda: self.set_brush_size(5))
        brush_size_menu.addAction(medium_action)

        thick_action = QAction("Thick", self)
        thick_action.triggered.connect(lambda: self.set_brush_size(10))
        brush_size_menu.addAction(thick_action)

        extra_thick_action = QAction("Extra Thick", self)
        extra_thick_action.triggered.connect(lambda: self.set_brush_size(20))
        brush_size_menu.addAction(extra_thick_action)

        # Set the menu to the Brush Size button
        brush_size_button.setMenu(brush_size_menu)

        # Add the Brush Size button to the layout
        brush_layout.addWidget(brush_size_button, alignment=Qt.AlignTop)

        # Add a label below the Brush Size button
        brush_label = QLabel("Brush tools")
        brush_label.setContentsMargins(0, 5, 0, 0)  # Adjust margins as needed
        brush_layout.addWidget(brush_label, alignment=Qt.AlignCenter)

        # Add a spacer item below the label to push it upwards
        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        brush_layout.addItem(spacer)

        # Add the container to the toolbar
        tool_bar.addWidget(brush_container)

        # Shape Buttons Layout
        shape_container = QWidget()
        shape_layout = QGridLayout(shape_container)

        # Adjust the vertical spacing to move the shape container down
        shape_layout.setVerticalSpacing(1)  # Adjust this value as needed to align with the color palette

        # Alternatively, add a margin to the layout to move it down a bit
        shape_layout.setContentsMargins(15, 5, -15, 0)  # Adjust the top margin value to control the position
        shape_layout.addItem(QSpacerItem(0, -5, QSizePolicy.Minimum, QSizePolicy.Expanding), 0, 0, 1, 3)

        shape_label = QLabel("Shapes")
        shape_layout.addWidget(shape_label, 2, 0, 1, 3, alignment=Qt.AlignCenter)
        shape_label.setContentsMargins(0, -10, 0, 0)  # Adjust the margins as needed

       # Create buttons for each shape and add them to the layout
        rectangle_button = QPushButton()
        rectangle_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\rectangle.png"))  # Set your rectangle icon
        rectangle_button.setToolTip("Rectangle")
        rectangle_button.setFixedSize(25,25)  # Set the size of the button
        rectangle_button.clicked.connect(lambda: self.set_shape_type("rectangle"))

        circle_button = QPushButton()
        circle_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\circle.png"))  # Set your circle icon
        circle_button.setToolTip("Circle")
        circle_button.setFixedSize(25,25)  # Set the size of the button
        circle_button.clicked.connect(lambda: self.set_shape_type("circle"))

        oval_button = QPushButton()
        oval_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\ellipse.png"))  # Set your oval icon
        oval_button.setToolTip("Oval")
        oval_button.setFixedSize(25,25)  # Set the size of the button
        oval_button.clicked.connect(lambda: self.set_shape_type("oval"))

        line_button = QPushButton()
        line_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\minus.png"))  # Set your line icon
        line_button.setToolTip("Line")
        line_button.setFixedSize(25,25)  # Set the size of the button
        line_button.clicked.connect(lambda: self.set_shape_type("line"))

        triangle_button = QPushButton()
        triangle_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\triangle.png"))  # Set your triangle icon
        triangle_button.setToolTip("Triangle")
        triangle_button.setFixedSize(25,25)  # Set the size of the button
        triangle_button.clicked.connect(lambda: self.set_shape_type("triangle"))

        star_button = QPushButton()
        star_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\star.png"))  # Set your star icon
        star_button.setToolTip("Star")
        star_button.setFixedSize(25, 25)  # Set the size of the button
        star_button.clicked.connect(lambda: self.set_shape_type("star"))

        shape_layout.addItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed), 2, 0, 1, 3)

        # Add buttons to the layout
        shape_layout.addWidget(rectangle_button, 0, 0)
        shape_layout.addWidget(circle_button, 0, 1)
        shape_layout.addWidget(oval_button, 0, 2)
        shape_layout.addWidget(line_button, 1, 0)
        shape_layout.addWidget(triangle_button, 1, 1)
        shape_layout.addWidget(star_button, 1, 2)

        # Add the shape container to the toolbar
        tool_bar.addWidget(shape_container)

        # Color Palette and Color Display Box with labels below
        color_container = QWidget()
        color_layout = QHBoxLayout(color_container)  # Use QHBoxLayout to place items side-by-side

        # Create a container for the color palette and its label
        palette_container = QWidget()
        palette_layout = QVBoxLayout(palette_container)

        # Add the color palette widget to the palette container
        self.color_palette = self.create_color_palette()
        palette_layout.addWidget(self.color_palette)

        # Add the "Colors" label below the color palette
        color_label = QLabel("Color Palatte")
        palette_layout.addWidget(color_label, alignment=Qt.AlignCenter)

        # Adjust the top margin of the palette_layout to push the label down
        palette_layout.setContentsMargins(0, 0, 0, 0)  # Adjust the top margin as needed

        # Add the palette container to the main color layout
        color_layout.addWidget(palette_container)

        # Create a container for the color display box and its label
        selected_color_container = QWidget()
        selected_color_layout = QVBoxLayout(selected_color_container)

        # Color display box (selected color) to the right of the color palette
        self.color_display_box = QLabel()
        self.color_display_box.setFixedSize(40,53)
        self.color_display_box.setStyleSheet("background-color: #FFFFFF; border: 1px solid black;")
        selected_color_layout.addWidget(self.color_display_box)

        # Create a horizontal layout for the label and spacer
        label_layout = QHBoxLayout()
        selected_color_label = QLabel("Selected")
        label_layout.addWidget(selected_color_label)

        # Add the horizontal layout to the vertical layout
        selected_color_layout.addLayout(label_layout)
        selected_color_label.setContentsMargins(-15, 0, 0, 0)  # Adjust the margins for the label as needed

        # Adjust the margins for the layout as needed
        selected_color_layout.setContentsMargins(5, 0, 0, 0)

        # Add the selected color container to the main color layout (to the right of the palette container)
        color_layout.addWidget(selected_color_container)

        # Add the color container to the toolbar
        tool_bar.addWidget(color_container)

        # Adjust the size policies and margins of the containers
        selected_color_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        selected_color_layout.setContentsMargins(0, 0, 0, 0)

        # Create a container for the text tool buttons and their label
        text_tool_container = QWidget()
        text_tool_layout = QGridLayout(text_tool_container)
        text_tool_layout.setContentsMargins(0, 5, 0, 0)  # Remove margins
        text_tool_layout.setSpacing(1)  # Remove spacing
        text_tool_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Font size button
        font_size_button = QToolButton()
        font_size_button.setText("Font Size")
        font_size_button.setPopupMode(QToolButton.InstantPopup)
        font_size_button.setFixedSize(70, 23)  # Set the desired size (width, height)
        font_size_menu = QMenu()
        for size in [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 64, 72]:
            action = QAction(str(size), self)
            action.triggered.connect(lambda _, s=size: self.set_font_size(s))
            font_size_menu.addAction(action)
        font_size_button.setMenu(font_size_menu)
        text_tool_layout.addWidget(font_size_button, 0, 0)

        # Bold button
        bold_button = QPushButton("Bold")
        bold_button.setCheckable(True)
        bold_button.clicked.connect(self.toggle_bold)
        text_tool_layout.addWidget(bold_button, 0, 1)

        # Italic button
        italic_button = QPushButton("Italic")
        italic_button.setCheckable(True)
        italic_button.clicked.connect(self.toggle_italic)
        text_tool_layout.addWidget(italic_button, 0, 2)

        # Font selection button
        font_combo_box = QFontComboBox()
        font_combo_box.currentFontChanged.connect(self.set_font_family)
        text_tool_layout.addWidget(font_combo_box, 1, 0, 1, 3)  # Span across 3 columns

        # Add a label below the text tool buttons
        text_tool_label = QLabel("Text Tool")
        text_tool_label.setContentsMargins(0, 5, 0, 0)  # Adjust margins as needed
        text_tool_layout.addWidget(text_tool_label, 2, 0, 1, 3, alignment=Qt.AlignCenter)

        # Add a spacer item to move the text tool container to the right
        spacer_item = QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        color_layout.addItem(spacer_item)

        # Add the text tool container to the main color layout (to the right of the selected color container)
        color_layout.addWidget(text_tool_container, alignment=Qt.AlignLeft)   
                     
       # Create a container for the thumbnail button and label
        thumbnail_container = QWidget()
        thumbnail_layout = QVBoxLayout(thumbnail_container)
        thumbnail_layout.setContentsMargins(0, 12, 0, 0)  # Adjust margins as needed
        thumbnail_layout.setSpacing(0)  # Adjust spacing as needed

        # Thumbnail Button
        thumbnail_button = QPushButton()
        thumbnail_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\video.png"))
        thumbnail_button.setToolTip("Thumbnail")
        thumbnail_button.setFixedSize(42, 48)
        thumbnail_button.clicked.connect(self.show_thumbnail_window)
        thumbnail_layout.addWidget(thumbnail_button, alignment=Qt.AlignCenter)

        # Thumbnail Label
        thumbnail_label = QLabel("Thumbnail")
        thumbnail_label.setContentsMargins(0, 0, 0, 5)  # Adjust margins as needed
        thumbnail_layout.addWidget(thumbnail_label, alignment=Qt.AlignCenter)

        # Add the container to the toolbar
        tool_bar.addWidget(thumbnail_container)

        # Create a container for the panning button and label
        panning_container = QWidget()
        panning_layout = QVBoxLayout(panning_container)
        panning_layout.setContentsMargins(0, 12, 0, 0)  # Adjust margins as needed
        panning_layout.setSpacing(0)  # Adjust spacing as needed

        # Panning Button
        panning_button = QPushButton()
        panning_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\all-directions.png"))  # Set the icon later
        panning_button.setToolTip("Panning")
        panning_button.setFixedSize(42, 48)
        panning_button.clicked.connect(self.activate_panning)
        panning_layout.addWidget(panning_button, alignment=Qt.AlignCenter)

        # Panning Label
        panning_label = QLabel("Panning")
        panning_label.setContentsMargins(0, 0, 0, 5)  # Adjust margins as needed
        panning_layout.addWidget(panning_label, alignment=Qt.AlignCenter)

        # Add the container to the toolbar
        tool_bar.addWidget(panning_container)

        self.addToolBar(Qt.TopToolBarArea, tool_bar)

        # Canvas setup
        self.canvas_scene = QGraphicsScene()  # Initialize scene before view
        self.canvas_view = CanvasView(self, None, None, self.canvas_scene)
        self.canvas_view.setScene(self.canvas_scene)
        self.canvas_scene.setBackgroundBrush(QColor("#e0e0e0"))

        # Only create tabs if create_tabs is True
        self.tab_widget = CustomTabWidget()
        if self.create_tabs:
            if image_path:
                # Initialize layers panel before loading image
                self.initialize_layers_panel()
                self.load_image_tab(image_path)  # Load image tab if image_path is provided
            else:
                self.create_blank_canvas_tab(width, height)  # Pass width and height here

        # Add canvas view to the first tab if no other tabs exist
        if self.create_tabs and len(self.opened_tabs) == 0:
            self.tab_widget.addTab(self.canvas_view, "New Canvas")
            self.opened_tabs.append("New Canvas")

        # Initialize layers panel
        self.initialize_layers_panel()

       # Main Layout
        left_sidebar = QWidget()
        left_layout = QVBoxLayout(left_sidebar)
        icons = {
            "Stitch": r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\merge.png",
            "Scale": r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\scale.png",
            "Rotate": r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\rotate.png",
            "Translate": r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\move-right.png",
            "Text": r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\font.png"
        }
        for tool, icon_path in icons.items():
            button = QPushButton()
            button.setIcon(QIcon(icon_path))
            left_layout.addWidget(button)
            label = QLabel(tool)  # Add this line to create a label
            label.setAlignment(Qt.AlignCenter)  # Center align the label
            left_layout.addWidget(label)  # Add the label to the layout
            if tool == "Rotate":
                button.clicked.connect(self.rotate_canvas)
            elif tool == "Scale":
                button.clicked.connect(self.show_scaling_dialog)
            elif tool == "Text":
                button.clicked.connect(self.activate_text_tool)
            elif tool == "Translate":
                button.clicked.connect(self.activate_translate_tool)
            elif tool == "Stitch":
                button.clicked.connect(self.stitch_images)  # Connect the stitch button

        # Eyedropper Button with Drop Down Menu
        eyedropper_button = QToolButton()
        eyedropper_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\eyedropper_icon.png"))
        eyedropper_button.setPopupMode(QToolButton.InstantPopup)
        eyedropper_button.setFixedSize(42, 26)
        eyedropper_menu = QMenu()
        select_color_action = QAction("Select Color", self)
        select_color_action.triggered.connect(self.activate_eyedropper)
        eyedropper_menu.addAction(select_color_action)
        change_color_action = QAction("Change Color", self)
        change_color_action.triggered.connect(self.activate_eyedropper_change_color)
        eyedropper_menu.addAction(change_color_action)
        group_of_pixels_action = QAction("Group of Pixels", self)
        group_of_pixels_action.triggered.connect(self.activate_eyedropper_group_of_pixels)
        eyedropper_menu.addAction(group_of_pixels_action)
        eyedropper_button.setMenu(eyedropper_menu)
        left_layout.addWidget(eyedropper_button)
        eyedropper_label = QLabel("eye<br>dropper")  # Use HTML to create a line break
        eyedropper_label.setAlignment(Qt.AlignCenter)  # Center align the label
        left_layout.addWidget(eyedropper_label)  # Add the label to the layout

        crop_button = QPushButton()
        crop_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\crop_icon.png"))
        crop_button.clicked.connect(self.activate_crop_mode)
        left_layout.addWidget(crop_button)
        crop_button.setFixedSize(42, 26)
        crop_label = QLabel("Crop")  # Add this line to create a label
        crop_label.setAlignment(Qt.AlignCenter)  # Center align the label
        left_layout.addWidget(crop_label)  # Add the label to the layout

        # Set size policy and minimum/maximum size for the left panel
        left_sidebar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        left_sidebar.setMinimumWidth(65)  # Set minimum width
        left_sidebar.setMaximumWidth(65)  # Set maximum width

        main_layout = QHBoxLayout()
        main_layout.addWidget(left_sidebar, 1)
        main_layout.addWidget(self.tab_widget, 4)
        main_layout.addWidget(self.layers_panel, 1)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Status Bar to show canvas details
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()  # Initial status bar update

        # Bottom right panel for zoom controls within the status bar
        zoom_controls_container = QWidget()
        zoom_controls_layout = QHBoxLayout(zoom_controls_container)
        zoom_controls_layout.setSpacing(0)  # Reduce spacing between widgets to zero
        zoom_controls_layout.setContentsMargins(0, 0, 25,25)  # Remove margins

        # Align everything to the right
        zoom_controls_layout.setAlignment(Qt.AlignRight)

        # Minus icon for zoom out
        zoom_out_button = QPushButton()
        zoom_out_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\zoomOut.png"))  # Path to your minus icon
        zoom_out_button.setToolTip("Zoom Out")
        zoom_out_button.setFixedSize(23, 23)
        zoom_out_button.clicked.connect(lambda: self.zoom_slider.setValue(self.zoom_slider.value() - 10))
        zoom_controls_layout.addWidget(zoom_out_button)

        # Zoom slider
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(10)
        self.zoom_slider.setFixedSize(150, 20)
        self.zoom_slider.valueChanged.connect(self.zoom_image)
        zoom_controls_layout.addWidget(self.zoom_slider)

        # Plus icon for zoom in
        zoom_in_button = QPushButton()
        zoom_in_button.setIcon(QIcon(r"C:\Users\nrsak\year3\project_env\2024_DIP-Assignment 1_NUR SAKINAH BINTI MOHAMMAD ALI_BS22110305\Icons\zoomIn.png"))  # Path to your plus icon
        zoom_in_button.setToolTip("Zoom In")
        zoom_in_button.setFixedSize(23, 23)
        zoom_in_button.clicked.connect(lambda: self.zoom_slider.setValue(self.zoom_slider.value() + 10))
        zoom_controls_layout.addWidget(zoom_in_button)

        # Add the zoom controls container to the status bar
        self.status_bar.addPermanentWidget(zoom_controls_container)

        # Enable mouse wheel zooming
        self.zoom_level = 0
        self.canvas_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.canvas_view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        # Connect tab change signal to update layers
        self.tab_widget.currentChanged.connect(self.update_layers_panel)

    def reset_all_changes(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == -1:
            self.statusBar().showMessage("No image to reset.")
            return

        current_view = self.tab_widget.widget(current_tab_index)
        if isinstance(current_view, CanvasView):
            original_pixmap = current_view.original_pixmap
            if original_pixmap:
                # Clear all items from the scene except the original image
                for item in current_view.canvas_scene.items():
                    if item != current_view.canvas_item:
                        current_view.canvas_scene.removeItem(item)

                # Restore the original pixmap
                current_view.canvas_pixmap = QPixmap(original_pixmap)
                current_view.canvas_item.setPixmap(current_view.canvas_pixmap)
                current_view.canvas_scene.update()

                # Clear all layers except the original image layer
                current_view.layers = [layer for layer in current_view.layers if layer.pixmap_item == current_view.canvas_item]
                self.update_layers_panel()

                self.statusBar().showMessage("All changes reset to original state.")
                self.undo_stack.clear()  # Clear the undo stack
                self.redo_stack.clear()  # Clear the redo stack

                # Deactivate all tools
                self.deactivate_all_tools()

                # Reset brush tool state
                self.drawing = False
                self.brush_color = QColor("#000000")  # Default to black
                self.brush_size = 5  # Default brush size

                # Reset shapes tool state
                self.shape_type = None
                self.shape_color = self.brush_color

                # Reset eyedropper tool state
                self.eyedropper_active = False
                self.eyedropper_change_color = False
                self.eyedropper_group_active = False

                # Reset crop mode
                self.crop_mode = False

                # Reset translate and panning states
                self.translate_active = False
                self.panning_active = False

                # Reset text tool state
                self.font_size = 12
                self.bold = False
                self.italic = False
                self.font_family = "Arial"

                # Reset cursor
                current_view.unsetCursor()

                # Reset the position of the canvas item
                current_view.canvas_item.setPos(0, 0)

                # Reset the transformation of the canvas item
                current_view.canvas_item.setTransform(QTransform())

            else:
                self.statusBar().showMessage("Original image not found.")

    def show_adjustment_dialog(self, adjustment_type):
        self.deactivate_all_tools()
        self.statusBar().showMessage(f"{adjustment_type} adjustment activated.")
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Adjust {adjustment_type}")
        layout = QVBoxLayout()
        
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(-50)  # Adjust the range to prevent extreme values
        slider.setMaximum(50)
        slider.setValue(0)
        layout.addWidget(slider)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        def apply_adjustment(value):
            current_tab_index = self.tab_widget.currentIndex()
            if current_tab_index == -1:
                return
            
            current_view = self.tab_widget.widget(current_tab_index)
            if isinstance(current_view, CanvasView):
                # Use the original image for adjustments
                image = current_view.original_image
                if image is None:
                    return
                
                if not hasattr(current_view, 'original_pixmap_snapshot'):
                    current_view.original_pixmap_snapshot = QPixmap(current_view.canvas_pixmap)

                if adjustment_type == "Brightness":
                    # Scale the value to a smaller range and add a small offset
                    scaled_value = value * 1.27  # Scale -50 to 50 to approximately -64 to 64
                    adjusted_image = self.adjust_brightness(image, scaled_value)
                
                elif adjustment_type == "Contrast":
                    adjusted_image = self.adjust_contrast(image, value)
                
                elif adjustment_type == "Vibrance":
                    adjusted_image = self.adjust_vibrance(image, value)
                
                elif adjustment_type == "Exposure":
                    adjusted_image = self.adjust_exposure(image, value)

                else:
                    return
                
                self.update_canvas_with_image(current_view, adjusted_image)
                self.update_thumbnail()
        
        slider.valueChanged.connect(apply_adjustment)
        
        def finalize_adjustment():
            current_tab_index = self.tab_widget.currentIndex()
            if current_tab_index == -1:
                return
            
            current_view = self.tab_widget.widget(current_tab_index)
            if isinstance(current_view, CanvasView):
                adjusted_pixmap_snapshot = QPixmap(current_view.canvas_pixmap)
                
                def undo_adjustment():
                    if hasattr(current_view, 'original_pixmap_snapshot'):
                        current_view.canvas_pixmap = QPixmap(current_view.original_pixmap_snapshot)
                        current_view.canvas_item.setPixmap(current_view.canvas_pixmap)
                        current_view.canvas_scene.update()
                
                def redo_adjustment():
                    current_view.canvas_pixmap = QPixmap(adjusted_pixmap_snapshot)
                    current_view.canvas_item.setPixmap(current_view.canvas_pixmap)
                    current_view.canvas_scene.update()
                
                self.undo_stack.append({
                    'undo': undo_adjustment,
                    'redo': redo_adjustment
                })
                self.redo_stack.clear()
        
        slider.sliderReleased.connect(finalize_adjustment)
        
        if dialog.exec_() == QDialog.Accepted:
            self.statusBar().showMessage(f"{adjustment_type} adjustment applied.")
        else:
            self.statusBar().showMessage(f"{adjustment_type} adjustment canceled.")
            self.undo_action()
            
    def adjust_brightness(self, image, value):
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float64)
        
        # Normalize and adjust the V channel
        hsv[:, :, 2] = hsv[:, :, 2] + value
        
        # Clip to valid range to prevent extreme values
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 10, 245)  # Prevent completely black or white
        
        # Convert back to BGR
        hsv = hsv.astype(np.uint8)
        adjusted_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)  # Convert to RGB for display
        return adjusted_image

    def adjust_contrast(self, image, value):
        # Adjust contrast by scaling the pixel values, clamping the result
        alpha = 1 + (value / 100.0)
        adjusted_image = cv2.convertScaleAbs(image, alpha=alpha, beta=0)
        adjusted_image = cv2.cvtColor(adjusted_image, cv2.COLOR_BGR2RGB)  # Convert to RGB for display
        return adjusted_image

    def adjust_vibrance(self, image, value):
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float64)
        
        # Adjust the saturation channel
        hsv[..., 1] = np.clip(hsv[..., 1] + value, 0, 255)
        
        # Convert back to BGR color space
        hsv = hsv.astype(np.uint8)
        adjusted_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)  # Convert to RGB for display
        return adjusted_image

    def adjust_exposure(self, image, value):
        # Adjust exposure by scaling the pixel values, clamping the result
        alpha = 1 + (value / 100.0)
        adjusted_image = cv2.convertScaleAbs(image, alpha=alpha, beta=0)
        adjusted_image = cv2.cvtColor(adjusted_image, cv2.COLOR_BGR2RGB)  # Convert to RGB for display
        return adjusted_image

    def stitch_images(self):
        self.deactivate_all_tools()
        self.statusBar().showMessage("Stitching tool activated. Select images to stitch.")

        # Prompt user to load images
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open Image Files", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if not file_paths:
            self.statusBar().showMessage("No images selected for stitching.")
            return

        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == -1:
            self.statusBar().showMessage("No base image to stitch with.")
            return

        current_view = self.tab_widget.widget(current_tab_index)
        if not isinstance(current_view, CanvasView):
            self.statusBar().showMessage("Invalid tab or view.")
            return

        base_image = self.pixmap_to_cv2(current_view.canvas_pixmap)
        if base_image is None:
            self.statusBar().showMessage("Failed to convert base image.")
            return

        base_height = base_image.shape[0]
        stitched_image = base_image
        new_layers = []

        # Save the original scene properties and visibility state
        original_scene_rect = current_view.canvas_scene.sceneRect()
        original_canvas_pixmap = QPixmap(current_view.canvas_pixmap)
        original_transform = current_view.canvas_item.transform()
        original_canvas_item = current_view.canvas_item  # Store the original canvas item

        # Save the visibility state of the original layers
        original_layer_visibility = {layer: layer.pixmap_item.isVisible() for layer in current_view.layers}

        for path in file_paths:
            pixmap = QPixmap(path)
            if pixmap.isNull():
                self.statusBar().showMessage(f"Failed to load image from {path}")
                continue

            image = self.pixmap_to_cv2(pixmap)
            if image is None:
                self.statusBar().showMessage(f"Failed to convert image from {path}")
                continue

            # Resize the image to match the height of the base image
            height, width = image.shape[:2]
            if height != base_height:
                new_width = int(width * (base_height / height))
                image = cv2.resize(image, (new_width, base_height))

            # Stitch images horizontally
            stitched_image = np.hstack((stitched_image, image))

            # Add each loaded image as a separate layer
            q_image = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_RGB888)
            canvas_item = QGraphicsPixmapItem(QPixmap.fromImage(q_image))
            current_view.canvas_scene.addItem(canvas_item)

            new_layer = Layer(f"Stitched Layer: {os.path.basename(path)}", canvas_item)
            new_layers.append(new_layer)

        # Create a new layer for the stitched image
        stitched_pixmap = self.cv2_to_pixmap(stitched_image)
        stitched_item = QGraphicsPixmapItem(stitched_pixmap)
        current_view.canvas_scene.addItem(stitched_item)

        # Update the current canvas to the stitched image
        current_view.canvas_pixmap = stitched_pixmap
        current_view.canvas_item = stitched_item

        # Update the scene rectangle to fit the new stitched image
        current_view.canvas_scene.setSceneRect(stitched_item.boundingRect())

        stitched_layer = Layer("Stitched Image", stitched_item)
        current_view.layers.extend(new_layers)
        current_view.layers.append(stitched_layer)
        self.update_layers_panel()

        def undo_stitch():
            # Remove new stitched layers
            for layer in new_layers:
                current_view.layers.remove(layer)
                current_view.canvas_scene.removeItem(layer.pixmap_item)

            # Remove the stitched image layer
            current_view.layers.remove(stitched_layer)
            current_view.canvas_scene.removeItem(stitched_item)

            # Restore the original canvas settings
            current_view.canvas_scene.setSceneRect(original_scene_rect)
            current_view.canvas_pixmap = original_canvas_pixmap
            current_view.canvas_item = original_canvas_item
            current_view.canvas_item.setPixmap(original_canvas_pixmap)
            current_view.canvas_item.setTransform(original_transform)
            
            # Re-add the original canvas item back to the scene (if removed during stitching)
            if not current_view.canvas_scene.items().count(original_canvas_item):
                current_view.canvas_scene.addItem(original_canvas_item)

            # Restore the original layer visibility state
            for layer, visibility in original_layer_visibility.items():
                layer.set_visible(visibility)

            self.update_layers_panel()
            self.statusBar().showMessage("Undo stitching.")

        def redo_stitch():
            # Re-add each stitched layer
            for layer in new_layers:
                current_view.layers.append(layer)
                current_view.canvas_scene.addItem(layer.pixmap_item)
            
            # Re-add the stitched image layer and update the scene rectangle
            current_view.layers.append(stitched_layer)
            current_view.canvas_scene.addItem(stitched_item)
            current_view.canvas_scene.setSceneRect(stitched_item.boundingRect())
            
            # Set the current view to the stitched pixmap and item
            current_view.canvas_pixmap = stitched_pixmap
            current_view.canvas_item = stitched_item
            self.update_layers_panel()

        # Push the stitching action to the undo stack and clear redo stack
        self.undo_stack.append({
            'undo': undo_stitch,
            'redo': redo_stitch
        })
        self.redo_stack.clear()
        self.statusBar().showMessage("Images stitched successfully.")


    def cv2_to_pixmap(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_image)
    
    def activate_panning(self):
        self.deactivate_all_tools()
        self.statusBar().showMessage("Panning activated. Click and drag to pan the image.")
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView):
            current_view.setCursor(Qt.OpenHandCursor)
            current_view.panning_active = True
    
    def set_font_size(self, size):
        self.font_size = size
        self.statusBar().showMessage(f"Font size set to {size}")
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView) and current_view.text_item:
            font = current_view.text_item.font()
            font.setPointSize(size)
            current_view.text_item.setFont(font)

    def toggle_bold(self):
        self.bold = not self.bold
        self.statusBar().showMessage("Bold " + ("enabled" if self.bold else "disabled"))
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView) and current_view.text_item:
            font = current_view.text_item.font()
            font.setBold(self.bold)
            current_view.text_item.setFont(font)

    def toggle_italic(self):
        self.italic = not self.italic
        self.statusBar().showMessage("Italic " + ("enabled" if self.italic else "disabled"))
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView) and current_view.text_item:
            font = current_view.text_item.font()
            font.setItalic(self.italic)
            current_view.text_item.setFont(font)

    def set_font_family(self, font):
        self.font_family = font.family()
        self.statusBar().showMessage(f"Font set to {self.font_family}")
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView) and current_view.text_item:
            font = current_view.text_item.font()
            font.setFamily(self.font_family)
            current_view.text_item.setFont(font)

    def open_canvas_dialog(self):
        dialog = CanvasDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            width, height = dialog.get_dimensions()
            if width and height:
                self.create_blank_canvas_tab(width, height)
            else:
                self.statusBar().showMessage("Invalid input for width or height.")

    def activate_text_tool(self):
        self.deactivate_all_tools()
        self.shape_type = None
        self.statusBar().showMessage("Text tool activated. Click on the canvas to add text.")
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView):
            current_view.setCursor(Qt.IBeamCursor)
            current_view.text_tool_active = True

    def reset_filter(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == -1:
            self.statusBar().showMessage("No image to reset.")
            return

        current_view = self.tab_widget.widget(current_tab_index)
        if isinstance(current_view, CanvasView):
            original_pixmap = current_view.original_pixmap
            if original_pixmap:
                current_view.canvas_pixmap = original_pixmap
                current_view.canvas_item.setPixmap(original_pixmap)
                current_view.canvas_scene.update()
                self.statusBar().showMessage("Image reset to original state.")
            else:
                self.statusBar().showMessage("Original image not found.")

    def apply_filter(self, filter_type):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == -1:
            self.statusBar().showMessage("No image to apply filter.")
            return

        current_view = self.tab_widget.widget(current_tab_index)
        if isinstance(current_view, CanvasView):
            # Reset the image to its original state before applying the filter
            if hasattr(current_view, 'original_image'):
                image = current_view.original_image.copy()
            else:
                self.statusBar().showMessage("Original image not found.")
                return

            if image is None:
                self.statusBar().showMessage("Failed to convert pixmap to image.")
                return

            # Capture the state of the image before applying the filter
            original_pixmap_snapshot = QPixmap(current_view.canvas_pixmap)

            # Debug: Print the color values before conversion
            print("Before conversion:", image[0, 0])

            if filter_type == "RGB":
                filtered_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            elif filter_type == "HSV":
                filtered_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            elif filter_type == "GRAY":
                filtered_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)  # Convert back to 3-channel image
            elif filter_type == "CIE":
                filtered_image = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
            elif filter_type == "HLS":
                filtered_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
            elif filter_type == "YCrCb":
                filtered_image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
            else:
                self.statusBar().showMessage("Unknown filter type.")
                return

            # Debug: Print the color values after conversion
            print("After conversion:", filtered_image[0, 0])

            self.update_canvas_with_image(current_view, filtered_image)
            self.statusBar().showMessage(f"Applied {filter_type} filter.")
            self.update_thumbnail()  # Update thumbnail after applying filter

            # Capture the state of the image after applying the filter
            filtered_pixmap_snapshot = QPixmap(current_view.canvas_pixmap)

            def undo_filter():
                current_view.canvas_pixmap = QPixmap(original_pixmap_snapshot)
                current_view.canvas_item.setPixmap(current_view.canvas_pixmap)
                current_view.canvas_scene.update()

            def redo_filter():
                current_view.canvas_pixmap = QPixmap(filtered_pixmap_snapshot)
                current_view.canvas_item.setPixmap(current_view.canvas_pixmap)
                current_view.canvas_scene.update()

            # Add the filter action to the undo stack and clear redo stack
            self.undo_stack.append({
                'undo': undo_filter,
                'redo': redo_filter
            })
            self.redo_stack.clear()

    def pixmap_to_cv2(self, pixmap):
        image = pixmap.toImage()
        image = image.convertToFormat(QImage.Format.Format_RGB32)
        width = image.width()
        height = image.height()
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

    """ def update_canvas_with_image(self, view, image):
        height, width = image.shape[:2]
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        view.canvas_pixmap = pixmap
        view.canvas_item.setPixmap(pixmap)
        view.canvas_scene.update() """

    def update_canvas_with_image(self, view, image):
        # Convert the image back to BGR format for display if necessary
        display_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        height, width, channel = display_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(display_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        view.canvas_pixmap = pixmap
        view.canvas_item.setPixmap(view.canvas_pixmap)
        view.canvas_scene.update()
        
    def zoom_image(self, value):
        factor = value / 100.0
        current_tab = self.tab_widget.currentWidget()
        if isinstance(current_tab, QGraphicsView):
            current_tab.setTransform(QTransform().scale(factor, factor))

    def undo_action(self):
        if self.undo_stack:
            action = self.undo_stack.pop()
            current_view = self.tab_widget.currentWidget()
            if isinstance(current_view, CanvasView):
                action['undo']()  # Undo the action
                self.redo_stack.append(action)  # Move to redo stack
                current_view.update()  # Force a refresh of the view
                self.update_layers_panel()
                self.update_thumbnail()  # Update the thumbnail

    def redo_action(self):
        if self.redo_stack:
            action = self.redo_stack.pop()
            current_view = self.tab_widget.currentWidget()
            if isinstance(current_view, CanvasView):
                action['redo']()  # Call the redo function for the action
                self.undo_stack.append(action)  # Move the action back to the undo stack
                current_view.update()  # Force a refresh of the view
                self.update_layers_panel()
                self.update_thumbnail()  # Update the thumbnail

    def initialize_layers_panel(self):
        self.layers_panel = QWidget()
        self.layers_layout = QVBoxLayout(self.layers_panel)
        
        # Add the label for the layer panel
        layers_label = QLabel("Layer Panel")
        layers_label.setStyleSheet("border: 1px solid black; padding: 4px; margin: 4px;")  # Adjust the box around the label
        self.layers_layout.addWidget(layers_label)
        
        self.layers_list = QListWidget()
        self.layers_layout.addWidget(self.layers_list)
        self.layers_list.itemClicked.connect(self.on_layer_item_clicked)
        
        # Add a box border around the layers panel
        self.layers_panel.setStyleSheet("border: 1px solid black;")
        
        # Adjust the box sizing
        self.layers_panel.setMinimumSize(200, 300)  # Set minimum size (width, height)
        self.layers_panel.setMaximumSize(300, 600)  # Set maximum size (width, height)
        self.layers_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy

    def create_blank_canvas(self):
        blank_image = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255
        q_image = QImage(blank_image.data, self.canvas_width, self.canvas_height, 3 * self.canvas_width, QImage.Format_RGB888)
        
        canvas_pixmap = QPixmap.fromImage(q_image)
        canvas_scene = QGraphicsScene()
        canvas_item = QGraphicsPixmapItem(canvas_pixmap)
        canvas_scene.addItem(canvas_item)
        
        # Set the background color of the scene to gray
        canvas_scene.setBackgroundBrush(QColor("#e0e0e0"))
        
        # Set the scene rectangle to fit the canvas
        canvas_scene.setSceneRect(0, 0, self.canvas_width, self.canvas_height)

        # Draw the boundary rectangle once
        boundary_pen = QPen(Qt.black, 1)
        boundary_rect_item = canvas_scene.addRect(0, 0, self.canvas_width, self.canvas_height, boundary_pen)

        return canvas_scene, canvas_item, canvas_pixmap, boundary_rect_item

    def update_layers_panel(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == -1:
            return

        current_view = self.tab_widget.widget(current_tab_index)
        if isinstance(current_view, CanvasView):
            self.layers_list.clear()
            for layer in current_view.layers:
                if layer is not None and hasattr(layer, 'name'):
                    item = QListWidgetItem(layer.name)
                    layer.update_icon()  # Ensure the icon is updated
                    item.setIcon(layer.icon)
                    self.layers_list.addItem(item)

    def show_thumbnail_window(self):
        # Show the thumbnail window as a popup
        self.thumbnail_window.show()  # Alternatively, use `exec_()` if you want it to block the main window
        self.update_thumbnail()

    def update_thumbnail(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == -1:
            return

        current_view = self.tab_widget.widget(current_tab_index)
        if isinstance(current_view, CanvasView):
            self.thumbnail_window.update_thumbnail(current_view.canvas_pixmap)

    def activate_translate_tool(self):
        self.deactivate_all_tools()
        self.shape_type = None
        self.statusBar().showMessage("Translate tool activated. Use arrow keys or drag to move the image.")
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView):
            current_view.setCursor(Qt.OpenHandCursor)
            current_view.translate_active = True
            current_view.show_translation_border()  # Show the translation border

    def activate_crop_mode(self):
        self.deactivate_all_tools()  # Add this line
        self.crop_mode = True
        self.statusBar().showMessage("Crop mode activated. Drag to select area.")

    def deactivate_crop_mode(self):
        self.crop_mode = False
        self.deactivate_all_tools()  # Add this line
        self.statusBar().showMessage("Crop mode deactivated.")
    
    def toggle_crop_mode(self):
        self.crop_mode = not self.crop_mode
        msg = "Crop mode activated." if self.crop_mode else "Crop mode deactivated."
        self.statusBar().showMessage(msg)
    
    def load_multiple_images(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open Image Files", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_paths:
            for path in file_paths:
                self.load_image_tab(path)

    """ def save_image(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == -1:  # No tab open
            self.statusBar().showMessage("No image to save.")
            return

        current_view = self.tab_widget.widget(current_tab_index)  # Get the view in the current tab
        if isinstance(current_view, CanvasView):
            updated_pixmap = current_view.canvas_pixmap
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Image File", "", 
                                                    "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;BMP Files (*.bmp)")
            if save_path:
                updated_pixmap.save(save_path)
                self.statusBar().showMessage(f"Image saved to {save_path}")
                self.recently_saved_image_path = save_path  # Store the path of the recently saved image
            else:
                self.statusBar().showMessage("Save operation cancelled.")
        else:
            self.statusBar().showMessage("Invalid tab or view.")
 """
    
    def save_image(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == -1:  # No tab open
            self.statusBar().showMessage("No image to save.")
            return

        current_view = self.tab_widget.widget(current_tab_index)  # Get the view in the current tab
        if isinstance(current_view, CanvasView):
            # Create a new QPixmap with the same size as the current scene
            scene_rect = current_view.canvas_scene.sceneRect()
            translated_pixmap = QPixmap(scene_rect.size().toSize())
            translated_pixmap.fill(Qt.transparent)  # Fill with transparent background

            # Use a QPainter to render the current scene onto the new QPixmap
            painter = QPainter(translated_pixmap)
            current_view.canvas_scene.render(painter)
            painter.end()

            # Save the new QPixmap to the specified file path
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Image File", "", 
                                                    "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;BMP Files (*.bmp)")
            if save_path:
                translated_pixmap.save(save_path)
                self.statusBar().showMessage(f"Image saved to {save_path}")
                self.recently_saved_image_path = save_path  # Store the path of the recently saved image
            else:
                self.statusBar().showMessage("Save operation cancelled.")
        else:
            self.statusBar().showMessage("Invalid tab or view.")

    def open_recently_saved_image(self):
        if hasattr(self, 'recently_saved_image_path') and self.recently_saved_image_path:
            self.load_image_tab(self.recently_saved_image_path)
            self.statusBar().showMessage(f"Opened recently saved image: {self.recently_saved_image_path}")
        else:
            self.statusBar().showMessage("No recently saved image found.")

    def on_layer_item_clicked(self, item):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == -1:
            return

        current_view = self.tab_widget.widget(current_tab_index)
        if isinstance(current_view, CanvasView):
            current_view.toggle_layer_visibility(item.text())

    def show_scaling_dialog(self):
        percentage, ok = QInputDialog.getInt(self, "Scale Image", "Enter scaling percentage:", 100, 1, 1000, 1)
        if ok:
            self.scale_image(percentage)

    def scale_image(self, percentage):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == -1:
            return

        current_view = self.tab_widget.widget(current_tab_index)
        if isinstance(current_view, CanvasView):
            original_pixmap = current_view.canvas_pixmap
            original_size = original_pixmap.size()
            new_size = original_size * (percentage / 100.0)
            scaled_pixmap = original_pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Create a new QGraphicsPixmapItem for the scaled image
            scaled_item = QGraphicsPixmapItem(scaled_pixmap)
            current_view.canvas_scene.addItem(scaled_item)

            # Add the scaled image as a new layer
            scaled_layer = Layer(f"Scaled {percentage}%", scaled_item)
            current_view.layers.append(scaled_layer)
            self.update_layers_panel()

            # Hide the original layer
            for layer in current_view.layers:
                if layer.pixmap_item == current_view.canvas_item:
                    layer.set_visible(False)
                    layer.update_icon()  # Update the icon to reflect visibility
                    break

            # Save the original transformation matrix and scene rectangle
            original_transform = current_view.canvas_item.transform()
            original_scene_rect = current_view.canvas_scene.sceneRect()

            # Define undo and redo functions for scaling action
            def undo_scale():
                current_view.canvas_scene.removeItem(scaled_item)
                current_view.layers.remove(scaled_layer)
                for layer in current_view.layers:
                    if layer.pixmap_item == current_view.canvas_item:
                        layer.set_visible(True)
                        layer.update_icon()  # Update the icon to reflect visibility
                        break
                current_view.canvas_item.setTransform(original_transform)  # Restore the original transformation matrix
                current_view.canvas_scene.setSceneRect(original_scene_rect)  # Restore the original scene rectangle
                self.update_layers_panel()

            def redo_scale():
                for layer in current_view.layers:
                    if layer.pixmap_item == current_view.canvas_item:
                        layer.set_visible(False)
                        layer.update_icon()  # Update the icon to reflect visibility
                        break
                current_view.canvas_scene.addItem(scaled_item)
                current_view.layers.append(scaled_layer)
                current_view.canvas_item.setTransform(QTransform())  # Reset the transformation matrix
                current_view.canvas_scene.setSceneRect(scaled_item.boundingRect())  # Update the scene rectangle
                self.update_layers_panel()

            # Add the undo/redo actions
            self.undo_stack.append({
                'undo': undo_scale,
                'redo': redo_scale
            })
            self.redo_stack.clear()  # Clear the redo stack on a new action

    def set_brush_size(self, size):
        # Update the brush size
        self.brush_size = size
        self.statusBar().showMessage(f"Brush size: {size}")

    def create_blank_canvas_tab(self, width, height):
        # Create a blank canvas area as a new tab
        self.canvas_width = width
        self.canvas_height = height
        canvas_scene, canvas_item, canvas_pixmap, boundary_rect_item = self.create_blank_canvas()
        
        # Pass boundary_rect_item to CanvasView
        canvas_view = CanvasView(self, canvas_pixmap, canvas_item, canvas_scene, boundary_rect_item)
        canvas_view.setScene(canvas_scene)
        canvas_view.original_pixmap = QPixmap(canvas_pixmap)  # Store the original pixmap
        self.tab_widget.addTab(canvas_view, "New Canvas")
        self.opened_tabs.append("New Canvas")
        self.update_status_bar()  # Update status bar with canvas details

    def load_image_tab(self, image_path):
        print(f"Loading image from path: {image_path}")  # Debug print
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Failed to load image from {image_path}")
            return

        # Create a new scene for each image tab
        new_scene = QGraphicsScene()
        canvas_item = QGraphicsPixmapItem(pixmap)
        new_scene.addItem(canvas_item)
        new_scene.setSceneRect(canvas_item.boundingRect())

        # Use CanvasView instead of QGraphicsView
        new_view = CanvasView(self, pixmap, canvas_item, new_scene)
        new_view.setScene(new_scene)  # Ensure the scene is set
        new_view.setStyleSheet("background-color: #e0e0e0;")
        new_view.fitInView(new_scene.sceneRect(), Qt.KeepAspectRatio)
        new_view.original_pixmap = QPixmap(pixmap)  # Store the original pixmap
        
        # Store the original image as a numpy array
        new_view.original_image = self.pixmap_to_cv2(pixmap)

        image_name = os.path.basename(image_path)
        self.tab_widget.addTab(new_view, image_name)

        # Initialize layers for the new tab
        new_view.layers.append(Layer(f"Original: {image_name}", canvas_item))
        self.update_layers_panel()

        # Update status bar with this image's details
        self.update_status_bar(image_path)  # Ensure image_path is passed here
        print(f"Status bar updated with image: {image_path}")  # Debug print

    def update_status_bar(self, image_path=None):
        if image_path:
            image_name = os.path.basename(image_path)
            image_type = image_path.split('.')[-1].upper()
            pixmap = QPixmap(image_path)
            print(f"Updating status bar with image: {image_path}")  # Debug print
            self.statusBar().showMessage(
                f"Image: {image_name}, Size: {pixmap.width()}x{pixmap.height()} pixels, Type: {image_type}"
            )
        else:
            self.statusBar().showMessage("No image loaded.")

    def create_color_palette(self):
        # Widget to hold the color palette
        palette_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)  # Space between rows

        # Define colors (based on the colors in your uploaded image)
        colors = [
            "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",  # Top row: normal colors
            "#808080", "#C0C0C0", "#FFB3B3", "#B3FFB3", "#B3B3FF", "#FFFFB3", "#FFB3FF"  # Bottom row: pastel colors
        ]
        
        button_size = 20  # Button size
        row_count = 8  # Number of colors per row

        # Create a QFrame to act as the border around the color palette
        palette_frame = QFrame()
        palette_frame.setStyleSheet("border: 1px solid black;")
        palette_frame_layout = QVBoxLayout(palette_frame)
        palette_frame_layout.setSpacing(5)  # Space between rows
        palette_frame_layout.setContentsMargins(5, 5, 5, 5)  # Add some padding inside the frame

        # Create rows with horizontal layouts and add to the frame layout
        for row_index in range(0, len(colors), row_count):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)  # Space between buttons in a row
            row_colors = colors[row_index:row_index + row_count]

            for color in row_colors:
                button = QPushButton()
                button.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
                button.setFixedSize(button_size, button_size)
                button.clicked.connect(lambda _, col=color: self.select_color(col))
                row_layout.addWidget(button)

            # Add the color selection button at the end of the bottom row
            if row_index == row_count:
                color_select_button = QPushButton("...")
                color_select_button.setFixedSize(button_size, button_size)
                color_select_button.clicked.connect(self.open_color_dialog)
                row_layout.addWidget(color_select_button)

            palette_frame_layout.addLayout(row_layout)

        # Add the frame to the main layout
        main_layout.addWidget(palette_frame)

        # Set layout margins if needed
        main_layout.setContentsMargins(0, 0, 0, 0)

        palette_widget.setLayout(main_layout)
        return palette_widget

    def open_color_dialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.select_color(color.name())
    
    def select_color(self, color):
        # Set the selected color for brush and shapes
        self.brush_color = QColor(color)
        self.shape_color = QColor(color)  # Use the same color for shapes
        self.color_display_box.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
        self.statusBar().showMessage(f"Selected color: {color}")
    
    def activate_brush(self):
        self.deactivate_all_tools()
        self.shape_type = None
        self.statusBar().showMessage("Brush activated. Use mouse to draw on canvas.")
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView):
            current_view.setCursor(Qt.CrossCursor)
            self.drawing = True

            # Save the initial state of the canvas for undo if it's not already saved
            if not hasattr(current_view, 'initial_pixmap'):
                current_view.initial_pixmap = QPixmap(current_view.canvas_pixmap)
            
            # Clear the redo stack to avoid redoing previous actions
            self.redo_stack.clear()

    def rotate_canvas(self):
            current_tab_index = self.tab_widget.currentIndex()
            if current_tab_index == -1:
                return

            current_view = self.tab_widget.widget(current_tab_index)
            if isinstance(current_view, CanvasView):
                current_view.rotate_image(90)  # Rotate by 90 degrees

    def closeEvent(self, event):
        # Clear all tabs on program exit
        self.opened_tabs.clear()  # Clear the list of opened tabs
        self.tab_widget.clear()  # Remove all tabs from the widget
        event.accept()  # Accept the close event to close the window

    def activate_eyedropper(self):
        self.deactivate_all_tools()
        self.shape_type = None
        self.statusBar().showMessage("Eyedropper activated. Click on the canvas to select color.")
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView):
            current_view.setCursor(self.eyedropper_cursor)
            self.eyedropper_active = True

    def activate_eyedropper_change_color(self):
        self.deactivate_all_tools()
        self.shape_type = None
        self.statusBar().showMessage("Eyedropper activated to change pixel color.")
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView):
            current_view.setCursor(self.eyedropper_cursor)
            self.eyedropper_change_color = True

    def activate_eyedropper_group_of_pixels(self):
        self.deactivate_all_tools()
        self.shape_type = None
        self.statusBar().showMessage("Eyedropper activated for group color change.")
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView):
            current_view.setCursor(self.group_of_pixels_cursor)
            self.eyedropper_group_active = True

    def deactivate_all_tools(self):
        self.drawing = False
        self.eyedropper_active = False
        self.eyedropper_change_color = False
        self.eyedropper_group_active = False
        self.eyedropper_group_color = False
        self.translate_active = False
        self.panning_active = False
        self.statusBar().clearMessage()
        current_view = self.tab_widget.currentWidget()
        if isinstance(current_view, CanvasView):
            current_view.unsetCursor()
            current_view.text_tool_active = False
            current_view.hide_translation_border()
            current_view.panning_active = False
            current_view.translate_active = False  # Ensure translate_active is reset
            current_view.dragging = False  # Ensure dragging is reset
        self.statusBar().showMessage("All tools deactivated.")

    def set_shape_type(self, shape_type):
        self.shape_type = shape_type
        self.statusBar().showMessage(f"Selected shape: {shape_type}")

    def wheelEvent(self, event):
        # Zoom in/out with the mouse wheel
        zoom_in_factor = 1.1
        zoom_out_factor = 1 / zoom_in_factor

        # Check if zooming in or out
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self.zoom_level += 1
        else:
            zoom_factor = zoom_out_factor
            self.zoom_level -= 1

        # Apply the zoom factor to the active view
        current_tab = self.tab_widget.currentWidget()
        if isinstance(current_tab, QGraphicsView):
            current_tab.scale(zoom_factor, zoom_factor)

        # Only fit in view the first time, after initial zoom interaction
        if self.image_loaded:
            self.canvas_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.canvas_view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
            self.image_loaded = False  # Reset flag so fitInView is not reapplied

# ======================================== LAYER CLASS ========================================

class Layer:
    def __init__(self, name, pixmap_item):
        self.name = name
        self.pixmap_item = pixmap_item
        self.visible = True

    def set_visible(self, visible):
        if self.pixmap_item is not None:
            self.visible = visible
            self.pixmap_item.setVisible(visible)
            self.update_icon()

    def update_icon(self):
        icon_path = EYE_ICON_PATH if self.visible else CLOSED_EYE_ICON_PATH
        self.icon = QIcon(icon_path)

# ======================================== CANVAS CLASS ========================================

class CanvasView(QGraphicsView):
    def __init__(self, editor, canvas_pixmap, canvas_item, canvas_scene, boundary_rect_item=None):
        super().__init__()
        self.editor = editor
        self.canvas_pixmap = canvas_pixmap
        self.canvas_item = canvas_item
        self.canvas_scene = canvas_scene
        self.boundary_rect_item = boundary_rect_item  # Store boundary rect item
        self.drawing = False  # Initialize drawing state
        self.last_point = QPoint()
        self.layers = []  # List to manage layers

        # Crop mode state and crop preview variables
        self.cropping = False
        self.crop_start_point = QPoint()
        self.crop_rect = None
        self.crop_preview_item = None  # Temporary rectangle for showing crop selection

        # Shape drawing state
        self.shape_preview_item = None  # Temporary shape preview item
        self.current_shape = None  # Store the currently drawn shape
        self.drawing_shape = False
        self.start_point = QPoint()

        self.text_tool_active = False
        self.text_item = None
        self.moving_text = False
        self.text_start_pos = None  # To store the initial position of the text

        self.translate_active = False  # Initialize translate state
        self.dragging = False  # Initialize dragging state

        self.panning_active = False

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def keyPressEvent(self, event):
        if self.translate_active:
            if event.key() == Qt.Key_Left:
                self.translate_image(-10, 0)
            elif event.key() == Qt.Key_Right:
                self.translate_image(10, 0)
            elif event.key() == Qt.Key_Up:
                self.translate_image(0, -10)
            elif event.key() == Qt.Key_Down:
                self.translate_image(0, 10)
        super().keyPressEvent(event)

    def translate_image(self, dx, dy):
        if self.canvas_item:
            initial_pos = self.canvas_item.pos()
            self.canvas_item.moveBy(dx, dy)
            final_pos = self.canvas_item.pos()
            self.canvas_scene.update()
            self.editor.statusBar().showMessage(f"Image translated to ({final_pos.x()}, {final_pos.y()})")

            # Update the translation border position
            if hasattr(self, 'translation_border_item') and self.translation_border_item:
                self.translation_border_item.setRect(self.canvas_item.boundingRect())

            # Define undo and redo functions
            def undo_translate():
                self.canvas_item.setPos(initial_pos)
                self.canvas_scene.update()
                self.editor.statusBar().showMessage(f"Undo: Image translated to ({initial_pos.x()}, {initial_pos.y()})")

            def redo_translate():
                self.canvas_item.setPos(final_pos)
                self.canvas_scene.update()
                self.editor.statusBar().showMessage(f"Redo: Image translated to ({final_pos.x()}, {final_pos.y()})")

            # Add the translation to the undo stack and clear redo stack
            self.editor.undo_stack.append({
                'undo': undo_translate,
                'redo': redo_translate
            })
            self.editor.redo_stack.clear()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())

            # Handling crop mode
            if self.editor.crop_mode:
                self.cropping = True
                self.crop_start_point = scene_pos

                # Initialize crop preview
                if self.crop_preview_item:
                    self.canvas_scene.removeItem(self.crop_preview_item)
                self.crop_rect = QRectF(self.crop_start_point, self.crop_start_point)
                self.crop_preview_item = self.canvas_scene.addRect(
                    self.crop_rect, QPen(Qt.yellow, 3, Qt.DashLine)
                )

            # Handling shape drawing
            elif self.editor.shape_type:
                self.drawing_shape = True
                self.start_point = scene_pos
                self.shape_preview_item = None  # Reset preview item on new shape

            # Handling brush tool
            elif self.editor.drawing:
                self.drawing = True
                self.last_point = scene_pos

                # Capture the state of the pixmap before the drawing starts for undo
                self.original_pixmap_snapshot = QPixmap(self.canvas_pixmap)

            # Handling eyedropper to select color
            elif self.editor.eyedropper_active and self.editor.statusBar().currentMessage() == "Eyedropper activated. Click on the canvas to select color.":
                image = self.canvas_pixmap.toImage()
                color = image.pixelColor(int(scene_pos.x()), int(scene_pos.y()))
                self.editor.select_color(color.name())

            # Handling eyedropper for changing pixel color
            elif self.editor.eyedropper_change_color and self.editor.statusBar().currentMessage() == "Eyedropper activated to change pixel color.":
                self.change_pixel_color(int(scene_pos.x()), int(scene_pos.y()), self.editor.brush_color)

            # Handling eyedropper for group color change
            elif self.editor.eyedropper_group_active and self.editor.statusBar().currentMessage() == "Eyedropper activated for group color change.":
                self.change_group_of_pixels_color(int(scene_pos.x()), int(scene_pos.y()), self.editor.brush_color)

            elif self.text_tool_active:
                if self.text_item and self.text_item.isUnderMouse():
                    self.moving_text = True
                    self.text_start_pos = self.text_item.pos()  # Capture the initial position
                    self.text_item.setFlag(QGraphicsItem.ItemIsMovable, True)
                else:
                    text, ok = QInputDialog.getText(self, "Input Text", "Enter text:")
                    if ok and text:
                        self.text_item = QGraphicsTextItem(text)
                        self.text_item.setDefaultTextColor(self.editor.brush_color)
                        font = QFont(self.editor.font_family, self.editor.font_size)
                        font.setBold(self.editor.bold)
                        font.setItalic(self.editor.italic)
                        self.text_item.setFont(font)
                        self.text_item.setPos(scene_pos)
                        self.canvas_scene.addItem(self.text_item)
                        self.text_item.setFlag(QGraphicsItem.ItemIsMovable, True)
                        self.moving_text = True

                        # Capture the state for undo
                        self.add_undo_redo_for_text(self.text_item, None, scene_pos)

            elif event.button() == Qt.LeftButton and self.translate_active:
                self.dragging = True
                self.last_point = self.mapToScene(event.pos())
                self.setCursor(Qt.ClosedHandCursor)
                self.initial_translate_pos = self.canvas_item.pos()  # Track the initial position

            elif event.button() == Qt.LeftButton and self.panning_active:
                self.dragging = True
                self.last_point = self.mapToScene(event.pos())
                self.setCursor(Qt.ClosedHandCursor)

        # Call the base class implementation to ensure proper event propagation
        super().mousePressEvent(event)
        self.editor.update_thumbnail()

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())

        # Ensure translate_active is defined and properly reset if required
        if not hasattr(self, 'translate_active'):
            self.translate_active = False

        # Update crop rectangle as the mouse moves
        if self.cropping and self.crop_start_point:
            current_point = self.mapToScene(event.pos())
            self.crop_rect = QRectF(self.crop_start_point, current_point).normalized()
            self.crop_preview_item.setRect(self.crop_rect)

        # Drawing on the canvas with the brush tool
        elif self.drawing and self.canvas_item and self.canvas_pixmap:
            current_point = self.mapToScene(event.pos())
            painter = QPainter(self.canvas_pixmap)
            pen = QPen(self.editor.brush_color, self.editor.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.last_point, current_point)
            painter.end()

            self.last_point = current_point
            self.canvas_item.setPixmap(self.canvas_pixmap)
            self.canvas_scene.update()

        # Drawing shapes (rectangle, circle, oval, line, triangle, star)
        elif self.drawing_shape and self.editor.shape_type:
            self.end_point = self.mapToScene(event.pos())
            shape_type = self.editor.shape_type
            color = self.editor.shape_color

            scene_rect = self.canvas_scene.sceneRect()
            self.end_point.setX(min(max(self.end_point.x(), scene_rect.left()), scene_rect.right()))
            self.end_point.setY(min(max(self.end_point.y(), scene_rect.top()), scene_rect.bottom()))

            if self.shape_preview_item:
                self.canvas_scene.removeItem(self.shape_preview_item)

            pen = QPen(color, 2, Qt.SolidLine)
            if shape_type == "rectangle":
                self.shape_preview_item = self.canvas_scene.addRect(QRectF(self.start_point, self.end_point), pen)
            elif shape_type == "circle":
                radius = (self.start_point - self.end_point).manhattanLength() / 2
                center = (self.start_point + self.end_point) / 2
                self.shape_preview_item = self.canvas_scene.addEllipse(
                    center.x() - radius, center.y() - radius, 2 * radius, 2 * radius, pen)
            elif shape_type == "oval":
                self.shape_preview_item = self.canvas_scene.addEllipse(QRectF(self.start_point, self.end_point), pen)
            elif shape_type == "line":
                self.shape_preview_item = self.canvas_scene.addLine(QLineF(self.start_point, self.end_point), pen)
            elif shape_type == "triangle":
                base_midpoint = QPointF((self.start_point.x() + self.end_point.x()) / 2, self.end_point.y())
                height = abs(self.start_point.y() - self.end_point.y())
                if self.start_point.y() > self.end_point.y():
                    apex = QPointF(base_midpoint.x(), self.end_point.y() - height)
                else:
                    apex = QPointF(base_midpoint.x(), self.end_point.y() + height)
                points = [QPointF(self.start_point.x(), self.end_point.y()), QPointF(self.end_point.x(), self.end_point.y()), apex]
                polygon = QPolygonF(points)
                self.shape_preview_item = self.canvas_scene.addPolygon(polygon, pen)
            elif shape_type == "star":
                center = (self.start_point + self.end_point) / 2
                radius = (self.start_point - self.end_point).manhattanLength() / 2
                points = []
                for i in range(10):
                    angle = i * 36
                    r = radius if i % 2 == 0 else radius / 2
                    x = center.x() + r * np.cos(np.radians(angle))
                    y = center.y() - r * np.sin(np.radians(angle))
                    points.append(QPointF(x, y))
                polygon = QPolygonF(points)
                self.shape_preview_item = self.canvas_scene.addPolygon(polygon, pen)

        # Moving text item
        elif self.moving_text and self.text_item:
            self.text_item.setPos(self.mapToScene(event.pos()))

        # Translate image if dragging and translate_active is true
        elif self.dragging and self.translate_active and self.canvas_item:
            current_point = self.mapToScene(event.pos())
            dx = current_point.x() - self.last_point.x()
            dy = current_point.y() - self.last_point.y()
            self.canvas_item.moveBy(dx, dy)  # Move canvas_item directly
            self.last_point = current_point
            self.canvas_scene.update()

        # Pan the view if panning_active is true
        elif self.dragging and self.panning_active:
            current_point = self.mapToScene(event.pos())
            delta = current_point - self.last_point
            self.translate(delta.x(), delta.y())
            self.last_point = current_point

        super().mouseMoveEvent(event)

        # Trigger thumbnail update if relevant actions occurred
        if self.drawing or self.drawing_shape or self.moving_text or self.dragging:
            self.editor.update_thumbnail()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.cropping and self.crop_rect:
                # Handle crop action and reset cropping state
                self.perform_crop(self.crop_rect)
                self.cropping = False
                self.editor.deactivate_crop_mode()
                if self.crop_preview_item:
                    self.canvas_scene.removeItem(self.crop_preview_item)
                    self.crop_preview_item = None
                self.editor.update_thumbnail()  # Update thumbnail after cropping
            elif self.drawing:
                # Complete the brush stroke and save it for undo
                self.drawing = False

                # Capture the current pixmap after the drawing is done
                brush_stroke_pixmap = QPixmap(self.canvas_pixmap)

                # Define undo/redo functions with unique snapshots
                original_pixmap_snapshot = QPixmap(self.original_pixmap_snapshot)
                final_brush_pixmap_snapshot = QPixmap(brush_stroke_pixmap)

                def undo_brush():
                    self.canvas_pixmap = QPixmap(original_pixmap_snapshot)
                    self.canvas_item.setPixmap(self.canvas_pixmap)
                    self.canvas_scene.update()

                def redo_brush():
                    self.canvas_pixmap = QPixmap(final_brush_pixmap_snapshot)
                    self.canvas_item.setPixmap(self.canvas_pixmap)
                    self.canvas_scene.update()

                # Add the brush stroke to the undo stack and clear redo stack
                self.editor.undo_stack.append({
                    'undo': undo_brush,
                    'redo': redo_brush
                })
                self.editor.redo_stack.clear()
                self.editor.update_thumbnail()  # Update thumbnail after drawing

            elif self.drawing_shape:
                # Finalize shape on release
                self.drawing_shape = False
                if self.shape_preview_item:
                    # Ensure the shape is within the canvas bounds
                    shape_rect = self.shape_preview_item.boundingRect()
                    if shape_rect.left() < 0 or shape_rect.top() < 0 or shape_rect.right() > self.canvas_scene.width() or shape_rect.bottom() > self.canvas_scene.height():
                        self.canvas_scene.removeItem(self.shape_preview_item)
                        self.shape_preview_item = None
                        return

                    # Remove the preview item
                    self.canvas_scene.removeItem(self.shape_preview_item)
                    self.shape_preview_item = None

                    # Capture the state of the pixmap before drawing the shape
                    original_pixmap_snapshot = QPixmap(self.canvas_pixmap)

                    # Draw the shape onto the canvas pixmap
                    painter = QPainter(self.canvas_pixmap)
                    pen = QPen(self.editor.shape_color, 2, Qt.SolidLine)
                    painter.setPen(pen)
                    if self.editor.shape_type == "rectangle":
                        painter.drawRect(QRectF(self.start_point, shape_rect.bottomRight()))
                    elif self.editor.shape_type == "circle":
                        radius = (self.start_point - shape_rect.bottomRight()).manhattanLength() / 2
                        center = (self.start_point + shape_rect.bottomRight()) / 2
                        painter.drawEllipse(center, radius, radius)
                    elif self.editor.shape_type == "oval":
                        painter.drawEllipse(QRectF(self.start_point, shape_rect.bottomRight()))
                    elif self.editor.shape_type == "line":
                        painter.drawLine(QLineF(self.start_point, self.end_point))
                    elif self.editor.shape_type == "triangle":
                        base_midpoint = QPointF((self.start_point.x() + shape_rect.bottomRight().x()) / 2, shape_rect.bottomRight().y())
                        height = abs(self.start_point.y() - shape_rect.bottomRight().y())
                        if self.start_point.y() > shape_rect.bottomRight().y():
                            apex = QPointF(base_midpoint.x(), shape_rect.bottomRight().y() - height)
                        else:
                            apex = QPointF(base_midpoint.x(), shape_rect.bottomRight().y() + height)
                        points = [QPointF(self.start_point.x(), shape_rect.bottomRight().y()), QPointF(shape_rect.bottomRight().x(), shape_rect.bottomRight().y()), apex]
                        polygon = QPolygonF(points)
                        painter.drawPolygon(polygon)
                    elif self.editor.shape_type == "star":
                        center = (self.start_point + shape_rect.bottomRight()) / 2
                        radius = (self.start_point - shape_rect.bottomRight()).manhattanLength() / 2
                        points = []
                        for i in range(10):
                            angle = i * 36
                            r = radius if i % 2 == 0 else radius / 2
                            x = center.x() + r * np.cos(np.radians(angle))
                            y = center.y() - r * np.sin(np.radians(angle))
                            points.append(QPointF(x, y))
                        polygon = QPolygonF(points)
                        painter.drawPolygon(polygon)
                    painter.end()

                    # Update the canvas item to reflect the drawn shape
                    self.canvas_item.setPixmap(self.canvas_pixmap)
                    self.canvas_scene.update()

                    # Capture the state of the pixmap after drawing the shape
                    shape_pixmap_snapshot = QPixmap(self.canvas_pixmap)

                    def undo_shape(original_pixmap_snapshot=original_pixmap_snapshot):
                        self.canvas_pixmap = QPixmap(original_pixmap_snapshot)
                        self.canvas_item.setPixmap(self.canvas_pixmap)
                        self.canvas_scene.update()

                    def redo_shape(shape_pixmap_snapshot=shape_pixmap_snapshot):
                        self.canvas_pixmap = QPixmap(shape_pixmap_snapshot)
                        self.canvas_item.setPixmap(self.canvas_pixmap)
                        self.canvas_scene.update()

                    self.editor.undo_stack.append({
                        'undo': undo_shape,
                        'redo': redo_shape
                    })
                    self.editor.redo_stack.clear()
                    self.editor.update_layers_panel()
                    self.editor.update_thumbnail()  # Update thumbnail after drawing shape

            elif self.moving_text and self.text_item:
                # Finalize text movement on release
                self.moving_text = False
                new_pos = self.text_item.pos()
                self.add_undo_redo_for_text(self.text_item, self.text_start_pos, new_pos)

                # Render the text onto the QPixmap
                self.render_text_onto_pixmap(self.text_item)

                # Remove the QGraphicsTextItem from the scene
                self.canvas_scene.removeItem(self.text_item)
                self.text_item = None

                self.editor.update_thumbnail()  # Update thumbnail after moving text

            elif event.button() == Qt.LeftButton and self.translate_active:
                self.dragging = False
                self.setCursor(Qt.OpenHandCursor)

                # Add the translated image as a new layer
                final_pos = self.canvas_item.pos()
                translated_layer = Layer(f"Translated to ({final_pos.x()}, {final_pos.y()})", self.canvas_item)
                self.layers.append(translated_layer)
                self.editor.update_layers_panel()

                # Define undo and redo functions for the translation
                initial_pos = self.initial_translate_pos
                def undo_translate():
                    self.canvas_item.setPos(initial_pos)
                    self.canvas_scene.update()
                    self.editor.statusBar().showMessage(f"Undo: Image translated to ({initial_pos.x()}, {initial_pos.y()})")
                    # Remove the translated layer
                    if translated_layer in self.layers:
                        self.layers.remove(translated_layer)
                        self.editor.update_layers_panel()
                def redo_translate():
                    self.canvas_item.setPos(final_pos)
                    self.canvas_scene.update()
                    self.editor.statusBar().showMessage(f"Redo: Image translated to ({final_pos.x()}, {final_pos.y()})")
                    # Add the translated layer back
                    if translated_layer not in self.layers:
                        self.layers.append(translated_layer)
                        self.editor.update_layers_panel()

                # Add the translation to the undo stack and clear redo stack
                self.editor.undo_stack.append({
                    'undo': undo_translate,
                    'redo': redo_translate
                })
                self.editor.redo_stack.clear()
                self.editor.update_thumbnail()  # Update thumbnail after translation

            elif event.button() == Qt.LeftButton and self.panning_active:
                self.dragging = False
                self.setCursor(Qt.OpenHandCursor)

        super().mouseReleaseEvent(event)
        self.editor.update_thumbnail()

    def render_text_onto_pixmap(self, text_item):
        # Capture the state of the pixmap before adding the text for undo
        original_pixmap_snapshot = QPixmap(self.canvas_pixmap)

        # Use a QPainter to draw the text onto the QPixmap
        painter = QPainter(self.canvas_pixmap)
        painter.setFont(text_item.font())
        painter.setPen(text_item.defaultTextColor())
        painter.drawText(text_item.pos(), text_item.toPlainText())
        painter.end()

        # Update the QGraphicsPixmapItem with the modified QPixmap
        self.canvas_item.setPixmap(self.canvas_pixmap)
        self.canvas_scene.update()

        # Capture the state of the pixmap after adding the text for redo
        final_pixmap_snapshot = QPixmap(self.canvas_pixmap)

        def undo_text():
            self.canvas_pixmap = QPixmap(original_pixmap_snapshot)
            self.canvas_item.setPixmap(self.canvas_pixmap)
            self.canvas_scene.update()

        def redo_text():
            self.canvas_pixmap = QPixmap(final_pixmap_snapshot)
            self.canvas_item.setPixmap(self.canvas_pixmap)
            self.canvas_scene.update()

        # Add the text addition to the undo stack and clear redo stack
        self.editor.undo_stack.append({
            'undo': undo_text,
            'redo': redo_text
        })
        self.editor.redo_stack.clear()
            
    def add_undo_redo_for_text(self, text_item, old_pos, new_pos):
        def undo_text():
            if old_pos is None:
                self.canvas_scene.removeItem(text_item)
            else:
                text_item.setPos(old_pos)

        def redo_text():
            if old_pos is None:
                self.canvas_scene.addItem(text_item)
            else:
                text_item.setPos(new_pos)

        self.editor.undo_stack.append({
            'undo': undo_text,
            'redo': redo_text
        })
        self.editor.redo_stack.clear()

    def show_translation_border(self):
        if self.canvas_pixmap:
            # Create a border rectangle item
            border_rect = QRectF(self.canvas_pixmap.rect())  # Convert QRect to QRectF
            pen = QPen(Qt.DashLine)
            pen.setColor(Qt.red)
            pen.setWidth(2)
            self.translation_border_item = self.canvas_scene.addRect(border_rect, pen)
            self.translation_border_item.setZValue(-1)  # Ensure the border is behind the image

    def hide_translation_border(self):
        if hasattr(self, 'translation_border_item') and self.translation_border_item:
            self.canvas_scene.removeItem(self.translation_border_item)
            self.translation_border_item = None

    def perform_crop(self, rect):
        cropped_pixmap = self.canvas_pixmap.copy(rect.toRect())
        cropped_item = QGraphicsPixmapItem(cropped_pixmap)
        cropped_item.setOffset(rect.topLeft())
        
        # Immediately hide the original and show the cropped item
        self.canvas_item.setVisible(False)
        self.canvas_scene.addItem(cropped_item)
        
        # Add the cropped image as a new layer
        cropped_layer = Layer("Cropped Layer", cropped_item)
        self.layers.append(cropped_layer)
        self.editor.update_layers_panel()
        self.editor.statusBar().showMessage("Cropped area added as a new layer")

        # Define undo and redo functions for crop action
        def undo_crop():
            # Remove cropped item and restore original
            self.canvas_scene.removeItem(cropped_item)
            self.layers.remove(cropped_layer)  # Remove from layers
            self.canvas_item.setVisible(True)  # Show the original item
            self.editor.update_layers_panel()

        def redo_crop():
            # Hide original and add cropped item back
            self.canvas_item.setVisible(False)
            self.canvas_scene.addItem(cropped_item)
            self.layers.append(cropped_layer)  # Re-add to layers
            self.editor.update_layers_panel()

        # Add the undo/redo actions
        self.editor.undo_stack.append({
            'undo': undo_crop,
            'redo': redo_crop
        })
        self.editor.redo_stack.clear()  # Clear the redo stack on a new action

    def toggle_layer_visibility(self, layer_name):
        for layer in self.layers:
            if layer.name == layer_name:
                if layer.pixmap_item is not None:
                    try:
                        layer.set_visible(not layer.visible)
                        self.canvas_scene.update()
                        self.editor.update_layers_panel()  # Ensure the panel is updated
                    except RuntimeError:
                        # Handle the case where the pixmap_item has been deleted
                        self.layers.remove(layer)
                        self.editor.update_layers_panel()
                else:
                    self.layers.remove(layer)  # Remove the layer if the pixmap_item is None
                    self.editor.update_layers_panel()
                break

    def rotate_image(self, angle):
        if self.canvas_pixmap:
            # Apply rotation to the pixmap
            transform = QTransform().rotate(angle)
            rotated_pixmap = self.canvas_pixmap.transformed(transform, Qt.SmoothTransformation)
            
            # Update canvas item with the rotated pixmap
            self.canvas_item.setPixmap(rotated_pixmap)
            self.canvas_pixmap = rotated_pixmap

            # Update scene boundary to fit the new pixmap size
            bounding_rect = QRectF(rotated_pixmap.rect())
            self.canvas_scene.setSceneRect(bounding_rect)

            # Update the existing boundary rectangle if it exists
            if self.boundary_rect_item:
                self.boundary_rect_item.setRect(bounding_rect)
            
            # Update the scene
            self.canvas_scene.update()
            self.editor.update_thumbnail()

    def change_pixel_color(self, x, y, color):
        if self.canvas_pixmap:
            image = self.canvas_pixmap.toImage()

            # Ensure the coordinates are within the image bounds
            if 0 <= x < image.width() and 0 <= y < image.height():
                # Capture the state of the pixmap before the change for undo
                original_pixmap_snapshot = QPixmap(self.canvas_pixmap)

                # Change the color of the specified pixel
                image.setPixelColor(x, y, QColor(color))
                self.canvas_pixmap = QPixmap.fromImage(image)

                # Update the canvas item to reflect the change
                self.canvas_item.setPixmap(self.canvas_pixmap)
                self.canvas_scene.update()  # Force scene update
                self.editor.statusBar().showMessage(f"Pixel at ({x}, {y}) changed to {color}")

                # Define undo/redo functions with unique snapshots
                final_pixmap_snapshot = QPixmap(self.canvas_pixmap)

                def undo_change():
                    self.canvas_pixmap = QPixmap(original_pixmap_snapshot)
                    self.canvas_item.setPixmap(self.canvas_pixmap)
                    self.canvas_scene.update()

                def redo_change():
                    self.canvas_pixmap = QPixmap(final_pixmap_snapshot)
                    self.canvas_item.setPixmap(self.canvas_pixmap)
                    self.canvas_scene.update()

                # Add the change to the undo stack and clear redo stack
                self.editor.undo_stack.append({
                    'undo': undo_change,
                    'redo': redo_change
                })
                self.editor.redo_stack.clear()
                self.editor.update_thumbnail()

    def change_group_of_pixels_color(self, x, y, new_color):
        if not self.canvas_pixmap:
            return

        image = self.canvas_pixmap.toImage()
        width, height = image.width(), image.height()

        # Ensure the starting point is within bounds
        if not (0 <= x < width and 0 <= y < height):
            return

        target_color = image.pixelColor(x, y)
        new_color = QColor(new_color)

        # If the target color is the same as the new color, return early
        if target_color == new_color:
            return

        # Capture the state of the pixmap before the change for undo
        original_pixmap_snapshot = QPixmap(self.canvas_pixmap)

        queue = [(x, y)]
        visited = set(queue)

        while queue:
            cx, cy = queue.pop(0)
            if 0 <= cx < width and 0 <= cy < height and image.pixelColor(cx, cy) == target_color:
                # Change the color of the current pixel
                image.setPixelColor(cx, cy, new_color)

                # Add neighboring pixels to the queue
                neighbors = [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
                for nx, ny in neighbors:
                    if (nx, ny) not in visited and 0 <= nx < width and 0 <= ny < height:
                        visited.add((nx, ny))
                        queue.append((nx, ny))

        # Update the pixmap and refresh the scene
        self.canvas_pixmap = QPixmap.fromImage(image)
        self.canvas_item.setPixmap(self.canvas_pixmap)
        self.canvas_scene.update()
        self.editor.statusBar().showMessage(f"Group of pixels starting from ({x}, {y}) changed to {new_color.name()}")

        # Define undo/redo functions with unique snapshots
        final_pixmap_snapshot = QPixmap(self.canvas_pixmap)

        def undo_change():
            self.canvas_pixmap = QPixmap(original_pixmap_snapshot)
            self.canvas_item.setPixmap(self.canvas_pixmap)
            self.canvas_scene.update()

        def redo_change():
            self.canvas_pixmap = QPixmap(final_pixmap_snapshot)
            self.canvas_item.setPixmap(self.canvas_pixmap)
            self.canvas_scene.update()

        # Add the change to the undo stack and clear redo stack
        self.editor.undo_stack.append({
            'undo': undo_change,
            'redo': redo_change
        })
        self.editor.redo_stack.clear()
        self.editor.update_thumbnail()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = PhotoEditor(create_tabs=False)
    editor.show()
    sys.exit(app.exec_())
