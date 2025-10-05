
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QPushButton,
    QPlainTextEdit, 
    QLineEdit
)
import subprocess



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


class GestionDocker(QWidget):
    volver_menu = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.run_stream = None
        self.dispositivo_remoto_activo = False
        self.dispositivo_remoto_nombre = "" 

        ventana = QVBoxLayout(self)
        ventana.setContentsMargins(16, 16, 16, 16)
        ventana.setSpacing(10)

        titulo = QLabel("Gestión de recursos Docker")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        titulo.setStyleSheet("font-size: 22px; font-weight: 600; margin: 4px 0;")
        ventana.addWidget(titulo)

        #gestion imagenes
        imagen = QHBoxLayout()
        imagen.setSpacing(10)

        boton_listar_imagen = QPushButton("Listar imágenes")
        boton_listar_imagen.setMinimumHeight(32)

        label_imagen = QLabel("Imagen:")
        self.input_imagen = QLineEdit()
        self.input_imagen.setPlaceholderText("ejemplo: repo/imagen:tag o ubuntu:latest")
        self.input_imagen.setMinimumWidth(260)

        boton_rm_imagen = QPushButton("Eliminar imagen")
        boton_rm_imagen.setMinimumHeight(32)

        imagen.addWidget(boton_listar_imagen)
        imagen.addSpacing(16)
        imagen.addWidget(label_imagen)
        imagen.addWidget(self.input_imagen, stretch=1)
        imagen.addWidget(boton_rm_imagen)
        ventana.addLayout(imagen)

        #gestion contenedores
        contenedor = QHBoxLayout()
        contenedor.setSpacing(10)

        boton_listar_contenedores = QPushButton("Listar contenedores")
        boton_listar_contenedores.setMinimumHeight(32)

        label_contenedor = QLabel("Contenedor:")
        self.input_contenedor = QLineEdit()
        self.input_contenedor.setPlaceholderText("ejemplo: mi_contenedor o ID contenedor")
        self.input_contenedor.setMaximumHeight(260)

        boton_rm_contenedor = QPushButton("Eliminar contenedor")
        boton_rm_contenedor.setMinimumHeight(32)

        boton_stop_contenedor = QPushButton("Parar contenedor")
        boton_stop_contenedor.setMinimumHeight(32)

        contenedor.addWidget(boton_listar_contenedores)
        contenedor.addSpacing(16)
        contenedor.addWidget(label_contenedor)
        contenedor.addWidget(self.input_contenedor, stretch=1)
        contenedor.addWidget(boton_rm_contenedor)
        contenedor.addWidget(boton_stop_contenedor)
        ventana.addLayout(contenedor)

        #gestion builder
        builder = QHBoxLayout()
        builder.setSpacing(10)

        boton_listar_builders = QPushButton("Listar builders")
        boton_listar_builders.setMinimumHeight(32)

        label_builder = QLabel("Builder:")
        self.input_builder = QLineEdit()
        self.input_builder.setPlaceholderText("ejemplo: multiplatform-builder")
        self.input_builder.setMaximumHeight(260)

        boton_rm_builder = QPushButton("Eliminar builder")
        boton_rm_builder.setMinimumHeight(32)

        builder.addWidget(boton_listar_builders)
        builder.addSpacing(16)
        builder.addWidget(label_builder)
        builder.addWidget(self.input_builder, stretch=1)
        builder.addWidget(boton_rm_builder)
        ventana.addLayout(builder)


        #borrar cache builder
        cache = QHBoxLayout()
        cache.setSpacing(10)

        label_rm_cache = QLabel("Builder (para borrar caché):")
        self.input_cache = QLineEdit()
        self.input_cache.setPlaceholderText("ejemplo: multiplatform-builder")
        self.input_cache.setMaximumHeight(260)

        boton_rm_cache = QPushButton("Borrar caché")
        boton_rm_cache.setMinimumHeight(32)

        cache.addWidget(label_rm_cache)
        cache.addWidget(self.input_cache, stretch=1)
        cache.addWidget(boton_rm_cache)
        ventana.addLayout(cache)


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
        boton_listar_imagen.clicked.connect(self.listar_imagenes)
        boton_rm_imagen.clicked.connect(self.eliminar_imagen)

        #accion botones relacionados con contenedores
        boton_listar_contenedores.clicked.connect(self.listar_contenedores)
        boton_rm_contenedor.clicked.connect(self.eliminar_contenedor)
        boton_stop_contenedor.clicked.connect(self.stop_contenedor)

        #accion botones relacionados con builders
        boton_listar_builders.clicked.connect(self.listar_builders)
        boton_rm_builder.clicked.connect(self.eliminar_buildr)
        boton_rm_cache.clicked.connect(self.borrar_cache_builder)

        #accion activar ssh connection
        boton_ssh.clicked.connect(self.ssh_connection)
        boton_ssh_dead.clicked.connect(self.usar_local)

        #accion botones volver menu y limpiar terminal
        boton_volver.clicked.connect(self.volver_menu.emit)
        boton_limpiar.clicked.connect(self.output.clear)

    def mostrar_texto(self, text: str):
        self.output.moveCursor(self.output.textCursor().MoveOperation.End)
        self.output.insertPlainText(text + ("\n" if not text.endswith("\n") else ""))


    #Funciones de imágenes
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

    def eliminar_imagen(self):
        imagen = (self.input_imagen.text() or "").strip()
        if not imagen:
            self.mostrar_texto("Introduce el nombre o ID de la imagen.")
            return
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh", self.dispositivo_remoto_nombre, "docker", "rmi", "-f", imagen]
        else:
            cmd = ["docker", "rmi", "-f", imagen]
        self.mostrar_texto("\n---Eliminando imagen " + imagen + "---\n\n" )
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Imagen: " + imagen + " eliminada---"))
        stream.start()


    #Funciones de contenedores
    def listar_contenedores(self):
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh", self.dispositivo_remoto_nombre, "docker", "ps", "-a", "--format", "table{{.ID}}------{{.Names}}------{{.Status}}------{{.Image}}"]
        else:
            cmd = ["docker", "ps", "-a", "--format", "table {{.ID}} | {{.Names}} | {{.Status}} | {{.Image}}"]
        self.mostrar_texto("\n---Listando contenedores---\n \n")
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Lista de contenedores mostrada---"))
        stream.start()


    def eliminar_contenedor(self):
        contenedor = (self.input_contenedor.text() or "").strip()
        if not contenedor:
            self.mostrar_texto("Introduce el nombre o ID del contenedor.")
            return
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh", self.dispositivo_remoto_nombre, "docker", "rm", "-f", contenedor]
        else:
            cmd = ["docker","rm", "-f", contenedor]
        self.mostrar_texto("\n---Eliminando contenedor " + contenedor + "---\n\n" )
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Contenedor: " + contenedor + " eliminada---"))
        stream.start()

    def stop_contenedor(self):
        contenedor = (self.input_contenedor.text() or "").strip()
        if not contenedor:
            self.mostrar_texto("Introduce el nombre o ID del contenedor.")
            return
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh", self.dispositivo_remoto_nombre, "docker","stop",  contenedor]
        else:
            cmd = ["docker","stop",  contenedor]

        self.mostrar_texto("\n---Parando contenedor " + contenedor + "---\n\n" )
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Contenedor: " + contenedor + " parado---"))
        stream.start()

    #Funciones de builders
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


    def eliminar_buildr(self):
        builder = (self.input_builder.text() or "").strip()
        if not builder:
            self.mostrar_texto("Introduce el nombre o ID del builder.")
            return

        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh", self.dispositivo_remoto_nombre, "docker", "buildx", "rm", "-f", builder]
        else:
            cmd = ["docker", "buildx", "rm", "-f", builder]

        self.mostrar_texto(f"\n---Eliminando builder {builder}---\n\n")
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto(f"\n---Builder: {builder} eliminado---"))
        stream.start()
        
    def borrar_cache_builder(self):
        cache = (self.input_cache.text() or "").strip()
        if not cache:
            self.mostrar_texto("Introduce el nombre del builder.")
            return

        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh", self.dispositivo_remoto_nombre, "docker", "buildx", "prune", "--builder", cache, "--all", "-f"]
        else:
            cmd = ["docker", "buildx", "prune", "--builder", cache, "--all", "-f"]

        self.mostrar_texto(f"\n---Eliminando caché del builder {cache}---\n\n")
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto(f"\n---Caché del builder: {cache} eliminada---"))
        stream.start()



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
