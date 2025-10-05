from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class MenuAplicacion(QWidget):
    ir_ventana_gestion = pyqtSignal()
    ir_ventana_configuracion = pyqtSignal()
    ir_ventana_construccion = pyqtSignal()
    ir_ventana_despliegue = pyqtSignal()

    def __init__(self,parent=None):
        super().__init__(parent)
        ventana = QVBoxLayout(self)
        ventana.setContentsMargins(24, 24, 24, 24)
        ventana.setSpacing(60)

        titulo = QLabel("Menú Principal")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        titulo.setStyleSheet("font-size: 30px; font-weight: 600; margin: 8px 0;")
        ventana.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignHCenter)

        ventana.addStretch(1)

        boton_gestion = QPushButton("Gestión de Docker")
        boton_configuracion  = QPushButton("Configuración builders")
        boton_construccion   = QPushButton("Construcción imágenes")
        boton_despliegue  = QPushButton("Desplegar contenedores")  

        for x in (boton_gestion, boton_configuracion, boton_construccion, boton_despliegue):
            x.setMinimumHeight(100)
            x.setMinimumWidth(500)
            x.setMaximumWidth(500)
            ventana.addWidget(x, alignment=Qt.AlignmentFlag.AlignHCenter)

        ventana.addStretch(1)

        boton_gestion.clicked.connect(self.ir_ventana_gestion.emit)
        boton_configuracion.clicked.connect(self.ir_ventana_configuracion.emit)
        boton_construccion.clicked.connect(self.ir_ventana_construccion.emit)
        boton_despliegue.clicked.connect(self.ir_ventana_despliegue.emit)




        