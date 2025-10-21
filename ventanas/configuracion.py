import subprocess
import shlex
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


class ConfiguracionDocker(QWidget):
    volver_menu = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.run_stream = None
        self.run_stream2 = None
        self.dispositivo_remoto_activo = False
        self.dispositivo_remoto_nombre = "" 

        ventana = QVBoxLayout(self)
        ventana.setContentsMargins(16, 16, 16, 16)
        ventana.setSpacing(10)

        titulo = QLabel("Configuración de builders")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        titulo.setStyleSheet("font-size: 22px; font-weight: 600; margin: 4px 0;")
        ventana.addWidget(titulo)

        #Builder multinodo
        multinodo = QHBoxLayout()
        multinodo.setSpacing(10)

        label_multinodo = QLabel("Builder a crear:")
        self.input_multinodo = QLineEdit()
        self.input_multinodo.setPlaceholderText("Nombre builder")
        boton_crear_builder = QPushButton("Crear Builder")
        boton_crear_builder.setMinimumHeight(32)
        multinodo.addWidget(label_multinodo)
        multinodo.addWidget(self.input_multinodo, stretch=1)
        multinodo.addWidget(boton_crear_builder)
        multinodo.addSpacing(10)
        label_nodo = QLabel("Nodo (ssh://...):")
        self.input_nodo = QLineEdit()
        self.input_nodo.setPlaceholderText("ssh://nombre_usuario@ip")
        label_destino = QLabel("en builder:")
        self.input_builder_destion = QLineEdit()
        self.input_builder_destion.setPlaceholderText("nombre builder destino")
        boton_incluir_nodo = QPushButton("Añadir nodo")
        boton_incluir_nodo.setMinimumHeight(32)


        multinodo.addWidget(label_nodo)
        multinodo.addWidget(self.input_nodo, stretch=1)
        multinodo.addWidget(label_destino)
        multinodo.addWidget(self.input_builder_destion, stretch=1)
        multinodo.addWidget(boton_incluir_nodo)
        ventana.addLayout(multinodo)

        #cloud builder
        cloud = QHBoxLayout()
        cloud.setSpacing(10)

        label_cloud = QLabel("Nombre del cloud Builder:")
        self.input_cloud = QLineEdit()
        self.input_cloud.setPlaceholderText("ejemplo: luis453/prueba-cloud")
        boton_cloud = QPushButton("Añadir Cloud Builder")
        boton_cloud.setMinimumHeight(32)

        cloud.addWidget(label_cloud)
        cloud.addWidget(self.input_cloud, stretch=1)
        cloud.addWidget(boton_cloud)
        ventana.addLayout(cloud)

        #boton QEMU
        qemu = QHBoxLayout()
        qemu.setSpacing(10)

        boton_qemu = QPushButton("Activar QEMU")
        boton_qemu.setMinimumHeight(32)
        qemu.addWidget(boton_qemu)
        qemu.addStretch(1)
        boton_listar_builder = QPushButton("Listar builders")
        boton_listar_builder.setMinimumHeight(32)
        qemu.addWidget(boton_listar_builder)
        ventana.addLayout(qemu)

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


        #acciones de creacion de builder multinodo
        boton_crear_builder.clicked.connect(self.crear_builder)
        boton_incluir_nodo.clicked.connect(self.incluir_nodo)

        #accion boton instanciar build cloud
        boton_cloud.clicked.connect(self.instancia_cloud)

        #accion activar qemu
        boton_qemu.clicked.connect(self.activar_qemu)

        #listar builder
        boton_listar_builder.clicked.connect(self.listar_builders)

        #accion activar ssh connection
        boton_ssh.clicked.connect(self.ssh_connection)
        boton_ssh_dead.clicked.connect(self.usar_local)


        #accion botones volver menu y limpiar terminal
        boton_volver.clicked.connect(self.volver_menu.emit)
        boton_limpiar.clicked.connect(self.output.clear)


    def mostrar_texto(self, text: str):
        self.output.moveCursor(self.output.textCursor().MoveOperation.End)
        self.output.insertPlainText(text + ("\n" if not text.endswith("\n") else ""))


    def listar_builders(self):
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh"] + self.dispositivo_remoto_nombre + ["docker", "buildx", "ls"]
        else:
            cmd = ["docker", "buildx", "ls"]

        self.mostrar_texto("\n---Listando builders---\n \n")
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Lista de builders mostrada---"))
        stream.start()

    #funciones de creacion de builders multinodo
    def crear_builder(self):
        nombre_builder = (self.input_multinodo.text() or "").strip()
        if not nombre_builder:
            self.mostrar_texto("Introducir nombre del builder a crear")
            return 
        
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh"] + self.dispositivo_remoto_nombre + ["docker", "buildx", "create", "--name", nombre_builder, "--driver", "docker-container"]
        else:
            cmd = ["docker", "buildx", "create", "--name", nombre_builder, "--driver", "docker-container"]
        
        self.mostrar_texto("\n---Creando el builder: " + nombre_builder + "---\n\n")
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Builder: " + nombre_builder + " creado---"))
        stream.start()

    def incluir_nodo(self):
        nombre_nodo = (self.input_nodo.text() or "").strip()
        if not nombre_nodo:
            self.mostrar_texto("Introducir nombre del nodo a añadir (ssh://usuario@host)")
            return
        builder_destino = (self.input_builder_destion.text() or "").strip()
        if not builder_destino:
            self.mostrar_texto("Introducir nombre del builder al cual añadir el nodo")
            return
        try:
            nombre_nodo_aux = shlex.split(nombre_nodo) if nombre_nodo else []
        except ValueError as e:
            self.mostrar_texto("Error al procesar el hostname \n")
            return

        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd1 = ["ssh"] + self.dispositivo_remoto_nombre + ["docker", "buildx", "create", "--name", builder_destino, "--append", nombre_nodo]
            cmd2 = ["ssh"] + self.dispositivo_remoto_nombre + ["docker", "buildx", "inspect", "--builder", builder_destino, "--bootstrap"]
        else:        
            cmd1 = ["docker", "buildx", "create", "--name", builder_destino,"--append", nombre_nodo]
            cmd2 = ["docker", "buildx", "inspect", "--builder", builder_destino, "--bootstrap"]

        self.mostrar_texto("\n---Añadiendo nodo "+ nombre_nodo + " a builder " + builder_destino + "---")

        stream = Stream(cmd1)
        self.run_stream = stream  
        stream.signal_linea.connect(self.mostrar_texto)

        def al_terminar_primero(builder=builder_destino, cmd_bootstrap=cmd2):
            self.mostrar_texto("---Nodo añadido---\n")

            self.mostrar_texto("---Activación Builder---\n")

            stream2 = Stream(cmd_bootstrap)
            self.run_stream2 = stream2  
            stream2.signal_linea.connect(self.mostrar_texto)
            stream2.signal_finish.connect(lambda: self.mostrar_texto("\n---Activación de builder realizada correctamente---"))
            stream2.start()

        stream.signal_finish.connect(al_terminar_primero)   
        stream.start()


    #funciones de Docker CLoud
    def instancia_cloud(self):
        nombre_cloud = (self.input_cloud.text() or "").strip()
        if not nombre_cloud:
            self.mostrar_texto("Introducir nombre del builder cloud a instanciar")
            return 
        
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh"] + self.dispositivo_remoto_nombre + ["docker", "buildx", "create", "--driver", "cloud", nombre_cloud]
        else:
            cmd = ["docker", "buildx", "create", "--driver", "cloud", nombre_cloud]
        
        self.mostrar_texto("\n---Instanciando el builder cloud: " + nombre_cloud + "---\n\n")
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Builder cloud: " + nombre_cloud + " instanciado---"))
        stream.start()

    #funcion para activar QEMU
    def activar_qemu(self):
        if self.dispositivo_remoto_activo and self.dispositivo_remoto_nombre:
            cmd = ["ssh"] + self.dispositivo_remoto_nombre + [ "docker", "run", "--privileged", "--rm", "tonistiigi/binfmt", "--install", "all"]
        else:
            cmd = ["docker", "run", "--privileged", "--rm", "tonistiigi/binfmt", "--install", "all"]
        self.mostrar_texto("\n---Activando emulación por QEMU---\n\n")
        stream = Stream(cmd)
        self.run_stream = stream
        stream.signal_linea.connect(self.mostrar_texto)
        stream.signal_finish.connect(lambda: self.mostrar_texto("\n---Emulación QEMU activada---"))
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
