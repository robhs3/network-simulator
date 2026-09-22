import sys

from PyQt6.QtCore import QLineF, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QBrush, QColor, QKeySequence, QPen, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFormLayout,
    QFrame,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


class CableItem(QGraphicsLineItem):
    def __init__(self, node1, node2):
        super().__init__()

        self.setZValue(-1)

        self.node1 = node1
        self.node2 = node2

        node1.cables.append(self)
        node2.cables.append(self)

        self.update_position()

    def update_position(self):
        point1 = self.node1.mapToScene(self.node1.rect().center())
        point2 = self.node2.mapToScene(self.node2.rect().center())

        self.setLine(QLineF(point1, point2))

    def disconnect(self):
        self.node1.cables.remove(self)
        self.node2.cables.remove(self)


class NetworkNodeItem(QGraphicsRectItem):
    def __init__(self, node_type, name):
        super().__init__(0, 0, 100, 60)

        self.node_type = node_type
        self.name = name
        self.cables = []

        self.setBrush(QBrush(QColor("grey")))
        self.setPen(QPen(QColor("black"), 2))

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.label = QGraphicsTextItem(name, self)

        label_rect = self.label.boundingRect()
        node_rect = self.rect()

        self.label.setPos(
            (node_rect.width() - label_rect.width()) / 2,
            (node_rect.height() - label_rect.height()) / 2,
        )

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for cable in self.cables:
                cable.update_position()

        return super().itemChange(change, value)

    def set_name(self, name):
        self.name = name
        self.label.setPlainText(name)

        label_rect = self.label.boundingRect()
        node_rect = self.rect()

        self.label.setPos(
            (node_rect.width() - label_rect.width()) / 2,
            (node_rect.height() - label_rect.height()) / 2,
        )


class NetworkScene(QGraphicsScene):
    empty_space_clicked = pyqtSignal(float, float)
    node_deleted = pyqtSignal(object)
    node_clicked = pyqtSignal(object)

    def mousePressEvent(self, event):
        position = event.scenePos()

        item = self.itemAt(position, self.views()[0].transform())

        if item is None:
            self.empty_space_clicked.emit(position.x(), position.y())

        elif isinstance(item, NetworkNodeItem):
            self.node_clicked.emit(item)

        elif isinstance(item.parentItem(), NetworkNodeItem):
            self.node_clicked.emit(item.parentItem())

        super().mousePressEvent(event)

    def delete_selected_items(self):
        for item in self.selectedItems():
            if isinstance(item, NetworkNodeItem):
                for cable in item.cables.copy():
                    cable.disconnect()
                    self.removeItem(cable)
                self.node_deleted.emit(item)

            self.removeItem(item)


class NetworkView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self._panning = False
        self._pan_start = None

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            zoom_factor = 1.15
        else:
            zoom_factor = 1 / 1.15

        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.position()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x())
            )

            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y())
            )

            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self._pan_start = None
            return

        super().mouseReleaseEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.selected_tool = None

        self.connection_mode = False
        self.connection_start = None

        escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape_shortcut.activated.connect(self.cancel_action)

        self.nodes = []

        self.setWindowTitle("Network Simulator")
        self.resize(1000, 700)

        layout = QHBoxLayout()

        self.label = QLabel("Nothing selected")

        self.selection_label = QLabel("No node selected")

        host_button = QPushButton("Host")
        switch_button = QPushButton("Switch")
        connect_button = QPushButton("Connect")

        host_button.setCheckable(True)
        switch_button.setCheckable(True)

        self.tool_button_group = QButtonGroup(self)

        self.tool_button_group.addButton(host_button)
        self.tool_button_group.addButton(switch_button)

        self.tool_button_group.setExclusive(True)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Node name")
        self.name_input.setEnabled(False)
        self.name_input.editingFinished.connect(self.name_edit_finished)

        self.type_label = QLineEdit("-")

        sidebar = QWidget()
        sidebar.setMinimumWidth(150)
        sidebar_layout = QVBoxLayout()

        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout()

        tools_layout.addWidget(host_button)
        tools_layout.addWidget(switch_button)
        tools_layout.addWidget(connect_button)

        tools_group.setLayout(tools_layout)

        properties_group = QGroupBox("Properties")
        properties_layout = QFormLayout()

        properties_layout.addRow("Type:", self.type_label)
        properties_layout.addRow("Name:", self.name_input)

        properties_group.setLayout(properties_layout)

        sidebar_layout.addWidget(self.label)
        sidebar_layout.addWidget(tools_group)
        sidebar_layout.addWidget(self.selection_label)
        sidebar_layout.addWidget(properties_group)
        sidebar_layout.addStretch()

        sidebar.setLayout(sidebar_layout)

        workspace = QFrame()
        workspace.setFrameShape(QFrame.Shape.Box)
        workspace_layout = QVBoxLayout()

        self.scene = NetworkScene()
        self.scene.setSceneRect(-1000, -600, 2000, 1200)

        self.scene.empty_space_clicked.connect(self.place_selected_tool)
        self.scene.selectionChanged.connect(self.selection_changed)
        self.scene.node_deleted.connect(self.node_deleted)
        self.scene.node_clicked.connect(self.node_clicked)

        view = NetworkView(self.scene)
        workspace_layout.addWidget(view)

        workspace.setLayout(workspace_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        splitter.addWidget(sidebar)
        splitter.addWidget(workspace)

        splitter.setCollapsible(0, False)

        splitter.setSizes([180, 820])

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        host_button.clicked.connect(lambda: self.select_tool("Host"))
        switch_button.clicked.connect(lambda: self.select_tool("Switch"))
        connect_button.clicked.connect(self.start_connection)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))

        self.delete_action = QAction("Delete", self)
        self.delete_action.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        self.delete_action.setEnabled(False)
        self.delete_action.triggered.connect(self.scene.delete_selected_items)

        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(exit_action)

        edit_menu = self.menuBar().addMenu("Edit")
        edit_menu.addAction(self.delete_action)

        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        toolbar.addAction(self.delete_action)
        toolbar.addSeparator()
        toolbar.addAction(exit_action)

        self.statusBar().showMessage("Ready")

    def select_tool(self, tool):
        self.selected_tool = tool
        self.label.setText(f"Selected: {self.selected_tool}")

        self.statusBar().showMessage(f"Click the workspace to place a {tool}")

    def place_selected_tool(self, x, y):
        if self.selected_tool is None:
            return

        self.add_node(self.selected_tool, x, y)

        self.selected_tool = None
        self.label.setText("Nothing selected")

        self.tool_button_group.setExclusive(False)

        for button in self.tool_button_group.buttons():
            button.setChecked(False)

        self.tool_button_group.setExclusive(True)

        self.statusBar().showMessage("Ready")

    def add_node(self, node_type, x, y):
        node = NetworkNodeItem(node_type, node_type)
        node_rect = node.rect()
        node.setPos(x - node_rect.width() / 2, y - node_rect.height() / 2)
        self.scene.addItem(node)
        self.nodes.append(node)

    def selection_changed(self):
        selected_items = self.scene.selectedItems()

        self.delete_action.setEnabled(len(selected_items) > 0)

        if len(selected_items) == 1:
            selected_node = selected_items[0]

            self.selection_label.setText(f"Selected node: {selected_node.name}")

            self.type_label.setText(selected_node.node_type)

            self.name_input.setText(selected_node.name)

            self.name_input.setEnabled(True)

        elif len(selected_items) > 1:
            self.selection_label.setText(f"{len(selected_items)} nodes selected")

            self.type_label.setText("-")
            self.name_input.clear()
            self.name_input.setEnabled(False)

        else:
            self.selection_label.setText("No node selected")

            self.type_label.setText("-")
            self.name_input.clear()
            self.name_input.setEnabled(False)

    def node_deleted(self, node):
        self.nodes.remove(node)

    def node_clicked(self, node):
        if not self.connection_mode:
            return

        if self.connection_start is None:
            self.connection_start = node
            self.label.setText(f"Connect from: {node.name}")
            return

        if node is self.connection_start:
            return

        cable = CableItem(self.connection_start, node)
        self.scene.addItem(cable)

        self.connection_mode = False
        self.connection_start = None
        self.label.setText("Nothing selected")

    def start_connection(self):
        self.connection_mode = True
        self.connection_start = None
        self.selected_tool = None
        self.label.setText("Connection mode")

    def cancel_action(self):
        self.selected_tool = None
        self.connection_mode = False
        self.connection_start = None

        self.label.setText("Nothing selected")

        self.tool_button_group.setExclusive(False)

        for button in self.tool_button_group.buttons():
            button.setChecked(False)

        self.tool_button_group.setExclusive(True)

        self.statusBar().showMessage("Ready")

    def name_edit_finished(self):
        selected_items = self.scene.selectedItems()

        if len(selected_items) != 1:
            return

        selected_node = selected_items[0]

        new_name = self.name_input.text()

        selected_node.set_name(new_name)

        self.selection_label.setText(f"Selected node: {new_name}")


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
