# settings_window.py
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QSpinBox

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")

        layout = QFormLayout(self)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 30)  # 波形显示时长范围1-30秒
        if parent:
            self.duration_spin.setValue(parent.duration_sec)  # 初始化为父窗口的当前值
        layout.addRow("波形显示时长（秒）:", self.duration_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
