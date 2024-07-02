# MainWindow.py

from PySide6.QtWidgets import QMainWindow, QGraphicsScene, QGraphicsView, QMenu, QFileDialog, QDockWidget
from PySide6.QtGui import QAction, QPixmap, QPainter
from PySide6.QtCore import Qt, QTimer, QPointF
from MapView import MapView
import file_operations
from CustomGraphicsView import CustomGraphicsView
from ExecCommandDialog import ExecCommandDialog  # Import the new dialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = CustomGraphicsScene()
        self.view = CustomGraphicsView(self.scene, self)  # Pass MainWindow reference to CustomGraphicsView
        self.setCentralWidget(self.view)
        self.create_dock_widgets()
        self.create_actions_and_menus()

    def create_actions_and_menus(self):
        actions = {
            "File": {
                "New": self.new,
                "Save": self.save,
                "Load": self.load,
            },
            "Tools": {
                "Map View": self.toggle_map_view,
                "Exec Command": self.exec_command,
            }
        }

        self.menu_bar = self.menuBar()
        self.actions = {}

        for menu_name, actions_dict in actions.items():
            menu = self.menu_bar.addMenu(menu_name)
            for action_name, method in actions_dict.items():
                action = QAction(action_name, self)
                action.triggered.connect(method)
                self.actions[action_name.lower().replace(" ", "_") + "_action"] = action
                menu.addAction(action)

    def create_dock_widgets(self):
        self.map_view = MapView()
        self.dock_widget = QDockWidget("Map View", self)
        self.dock_widget.setWidget(self.map_view)
        self.dock_widget.setFloating(True)
        
        # Move the dock widget to the bottom-left corner of the screen
        screen_geometry = self.screen().geometry()
        screen_height = screen_geometry.height()
        self.dock_widget.move(0, screen_height - 200)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_widget)

    def new(self):
        self.scene.clear()  # Clears all items from the scene
        self.scene.node_counter = 1  # Reset the node counter
        self.view.update_map_view()  # Refresh the view

    def save(self):
        file_operations.save(self.scene)

    def load(self):
        self.new()
        file_operations.load(self.scene)
        self.view.update_map_view()  # Refresh the view after loading

    def exec_command(self):
        self.exec_command_dialog = ExecCommandDialog(self)
        self.exec_command_dialog.show()

    def toggle_map_view(self):
        is_visible = self.dock_widget.isVisible()
        self.dock_widget.setVisible(not is_visible)

class CustomGraphicsScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.node_counter = 1  # Initialize the counter
        self.nodes_by_id = {}  # Dictionary to store nodes by their unique IDs

    def add_node(self, node):
        self.addItem(node)
        self.nodes_by_id[node.data.uniq_id] = node
        self.node_counter += 1

    def remove_node(self, node):
        if node.data.uniq_id in self.nodes_by_id:
            del self.nodes_by_id[node.data.uniq_id]
        self.removeItem(node)

    def get_node_by_id(self, node_id):
        return self.nodes_by_id.get(node_id)

    def clear(self):
        super().clear()
        self.nodes_by_id.clear()
        self.node_counter = 1
