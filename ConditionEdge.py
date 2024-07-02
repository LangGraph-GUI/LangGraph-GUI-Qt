# ConditionEdge.py

from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QPainterPath

class ConditionEdge(QGraphicsPathItem):
    def __init__(self, source_port, condition_type):
        super().__init__()
        self.source_port = source_port
        self.source_id = source_port.parentItem().data.uniq_id
        self.condition_type = condition_type
        self.setPen(QPen(Qt.green if condition_type == "true" else Qt.red, 2))
        self.setZValue(-1)
        self.destination_port = None
        self.destination_id = None
        self.update_position()

    def update_position(self, end_point=None):
        path = QPainterPath()
        start_point = self.source_port.scenePos()
        if end_point:
            control_point_1 = QPointF(start_point.x() + 50, start_point.y())
            control_point_2 = QPointF(end_point.x() - 50, end_point.y())
            path.moveTo(start_point)
            path.cubicTo(control_point_1, control_point_2, end_point)
        elif self.destination_port:
            end_point = self.destination_port.scenePos()
            control_point_1 = QPointF(start_point.x() + 50, start_point.y())
            control_point_2 = QPointF(end_point.x() - 50, end_point.y())
            path.moveTo(start_point)
            path.cubicTo(control_point_1, control_point_2, end_point)
        else:
            path.moveTo(start_point)
            path.cubicTo(start_point, start_point, start_point)
        self.setPath(path)

    def set_destination(self, destination_port):
        self.destination_port = destination_port
        self.destination_id = destination_port.parentItem().data.uniq_id
        self.update_position()
        source_node = self.source_port.parentItem().data
        dest_node = self.destination_port.parentItem().data
        
        if self.condition_type == "true":
            source_node.true_next = self.destination_id
        else:
            source_node.false_next = self.destination_id
        dest_node.prevs.append(self.source_id)

    def remove(self):
        if self in self.source_port.edges:
            self.source_port.edges.remove(self)
        if self in self.destination_port.edges:
            self.destination_port.edges.remove(self)
        source_node = self.source_port.parentItem().data
        dest_node = self.destination_port.parentItem().data
        if self.condition_type == "true":
            if self.destination_id == source_node.true_next:
                source_node.true_next = None
        else:
            if self.destination_id == source_node.false_next:
                source_node.false_next = None
        if self.source_id in dest_node.prevs:
            dest_node.prevs.remove(self.source_id)
        self.scene().removeItem(self)
