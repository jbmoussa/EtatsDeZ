import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame, QLabel, QHBoxLayout, QPushButton, QLineEdit
from PyQt5.QtGui import QPainter, QPen, QDoubleValidator
from PyQt5.QtCore import Qt, QEvent, pyqtSignal


class RulerWidget(QWidget):

    value_changed = pyqtSignal()

    def __init__(self, min_value=0, max_value=100, tick_length=10, line_thickness=2,
                 zero_offset=None, unit_length=None):
        super().__init__()
        if zero_offset is None:
            self.min_value = min_value
            self.max_value = max_value
            self.unit_length = (self.width() - 40) / (self.max_value - self.min_value)
            self.zero_offset = 20 - self.min_value * self.unit_length
        else:
            self.zero_offset = zero_offset
            self.unit_length = unit_length
            self.min_value = (20 - self.zero_offset) / self.unit_length
            self.max_value = (self.width() - 20 - self.zero_offset) / self.unit_length
        self.max_integer = min_value
        self.min_integer = max_value
        self.tick_interval = 1
        self.tick_length = tick_length
        self.line_thickness = line_thickness
        self.setMinimumHeight(50)  # Set a minimum height for the ruler widget
        self.y_ruler = 0
        self.show_ruler = True
        self.show_labels = False
        self.special_number = None
        self.is_dragging = False
        self.start_drag_x = 1
        self.start_drag_unit_length = 1

    def paintEvent(self, event):
        self.update_zero_offset_system()
        self.update_min_max_integer()
        self.value_changed.emit()

        if not self.show_ruler:
            return
        self.y_ruler = self.rect().height()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the horizontal line
        pen = QPen(Qt.black, self.line_thickness)
        painter.setPen(pen)
        painter.drawLine(20, self.y_ruler, self.width() - 20, self.y_ruler)  # Horizontal line with padding on both ends

        if self.show_labels:
            self.update_tick_interval(painter)
        else:
            self.tick_interval = 1

        # Draw the vertical ticks
        for i in range(self.min_integer + ((-self.min_integer) % self.tick_interval),
                       self.max_integer + 1, self.tick_interval):
            x = (20 + (self.width() - 40) * (i - self.min_value)
                 / (self.max_value - self.min_value)) # calculate the x position of the tick
            painter.drawLine(int(x), self.y_ruler, int(x),
                             self.y_ruler - self.tick_length)  # Draw the tick (small vertical line)

            # Draw the label above the tick
            if self.show_labels:
                label = self.integer_label(i)
                label_x = int(x) - painter.fontMetrics().width(label) // 2  # Center the label
                label_y = self.y_ruler - self.tick_length - 10  # Position the label above the tick
                painter.drawText(label_x, label_y, label)

        if self.special_number is not None:
            if self.min_value <= self.special_number <= self.max_value:
                pen = QPen(Qt.red, self.line_thickness)
                painter.setPen(pen)
                x = (20 + (self.width() - 40) * (self.special_number - self.min_value)
                     / (self.max_value - self.min_value))
                painter.drawLine(int(x), self.y_ruler, int(x),
                                 self.y_ruler - self.tick_length)

    def update_min_max_integer(self):
        if self.min_value < self.max_value:
            if self.min_value <= 0:
                self.min_integer = int(self.min_value)
            else:
                self.min_integer = int(self.min_value) + 1
            if self.max_value <= 0:
                self.max_integer = int(self.max_value) - 1
            else:
                self.max_integer = int(self.max_value)
        else:
            if self.min_value <= 0:
                self.min_integer = int(self.min_value) - 1
            else:
                self.min_integer = int(self.min_value)
            if self.max_value <= 0:
                self.max_integer = int(self.max_value) - 2
            else:
                self.max_integer = int(self.max_value) - 1

    def print(self):
        print('Properties of the ruler :')
        print(f'Zero offset: {self.zero_offset}')
        print(f'Unit length: {self.unit_length}')
        print(f'Min value: {self.min_value}')
        print(f'Max value: {self.max_value}')

    def mousePressEvent(self, event):
        # Catch right-click events in the RulerWidget
        if event.button() == Qt.RightButton:
            if event.type() == QEvent.MouseButtonPress:
                if abs(event.x() - self.zero_offset) > 30:
                    # Start dragging
                    self.is_dragging = True
                    self.start_drag_x = event.x() - self.zero_offset  # Record the X position where dragging starts
                    self.start_drag_unit_length = self.unit_length
        # If left-clicked, ignore so it can propagate to DoubleRulerWidget
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            if abs(event.x() - self.zero_offset) > 20:
                # Calculate the difference in X position during dragging
                delta_x = (event.x() - self.zero_offset) / self.start_drag_x

                # Update the zero_offset based on mouse movement
                self.unit_length = self.start_drag_unit_length * delta_x
                self.update_min_max_system()
                # Trigger a repaint to update the ruler display
                self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Catch right-click events in the RulerWidget
        if event.button() == Qt.RightButton:
            if event.type() == QEvent.MouseButtonRelease:
                # Stop dragging
                self.is_dragging = False
        # If left-clicked, ignore so it can propagate to DoubleRulerWidget
        else:
            super().mouseReleaseEvent(event)

    def update_zero_offset_system(self):
        self.unit_length = (self.width() - 40) / (self.max_value - self.min_value)
        self.zero_offset = 20 - self.min_value * self.unit_length

    def update_min_max_system(self):
        self.min_value = (20 - self.zero_offset) / self.unit_length
        self.max_value = (self.width() - 20 - self.zero_offset) / self.unit_length

    def update_tick_interval(self, painter):
        interval_marker = False
        if self.min_value <= self.max_value:
            self.tick_interval = 1
        else:
            self.tick_interval = -1
        while not interval_marker:
            interval_marker = True
            nb_graduations = (self.max_integer - self.min_integer) // self.tick_interval + 1
            place_per_graduation = self.width() // nb_graduations - 5
            for i in range(self.min_integer + ((-self.min_integer) % self.tick_interval),
                           self.max_integer + 1, self.tick_interval):
                if painter.fontMetrics().width(str(i)) > place_per_graduation:
                    interval_marker = False
            if not interval_marker:
                if self.tick_interval == 1 or self.tick_interval == -1 or self.tick_interval % 10 == 0:
                    self.tick_interval *= 5
                else:
                    self.tick_interval *= 2

    def showSpecialNumber(self, number):
        self.special_number = float(number)
        self.update()

    def onEraseSpecialNumber(self):
        self.special_number = None
        self.update()

    def integer_label(self, i):
        if i > 0:
            return '+' + str(i)
        else:
            return str(i)

class BottomRuler(RulerWidget):

    value_changed = pyqtSignal()

    def __init__(self, main_ruler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_ruler = main_ruler
        self.homothetie = 1

        self.setMinimumHeight(70)
        self.copy_parent()
        self.main_ruler.value_changed.connect(self.update)

    def paintEvent(self, event):
        self.copy_parent()
        self.update_min_max_integer()
        self.value_changed.emit()
        if not self.show_ruler:
            return
        self.y_ruler = 0

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the horizontal line
        pen = QPen(Qt.darkBlue, self.line_thickness)
        painter.setPen(pen)

        if self.show_labels:
            self.update_tick_interval(painter)
        else:
            self.tick_interval = 1

        # Draw the vertical ticks
        for i in range(self.min_integer + ((-self.min_integer) % self.tick_interval),
                       self.max_integer + 1, self.tick_interval):
            x = (20 + (self.width() - 40) * (i - self.min_value)
                 / (self.max_value - self.min_value)) # calculate the x position of the tick

            painter.drawLine(int(x), self.y_ruler, int(x),
                             self.y_ruler + self.tick_length)  # Draw the tick (small vertical line)
            painter.drawLine(int(x), self.y_ruler, int(x) - self.tick_length // 3,
                             self.y_ruler + self.tick_length // 3)
            painter.drawLine(int(x), self.y_ruler, int(x) + self.tick_length // 3,
                             self.y_ruler + self.tick_length // 3)

            if self.show_labels:
                if abs(self.homothetie - round(self.homothetie)) < 0.02:
                    label_product = self.prod_label(i)
                    label_x = int(x) - painter.fontMetrics().width(label_product) // 2  # Center the label
                    label_y = self.y_ruler + self.tick_length + 10 + painter.fontMetrics().height() // 2  # Position the label above the tick
                    painter.drawText(label_x, label_y, label_product)

                    label = self.integer_label(i)
                    label_x = int(x) - painter.fontMetrics().width(label) // 2  # Center the label
                    label_y = self.y_ruler + self.tick_length + 20 + 3 * painter.fontMetrics().height() // 2  # Position the label above the tick
                    painter.drawText(label_x, label_y, label)

                else:
                    label = self.integer_label(i)
                    label_x = int(x) - painter.fontMetrics().width(label) // 2  # Center the label
                    label_y = self.y_ruler + self.tick_length + 10 + painter.fontMetrics().height() // 2  # Position the label above the tick
                    painter.drawText(label_x, label_y, label)

    def copy_parent(self):
        self.zero_offset = self.main_ruler.zero_offset
        self.unit_length = self.main_ruler.unit_length * self.homothetie
        self.update_min_max_system()

    def update_tick_interval(self, painter):
        interval_marker = False
        if self.min_value <= self.max_value:
            self.tick_interval = 1
        else:
            self.tick_interval = -1

        if abs(self.homothetie - round(self.homothetie)) >= 0.02:
            while not interval_marker:
                interval_marker = True
                nb_graduations = (self.max_integer - self.min_integer) // self.tick_interval + 1
                place_per_graduation = self.width() // nb_graduations - 5
                for i in range(self.min_integer + ((-self.min_integer) % self.tick_interval),
                               self.max_integer + 1, self.tick_interval):
                    if painter.fontMetrics().width(str(i)) > place_per_graduation:
                        interval_marker = False
                if not interval_marker:
                    if self.tick_interval == 1 or self.tick_interval == -1 or self.tick_interval % 10 == 0:
                        self.tick_interval *= 5
                    else:
                        self.tick_interval *= 2

        else:
            while not interval_marker:
                interval_marker = True
                nb_graduations = (self.max_integer - self.min_integer) // self.tick_interval + 1
                place_per_graduation = self.width() // nb_graduations - 5
                for i in range(self.min_integer + ((-self.min_integer) % self.tick_interval),
                               self.max_integer + 1, self.tick_interval):
                    if painter.fontMetrics().width(self.prod_label(i)) > place_per_graduation:
                        interval_marker = False
                if not interval_marker:
                    if self.tick_interval == 1 or self.tick_interval == -1 or self.tick_interval % 10 == 0:
                        self.tick_interval *= 5
                    else:
                        self.tick_interval *= 2

    def mousePressEvent(self, event):
        # Catch right-click events in the RulerWidget
        if event.button() == Qt.RightButton:
            if event.type() == QEvent.MouseButtonPress:
                if abs(event.x() - self.zero_offset) > 20:
                    # Start dragging
                    self.is_dragging = True
                    self.start_drag_x = event.x() - self.zero_offset  # Record the X position where dragging starts
                    self.start_drag_unit_length = self.homothetie    # We replace unit length by homothetie
        # If left-clicked, ignore so it can propagate to DoubleRulerWidget
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging and self.show_ruler:
            if abs(event.x() - self.zero_offset) > 20 and abs(self.homothetie) > 0.1:
                # Calculate the difference in X position during dragging
                delta_x = (event.x() - self.zero_offset) / self.start_drag_x

                # Update the zero_offset based on mouse movement
                self.homothetie = delta_x * self.start_drag_unit_length
                if round(self.homothetie) != 0 and 0.97 < (self.homothetie / round(self.homothetie)) < 1.03:
                    self.homothetie = round(self.homothetie)
                self.unit_length = self.main_ruler.unit_length * self.homothetie
                self.update_min_max_system()
                # Trigger a repaint to update the ruler display
                self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Catch right-click events in the RulerWidget
        if event.button() == Qt.RightButton:
            if event.type() == QEvent.MouseButtonRelease:
                # Stop dragging
                self.is_dragging = False
        # If left-clicked, ignore so it can propagate to DoubleRulerWidget
        else:
            super().mouseReleaseEvent(event)

    def prod_label(self, i):
        if i > 0:
            return f'(+{i})x{self.homothetie:.0f}'
        if i == 0:
            return f'{i}x{self.homothetie:.0f}'
        else:
            return f'({i})x{self.homothetie:.0f}'


class DoubleRulerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.main_ruler = None
        self.low_ruler = None
        self.start_drag_x = None
        self.is_dragging = None
        self.start_drag_zero_offset = None
        self.show_labels = False
        self.initUI()

    def initUI(self):
        self.main_ruler = RulerWidget(min_value=-10, max_value=10)
        self.low_ruler = BottomRuler(main_ruler=self.main_ruler, tick_length=20)
        self.low_ruler.show_ruler = False

        layout = QVBoxLayout()
        layout.addWidget(self.main_ruler)
        layout.addWidget(self.low_ruler)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                # Start dragging
                self.is_dragging = True
                self.start_drag_x = event.x()  # Record the X position where dragging starts
                self.start_drag_zero_offset = self.main_ruler.zero_offset

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            # Calculate the difference in X position during dragging
            delta_x = event.x() - self.start_drag_x

            # Update the zero_offset based on mouse movement
            self.main_ruler.zero_offset = self.start_drag_zero_offset + delta_x
            self.main_ruler.update_min_max_system()
            self.low_ruler.zero_offset = self.main_ruler.zero_offset
            self.low_ruler.update_min_max_system()
            # Trigger a repaint to update the ruler display
            self.update()

    def mouseReleaseEvent(self, event):
        if event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                # Stop dragging
                self.is_dragging = False

    def onShowRulerButton(self):
        if self.low_ruler.show_ruler:
            self.low_ruler.show_ruler = False
        else:
            self.low_ruler.show_ruler = True
        self.update()

    def onShowIntegerButton(self):
        if self.show_labels:
            self.main_ruler.show_labels = False
            self.low_ruler.show_labels = False
            self.show_labels = False
        else:
            self.main_ruler.show_labels = True
            self.low_ruler.show_labels = True
            self.show_labels = True
        self.update()

    def set_homothetie(self, homothetie):
        self.low_ruler.homothetie = homothetie
        self.low_ruler.update_min_max_system()
        self.update()


class RulerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.homothetie_current_label = None
        self.doubleRuler = None
        self.special_number_input = None
        self.homothetie_input = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.doubleRuler = DoubleRulerWidget()

        show_integer_layout = QHBoxLayout()
        show_integer_button_up = QPushButton('Montrer graduation', self)
        show_integer_button_up.clicked.connect(self.doubleRuler.onShowIntegerButton)
        show_integer_button_down = QPushButton('Montrer homothétie', self)
        show_integer_button_down.clicked.connect(self.doubleRuler.onShowRulerButton)
        show_integer_layout.addWidget(show_integer_button_up)
        show_integer_layout.addWidget(show_integer_button_down)

        special_number_layout = QHBoxLayout()
        special_number_label = QLabel("Entrer un nombre à faire apparaître sur l'échelle: ", self)
        self.special_number_input = QLineEdit()
        self.special_number_input.setValidator(QDoubleValidator())
        special_number_show = QPushButton("Montrer l'emplacement du nombre", self)
        special_number_show.clicked.connect(self.on_input_object)
        special_number_erase = QPushButton('Effacer', self)
        special_number_erase.clicked.connect(self.doubleRuler.main_ruler.onEraseSpecialNumber)
        special_number_layout.addWidget(special_number_label)
        special_number_layout.addWidget(self.special_number_input)
        special_number_layout.addWidget(special_number_show)
        special_number_layout.addWidget(special_number_erase)

        homothetie_layout = QHBoxLayout()
        self.homothetie_current_label = QLabel('Homothétie actuelle: 1', self)
        homothetie_label = QLabel('Entrer manuellement une homothétie: ', self)
        self.homothetie_input = QLineEdit()
        self.homothetie_input.setValidator(QDoubleValidator())
        homothetie_set = QPushButton("Appliquer l'homothétie", self)
        homothetie_set.clicked.connect(self.on_homothetie_set)
        homothetie_layout.addWidget(self.homothetie_current_label)
        homothetie_layout.addWidget(homothetie_label)
        homothetie_layout.addWidget(self.homothetie_input)
        homothetie_layout.addWidget(homothetie_set)

        self.doubleRuler.main_ruler.value_changed.connect(self.on_ruler_value_changed)
        self.doubleRuler.low_ruler.value_changed.connect(self.on_ruler_value_changed)

        layout.addLayout(show_integer_layout)
        layout.addWidget(self.doubleRuler)
        layout.addLayout(special_number_layout)
        layout.addLayout(homothetie_layout)

        # Set the layout and window properties
        self.setLayout(layout)
        self.setWindowTitle('Z dans tous ses états')
        self.setGeometry(300, 300, 500, 300)

    def on_input_object(self):
        special_number = self.special_number_input.text()
        try:
            self.doubleRuler.main_ruler.showSpecialNumber(float(special_number))
        except ValueError:
            self.doubleRuler.main_ruler.showSpecialNumber(None)

    def on_homothetie_set(self):
        homothetie = self.homothetie_input.text()
        try:
            self.doubleRuler.set_homothetie(float(homothetie))
        except ValueError:
            print(f'The value {homothetie} is not acceptable')

    def on_ruler_value_changed(self):
        homothetie = self.doubleRuler.low_ruler.homothetie
        self.homothetie_current_label.setText(f'Homothécie actuelle : {homothetie: .2f}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RulerWindow()
    window.show()
    sys.exit(app.exec_())