import subprocess
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QPushButton,
    QLineEdit, 
    QPlainTextEdit, 
    QCheckBox, 
)


class Stream(QThread):
    signal_linea = pyqtSignal(str)   
    signal_finish = pyqtSignal(int)  

    def __init__(self, cmd_list):
        super().__init__()
        self.lista_comando = cmd_list

    def run(self):
        try:
            with subprocess.Popen(
                self.lista_comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,               
                bufsize=1,               
                universal_newlines=True  
            ) as proceso:
                for linea_salida in proceso.stdout:
                    self.signal_linea.emit(linea_salida.rstrip("\n"))
                codigo_retorno = proceso.wait()
                self.signal_finish.emit(codigo_retorno)

        except Exception as error:
            self.signal_linea.emit("Error al ejecutar el comando")
            self.signal_finish.emit(1)  



class COnstruccionDocker(QWidget):
    volver_menu = pyqtSignal()


    def __init__(self, parent=None):
        super().__init__(parent)
        self.run_stream = None
        self.construccion_activa = False
        self.dispositivo_remoto_activo = False
        self.dispositivo_remoto_nombre = "" 
        ventana = QVBoxLayout(self)
        ventana.setContentsMargins(16, 16, 16, 16)
        ventana.setSpacing(10)

        titulo = QLabel("Construcción de imágenes en Docker")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        titulo.setStyleSheet("font-size: 22px; font-weight: 600; margin: 4px 0;")
        ventana.addWidget(titulo)

        #fila 1 construccion
        fila1 = QHBoxLayout()
        fila1.setSpacing(10)
        label_builder = QLabel("Builder:")
        self.input_builder = QLineEdit()
        self.input_builder.setPlaceholderText("especificar builder")
        boton_listar_builders = QPushButton("Listar builders")
        boton_listar_builders.setMinimumHeight(32)
        label_plataformas = QLabel("Plataformas:")
        self.input_platformas = QLineEdit()
        self.input_platformas.setPlaceholderText("ejemplo: linux/amd64,linux/arm64")
        fila1.addWidget(label_builder)
        fila1.addWidget(self.input_builder, stretch=1)
        fila1.addWidget(boton_listar_builders)
        fila1.addSpacing(10)
        fila1.addWidget(label_plataformas)
        fila1.addWidget(self.input_platformas, stretch=1)
        ventana.addLayout(fila1)

        #fila2 construccion
        fila2 = QHBoxLayout()
        fila2.setSpacing(10)
        label_imagen = QLabel("Imagen (-t):")
        self.input_imagen = QLineEdit()
        self.input_imagen.setPlaceholderText("nombre de imagen")
        boton_listar_imagenes = QPushButton("Listar imágenes")
        boton_listar_imagenes.setMinimumHeight(32)
        label_contexto = QLabel("Contexto:")
        self.input_contexto = QLineEdit()
        self.input_contexto.setPlaceholderText("ruta o URL")
        fila2.addWidget(label_imagen)
        fila2.addWidget(self.input_imagen, stretch=1)
        fila2.addWidget(boton_listar_imagenes)
        fila2.addSpacing(18)
        fila2.addWidget(label_contexto)
        fila2.addWidget(self.input_contexto, stretch=1)
        ventana.addLayout(fila2)

        #fila3 construccion
        fila3 = QHBoxLayout()
        fila3.setSpacing(10)
        self.cb_push = QCheckBox("Push")
        self.cb_no_cache = QCheckBox("No usar caché")
        self.cb_cache_from = QCheckBox("Importar caché")
        self.input_cache_from = QLineEdit()
        self.input_cache_from.setPlaceholderText("CACHE_ORIGEN p.ej. repo/img:cache")
        self.input_cache_from.setEnabled(False)
        self.cb_cache_to = QCheckBox("Exportar caché")
        self.input_cache_to = QLineEdit()
        self.input_cache_to.setPlaceholderText("CACHE_DESTINO p.ej. repo/img:cache")
        self.input_cache_to.setEnabled(False)
        self.cb_cache_from.toggled.connect(self.input_cache_from.setEnabled)
        self.cb_cache_to.toggled.connect(self.input_cache_to.setEnabled)
        fila3.addWidget(self.cb_push)
        fila3.addSpacing(12)
        fila3.addWidget(self.cb_no_cache)
        fila3.addSpacing(16)
        fila3.addWidget(self.cb_cache_from)
        fila3.addWidget(self.input_cache_from, stretch=1)
        fila3.addSpacing(16)
        fila3.addWidget(self.cb_cache_to)
        fila3.addWidget(self.input_cache_to, stretch=1)
        ventana.addLayout(fila3)

        #fila 4 construccion
        fila4 = QHBoxLayout()
        fila4.setSpacing(10)
        self.boton_build = QPushButton("Construir imagen")
        self.boton_build.setMinimumHeight(32)
        fila4.addWidget(self.boton_build) 
        fila4.addStretch(1)
        ventana.addLayout(fila4)     
   


        #Ventana para outputs
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Los resultados aparecerán aquí!!!")
        ventana.addWidget(self.output)

        #boton volver al menú
        boton_volver = QPushButton("Volver al Menú principal")
        boton_volver.setMinimumHeight(32); boton_volver.clicked.connect(self.volver_menu.emit)
        pal = boton_volver.palette()
        pal.setColor(QPalette.ColorRole.ButtonText, QColor(255, 0, 0))
        boton_volver.setPalette(pal)
        ventana.addWidget(boton_volver, alignment=Qt.AlignmentFlag.AlignHCenter)



        #boton limpiar outputs
        fila = QHBoxLayout()
        label_prueba = QLabel("ssh nodo:")
        self.input_ssh = QLineEdit()
        self.input_ssh.setPlaceholderText("introducir nodo")
        self.input_ssh.setMaximumHeight(32)
        boton_ssh = QPushButton("Activar ssh")
        boton_ssh.setMinimumHeight(32)
        boton_ssh_dead = QPushButton("Cortar conexion ssh")
        boton_ssh_dead.setMinimumHeight(32)
        fila.addWidget(label_prueba)
        fila.addWidget(self.input_ssh, stretch=1)
        fila.addWidget(boton_ssh)
        fila.addWidget(boton_ssh_dead) 
        fila.addStretch(2)

        boton_limpiar = QPushButton("Limpiar terminal")
        boton_limpiar.setMinimumHeight(32)
        
        fila.addWidget(boton_limpiar)
        ventana.addLayout(fila)

        #accion botones listar builders e imagenes
        boton_listar_imagenes.clicked.connect(self.listar_imagenes)
        boton_listar_builders.clicked.connect(self.listar_builders)

        #accion activar ssh connection
        boton_ssh.clicked.connect(self.ssh_connection)
        boton_ssh_dead.clicked.connect(self.usar_local)

        #accion de construccion de imagen
        self.boton_build.clicked.connect(self.construir_imagen)

        #accion botones volver menu y limpiar terminal
        boton_volver.clicked.connect(self.volver_menu.emit)
        boton_limpiar.clicked.connect(self.output.clear)

    def mostrar_texto(self, text: str):
        self.output.moveCursor(self.output.textCursor().MoveOperation.End)
        self.output.insertPlainText(text + ("\n" if not text.endswith("\n") else ""))

    #funciones de listado
    def listar_imagenes(self):
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh", self.dispositivo_remoto_nombre, "docker", "images", "--format", "table{{.Repository}}:{{.Tag}}------{{.ID}}------{{.Size}}" ]
        else:
            cmd = ["docker", "images", "--format", "table {{.Repository}}:{{.Tag}}------{{.ID}}------{{.Size}}" ]
        self.mostrar_texto("\n---Listando imágenes---\n \n")
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Lista de imágenes mostrada---"))
        stream.start()

    def listar_builders(self):
        self.mostrar_texto(self.dispositivo_remoto_nombre)
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh", self.dispositivo_remoto_nombre, "docker", "buildx", "ls"]
        else:
            cmd = ["docker", "buildx", "ls"]

        self.mostrar_texto("\n---Listando builders---\n \n")
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Lista de builders mostrada---"))
        stream.start()


    def construir_imagen(self):
        builder = (self.input_builder.text() or "").strip()
        plataformas = (self.input_platformas.text() or "").strip()
        imagen = (self.input_imagen.text() or "").strip()
        contexto = (self.input_contexto.text() or "").strip()

        if not builder:
            self.mostrar_texto("Falta especificar el builder")
            return
        if not plataformas:
            self.mostrar_texto("Falta especificar las plataformas")
            return
        if not imagen:
            self.mostrar_texto("Falta especificar la imagen")
            return
        if not contexto:
            self.mostrar_texto("Falta especificar el contexto")
            return
        
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = [
                "ssh", self.dispositivo_remoto_nombre,
                "docker", "buildx", "build",
                "--builder", builder,
                "--platform", plataformas,
                "-t", imagen,
                contexto
            ]
            
        else:
            cmd = [
                "docker", "buildx", "build",
                "--builder", builder,
                "--platform", plataformas,
                "-t", imagen,
                contexto
            ]

        if self.cb_push.isChecked():
            cmd.insert(-1, "--push")
        if self.cb_no_cache.isChecked():
            cmd.insert(-1, "--no-cache")
        if self.cb_cache_from.isChecked():
            cache_from = (self.input_cache_from.text() or "").strip()
            if not cache_from:
                self.mostrar_texto("Caché importada no especificada")
                return
            else:
                cmd.insert(-1, f"--cache-from=type=registry,ref={cache_from}")
        
        if self.cb_cache_to.isChecked():
            cache_to = (self.input_cache_to.text() or "").strip()
            if not cache_to:
                self.mostrar_texto("Caché a exportar no especificada")
                return
            else:
                cmd.insert(-1, f"--cache-to=type=registry,ref={cache_to}")

        self.mostrar_texto("---Comenzando build de la " + imagen + "---")
        stream = Stream(cmd)
        self.construccion_activa = True
        self.run_stream = stream
        self.boton_build.setEnabled(False)
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(self.build_acabado)
        stream.start()
    
    def build_acabado(self):
        self.mostrar_texto("---Build acabado---")
        self.construccion_activa = False
        self.boton_build.setEnabled(True)
     

    def ssh_connection(self):
        ssh = (self.input_ssh.text() or "").strip()  
        if not ssh:
            self.mostrar_texto("Introduce el usuario y host, p. ej. lvalverde@192.168.1.66")
            return
        self.dispositivo_remoto_nombre = ssh
        self.dispositivo_remoto_activo = True
        self.mostrar_texto("\n---Dispositivo remoto " + self.dispositivo_remoto_nombre + "---\n")

    def usar_local(self):
        self.dispositivo_remoto_activo = False
        self.dispositivo_remoto_nombre = ""
        self.mostrar_texto("\n---Modo local ACTIVADO---\n")
