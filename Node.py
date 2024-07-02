# Node.py

from PySide6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem
from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QPainterPath
from Edge import Edge
from ConditionEdge import ConditionEdge  # Import ConditionEdge
from NodeData import NodeData
from NodeLayout import NodeLayout


class Node(QGraphicsItem):
    def __init__(self, node_data: NodeData):
        super().__init__()
        self.data = node_data
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.rect = QRectF(0, 0, self.data.width, self.data.height)
        self.resizeHandleSize = 10
        self.resizing = False
        self.resizeDirection = None
        self.content = NodeLayout(self)
        self.input_port = Port(self, QPointF(0, 25), "input")
        self.output_port = Port(self, QPointF(self.rect.width(), 25), "output")
        
        # Add true and false ports for condition nodes
        self.true_port = Port(self, QPointF(self.rect.width() / 2, 0), "true")
        self.true_port.setBrush(QBrush(Qt.green))
        self.false_port = Port(self, QPointF(self.rect.width() / 2, self.rect.height()), "false")
        self.false_port.setBrush(QBrush(Qt.red))

        self.setPos(self.data.pos_x, self.data.pos_y)
        self.setAcceptHoverEvents(True)
        self.hovered = False
        self.update_ports_visibility()

    def update_ports_visibility(self):
        if self.data.type == "CONDITION":
            self.true_port.setVisible(True)
            self.false_port.setVisible(True)
            self.output_port.setVisible(False)
        else:
            self.true_port.setVisible(False)
            self.false_port.setVisible(False)
            self.output_port.setVisible(True)

    def setWidth(self, width):
        self.rect.setWidth(width)
        self.output_port.setPos(width, 25)
        self.true_port.setPos(width / 2, 0)
        self.prepareGeometryChange()
        self.content.update_proxy_widget_geometry()
        self.data.width = width

    def setHeight(self, height):
        self.rect.setHeight(height)
        self.false_port.setPos(self.rect.width() / 2, height)
        self.prepareGeometryChange()
        self.content.update_proxy_widget_geometry()
        self.data.height = height

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        pen = QPen(Qt.black, 2)
        if self.hovered:
            pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.drawRect(self.rect)
        self.content.paint(painter, option, widget)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for port in [self.input_port, self.output_port, self.true_port, self.false_port]:
                for edge in port.edges:
                    edge.update_position()
            self.data.pos_x = value.x()
            self.data.pos_y = value.y()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        pos = event.pos()
        if pos.x() >= self.rect.right() - self.resizeHandleSize and \
                pos.y() >= self.rect.bottom() - self.resizeHandleSize:
            self.resizing = True
            self.resizeDirection = "bottom_right"
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.resizing = False
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            delta = event.pos() - event.lastPos()
            if self.resizeDirection == "bottom_right":
                self.setWidth(self.rect.width() + delta.x())
                self.setHeight(self.rect.height() + delta.y())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.resizing:
            self.resizing = False
            self.setCursor(Qt.ArrowCursor)
        else:
            super().mouseReleaseEvent(event)

    def remove_node(self):
        for edge in self.input_port.edges[:]:
            edge.remove()
        for edge in self.output_port.edges[:]:
            edge.remove()
        for edge in self.true_port.edges[:]:
            edge.remove()
        for edge in self.false_port.edges[:]:
            edge.remove()

        for prev_id in self.data.prevs:
            prev_node = self.scene().get_node_by_id(prev_id)
            if prev_node:
                prev_node.data.nexts.remove(self.data.uniq_id)

        for next_id in self.data.nexts:
            next_node = self.scene().get_node_by_id(next_id)
            if next_node:
                next_node.data.prevs.remove(self.data.uniq_id)

        self.scene().removeItem(self)

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)


class Port(QGraphicsEllipseItem):
    def __init__(self, parent, position, port_type):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setPos(position)
        self.port_type = port_type
        self.edges = []
        self.setRect(self.boundingRect())

    def boundingRect(self):
        return QRectF(-5, -5, 10, 10)

    def paint(self, painter, option, widget):
        painter.setPen(Qt.NoPen)
        if self.port_type == "true":
            painter.setBrush(Qt.green)
        elif self.port_type == "false":
            painter.setBrush(Qt.red)
        else:
            painter.setBrush(Qt.black)

        path = QPainterPath()
        path.moveTo(-5, -5)
        path.lineTo(5, 0)
        path.lineTo(-5, 5)
        path.closeSubpath()

        painter.drawPath(path)

    def mousePressEvent(self, event):
        if self.port_type == "output":
            self.create_edge(event)
        elif self.port_type in ["true", "false"]:
            self.create_condition_edge(event)

    def create_edge(self, event):
        edge = Edge(self)
        self.edges.append(edge)
        self.scene().addItem(edge)

    def create_condition_edge(self, event):
        condition_edge = ConditionEdge(self, self.port_type)
        self.edges.append(condition_edge)
        self.scene().addItem(condition_edge)

    def mouseMoveEvent(self, event):
        if self.edges:
            self.edges[-1].update_position(event.scenePos())

    def mouseReleaseEvent(self, event):
        if self.edges:
            items = self.scene().items(event.scenePos())
            for item in items:
                if isinstance(item, Port) and item != self:
                    if self.port_type == "output" and item.port_type == "input":
                        self.edges[-1].set_destination(item)
                        item.edges.append(self.edges[-1])
                        break
                    elif self.port_type in ["true", "false"] and item.port_type == "input":
                        source_node = self.parentItem().data
                        if (self.port_type == "true" and source_node.true_next is None) or \
                           (self.port_type == "false" and source_node.false_next is None):
                            self.edges[-1].set_destination(item)
                            item.edges.append(self.edges[-1])
                            break
            else:
                self.scene().removeItem(self.edges[-1])
                self.edges.pop()
