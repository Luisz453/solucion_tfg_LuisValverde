import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ventanas.menu import MenuAplicacion
from ventanas.gestion import GestionDocker
from ventanas.configuracion import ConfiguracionDocker
from ventanas.construccion import COnstruccionDocker
from ventanas.despliegue import DespliegueDocker

MENU = 0
GESTION = 1
CONFIGURACION = 2
CONSTRUCCION = 3
DESPLIEGUE = 4

class MainAplicacion(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Herramienta Docker TFG")
        self.resize(1100, 750)
        self.setMinimumSize(1100, 750)
        
        #contendor de ventanas
        self.contenedor_ventanas= QStackedWidget()
        self.setCentralWidget(self.contenedor_ventanas)

        #incicializar ventanar
        self.ventana_menu = MenuAplicacion()
        self.ventana_gestion = GestionDocker()
        self.ventana_configuracion = ConfiguracionDocker()
        self.ventana_construccion = COnstruccionDocker()
        self.ventana_despliegue = DespliegueDocker()

        #orden del contenedor de ventanas
        self.contenedor_ventanas.addWidget(self.ventana_menu)
        self.contenedor_ventanas.addWidget(self.ventana_gestion) 
        self.contenedor_ventanas.addWidget(self.ventana_configuracion)
        self.contenedor_ventanas.addWidget(self.ventana_construccion)
        self.contenedor_ventanas.addWidget(self.ventana_despliegue)
        
        self.contenedor_ventanas.setCurrentIndex(MENU)
        
        #navegavilidad del menu
        self.ventana_menu.ir_ventana_gestion.connect(lambda: self.contenedor_ventanas.setCurrentIndex(GESTION))
        self.ventana_menu.ir_ventana_configuracion.connect(lambda: self.contenedor_ventanas.setCurrentIndex(CONFIGURACION))
        self.ventana_menu.ir_ventana_construccion.connect(lambda: self.contenedor_ventanas.setCurrentIndex(CONSTRUCCION))
        self.ventana_menu.ir_ventana_despliegue.connect(lambda: self.contenedor_ventanas.setCurrentIndex(DESPLIEGUE))

        #navegavilidad para volver a menu
        self.ventana_gestion.volver_menu.connect(lambda: self.contenedor_ventanas.setCurrentIndex(MENU))
        self.ventana_configuracion.volver_menu.connect(lambda: self.contenedor_ventanas.setCurrentIndex(MENU))
        self.ventana_construccion.volver_menu.connect(lambda: self.contenedor_ventanas.setCurrentIndex(MENU))
        self.ventana_despliegue.volver_menu.connect(lambda: self.contenedor_ventanas.setCurrentIndex(MENU))




app = QApplication(sys.argv)
ventana = MainAplicacion()
ventana.show()
sys.exit(app.exec())