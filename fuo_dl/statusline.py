from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QColor, QPalette

from feeluown.widgets.statusline import StatuslineLabel


class DownloadLabel(StatuslineLabel):
    def __init__(self, app, mgr):
        super().__init__(app, parent=None)

        mgr.tasks_changed.connect(self._on_tasks_changed)

        self._timer = QTimer(self)
        self._downloading = False
        self._status_color = 'orange'

        self._timer.timeout.connect(self._on_timer_timeout)
        self._timer.start(1000)

    def _on_timer_timeout(self):
        self._schedule_update()

    def _on_tasks_changed(self, tasks):
        self.setText(str(len(tasks)))
        if len(tasks) > 0:
            self._downloading = True
            self._timer.start()
        else:
            self._downloading = False
            self._timer.stop()
            self._schedule_update()

    def _schedule_update(self):
        """schedule an paint event"""
        self.update()

    def drawInner(self, painter):
        fill_color = self.palette().color(QPalette.Text)
        painter.setBrush(QColor(fill_color))
        painter.setPen(Qt.NoPen)

        # parameters
        inner_width, inner_height = self._inner_width, self._inner_height
        line_width, line_width_half, line_radius = 2, 1, 1

        # draw an arrow in inner rect
        center = inner_width // 2

        # draw the vertical line
        painter.save()
        line_height = 9
        point_height = line_width
        point_top_margin, point_line_margin = 1, 2
        line_top_margin = point_top_margin + point_height + point_line_margin
        x = center - line_width_half
        point_rect = QRect(x, point_top_margin, line_width, line_width)
        line_rect = QRect(x, line_top_margin, line_width, line_height)
        painter.drawRoundedRect(line_rect, line_radius, line_radius)
        painter.drawRoundedRect(point_rect, line_radius, line_radius)

        # draw left and right line
        vertical_line_bottom_y = line_rect.y() + line_rect.height()
        side_line_width, side_line_height = line_width, 6
        angle = 40
        translate_x = inner_width // 2
        translate_y = vertical_line_bottom_y
        side_line_rect = QRect(-side_line_width//2, -side_line_height,
                               side_line_width, side_line_height)
        painter.translate(translate_x, translate_y)
        painter.rotate(-angle)
        painter.drawRoundedRect(side_line_rect, line_radius, line_radius)
        painter.rotate(angle * 2)
        painter.drawRoundedRect(side_line_rect, line_radius, line_radius)
        painter.restore()

        # draw bottom line
        margin_left = 2
        bottom_line_height = 2
        bottom_lr_height = 4
        bottom_line_y = inner_height - 2
        bottom_line_width = inner_width - margin_left * 2
        bottom_line_rect = QRect(margin_left, bottom_line_y,
                                 bottom_line_width, bottom_line_height)
        bottom_lr_y = bottom_line_y - bottom_lr_height + bottom_line_height
        bottom_left_rect = QRect(margin_left, bottom_lr_y,
                                 line_width, bottom_lr_height)
        bottom_right_rect = QRect(margin_left+bottom_line_width-line_width, bottom_lr_y,
                                  line_width, bottom_lr_height)
        painter.drawRoundedRect(bottom_line_rect, 2, 2)
        painter.drawRoundedRect(bottom_left_rect, 2, 2)
        painter.drawRoundedRect(bottom_right_rect, 2, 2)

    def drawStatus(self, painter):
        if self._downloading:
            super().drawStatus(painter)


if __name__ == '__main__':
    from unittest.mock import MagicMock
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    widget = DownloadLabel(MagicMock(), MagicMock())
    widget.show()

    widget.resize(30, 30)
    app.exec()
