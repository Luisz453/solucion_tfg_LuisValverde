import subprocess
import os
import shlex
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QPushButton,
    QLineEdit, 
    QPlainTextEdit
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
            self.signal_linea.emit(f"ERROR al ejecutar el comando: {error}")
            self.signal_finish.emit(1)  


class DespliegueDocker(QWidget):
    volver_menu = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.run_stream = None
        self.dispositivo_remoto_activo = False
        self.dispositivo_remoto_nombre = "" 
        ventana = QVBoxLayout(self)
        ventana.setContentsMargins(16, 16, 16, 16)
        ventana.setSpacing(10)

        titulo = QLabel("Despliegue de contenedores Docker")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        titulo.setStyleSheet("font-size: 22px; font-weight: 600; margin: 4px 0;")
        ventana.addWidget(titulo)

        #fila 1 despliegue
        fila1 = QHBoxLayout()
        fila1.setSpacing(10)
        label_contenedor = QLabel("Nombre contenedor:")
        self.input_contenedor = QLineEdit()
        self.input_contenedor.setPlaceholderText("nombre del contenedor")
        label_imagen = QLabel("Imagen:")
        self.input_imagen = QLineEdit()
        self.input_imagen.setPlaceholderText("nombre de la imagen")
        boton_listar_imagenes = QPushButton("Listar imágenes")
        boton_listar_imagenes.setMinimumHeight(32)
        fila1.addWidget(label_contenedor)
        fila1.addWidget(self.input_contenedor, stretch=1)
        fila1.addSpacing(10)
        fila1.addWidget(label_imagen)
        fila1.addWidget(self.input_imagen, stretch=1)
        fila1.addWidget(boton_listar_imagenes)
        ventana.addLayout(fila1)

        #fila2 despliegue
        fila2 = QHBoxLayout()
        fila2.setSpacing(10)
        label_flags = QLabel("Flags opcionales:")
        self.input_flags = QLineEdit()
        self.input_flags.setPlaceholderText("ejemplo: -d -p 8080:80 -v /host:/cont ...")
        fila2.addWidget(label_flags)
        fila2.addWidget(self.input_flags, stretch=1)
        ventana.addLayout(fila2)  

        #fila3 despliegue
        fila3 = QHBoxLayout()
        fila3.setSpacing(10)
        boton_run = QPushButton("Crear contenedor")
        boton_run.setMinimumHeight(32)
        label_pull = QLabel("Pull de imagen:")
        self.input_pull = QLineEdit()
        self.input_pull.setPlaceholderText("nombre de imagen")
        boton_pull = QPushButton("Pull imagen")
        fila3.addWidget(boton_run)
        fila3.addSpacing(12)
        fila3.addStretch(1)
        fila3.addWidget(label_pull)
        fila3.addWidget(self.input_pull, stretch=1)
        fila3.addWidget(boton_pull)
        ventana.addLayout(fila3)    

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


        #accion botones relacionados con imágenes
        boton_listar_imagenes.clicked.connect(self.listar_imagenes)

        #accion lanzar un contenedor
        boton_run.clicked.connect(self.despliegue_contenedor)

        #accion activar ssh connection
        boton_ssh.clicked.connect(self.ssh_connection)
        boton_ssh_dead.clicked.connect(self.usar_local)

        #accion pull
        boton_pull.clicked.connect(self.pull_imagen)

        #accion botones volver menu y limpiar terminal
        boton_volver.clicked.connect(self.volver_menu.emit)
        boton_limpiar.clicked.connect(self.output.clear)



    def mostrar_texto(self, text: str):
        self.output.moveCursor(self.output.textCursor().MoveOperation.End)
        self.output.insertPlainText(text + ("\n" if not text.endswith("\n") else ""))


    #funcion de imagen
    def listar_imagenes(self):
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh"] + self.dispositivo_remoto_nombre + ["docker", "images", "--format", "table{{.Repository}}:{{.Tag}}------{{.ID}}------{{.Size}}" ]
        else:
            cmd = ["docker", "images", "--format", "table {{.Repository}}:{{.Tag}}------{{.ID}}------{{.Size}}" ]
        self.mostrar_texto("\n---Listando imágenes---\n \n")
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Lista de imágenes mostrada---"))
        stream.start()

    #funcion de desplegar contenedor
    def despliegue_contenedor(self):
        contenedor = (self.input_contenedor.text() or "").strip()
        imagen = (self.input_imagen.text() or "").strip()
        flags = (self.input_flags.text() or "").strip()

        if not contenedor:
            self.mostrar_texto("Falta especificar el nombre de contenedor")
            return
        if not imagen:
            self.mostrar_texto("Falta especificar la imagen")
            return
            
        try:
            flags_procesadas = shlex.split(flags) if flags else []
        except ValueError as e:
            self.mostrar_texto("Error al procesar los flags \n")
            return

        flags_finales = [os.path.expanduser(os.path.expandvars(flag)) for flag in flags_procesadas]

        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh"] + self.dispositivo_remoto_nombre + ["docker", "run", "--name", contenedor] + flags_finales + [imagen]
        else:
            cmd = ["docker", "run", "--name", contenedor] + flags_finales + [imagen]
        

        self.mostrar_texto("\n---Creando contenedor--- \n\n")

        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Contenedor creado---"))
        stream.start()

    #funcion de pull
    def pull_imagen(self):
        pull = (self.input_pull.text() or "").strip()
        if not pull:
            self.mostrar_texto("No se ha especificado la imagen para hacer el pull")
            return
        
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh"] + self.dispositivo_remoto_nombre + ["docker", "pull", pull]
        else:
            cmd = ["docker", "pull", pull]

        self.mostrar_texto("\n---Iniciando el pull--- \n\n")
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Pull realizado---"))
        stream.start()

    def ssh_connection(self):
        ssh = (self.input_ssh.text() or "").strip()  
        if not ssh:
            self.mostrar_texto("Introduce el usuario y host, p. ej. lvalverde@192.168.1.66")
            return
        #self.dispositivo_remoto_nombre = ssh
        try:
            self.dispositivo_remoto_nombre = shlex.split(ssh) if ssh else []
        except ValueError as e:
            self.mostrar_texto("Error al procesar el hostname \n")
            return
        self.dispositivo_remoto_activo = True
        self.mostrar_texto("\n---Dispositivo remoto " + ssh + "---\n")

    def usar_local(self):
        self.dispositivo_remoto_activo = False
        self.dispositivo_remoto_nombre = ""
        self.mostrar_texto("\n---Modo local ACTIVADO---\n")
