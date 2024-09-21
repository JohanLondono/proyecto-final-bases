import sys
import hashlib

from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QLineEdit, QFormLayout, QWidget,
    QComboBox, QMessageBox, QHBoxLayout, QLabel, QDateEdit, QCheckBox, 
    QHeaderView
)
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtCore import QDate, QDateTime, Qt
from datetime import timedelta
from database import get_connection
from dao import SucursalDAO
from dto import SucursalDTO
from dao import EmpleadoDAO
from dto import EmpleadoDTO
from dao import UsuarioDAO
from dto import UsuarioDTO
from dao import SolicitudPrestamoDAO
from dto import SolicitudPrestamoDTO
from dao import PrestamoDAO
from dto import PrestamoSqlDTO
from dto import PrestamoTablaDTO
from dto import PrestamoDetalleDTO
from dao import PagoDAO
from dto import PagoSqlDTO
from dto import PagoTablaDTO
from dao import LogSesionDAO
from dto import LogSesionSqlDTO
from dto import LogSesionTablaDTO

SALARY_RANGES = {
    "OPERARIO": 5000000,
    "ADMINISTRATIVO": 7500000,
    "EJECUTIVO": 10000000,
    "OTROS": 6000000
}

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.connection = get_connection()
        self.usuario_dao = UsuarioDAO(self.connection)
        self.log_sesion_dao = LogSesionDAO(self.connection)
        self.main_app = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login")
        self.setGeometry(500, 250, 300, 200)

        # Campos de login
        self.username_label = QLabel("Nombre de Usuario:")
        self.username_input = QLineEdit(self)

        self.password_label = QLabel("Contraseña:")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)  # Ocultar contraseña

        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.clicked.connect(self.verify_login)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def verify_password(self, stored_password, provided_password):
        return self.hash_password(provided_password) == stored_password
    
    def hash_password(self, password):
        # Crear un objeto hash SHA-256
        sha256 = hashlib.sha256()
        # Actualizar el objeto hash con la contraseña en bytes
        sha256.update(password.encode('utf-8'))
        # Obtener el hash en formato hexadecimal
        return sha256.hexdigest()
    
    def verify_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        user = self.usuario_dao.buscar_por_nombre_usuario(username)

        if user:
            stored_password = user.contraseña
            if self.verify_password(stored_password, password):
                self.registrar_log(user.id_empleado, "ENTRADA", "EXITOSO")
                self.show_main_app(user)
            else:
                self.registrar_log(user.id_empleado, "ENTRADA", "FALLIDO")
                QMessageBox.warning(self, "Error", "Datos Incorrectos")
        else:
            QMessageBox.warning(self, "Error", "Datos Incorrectos")
        
    def show_main_app(self, usuario):
        self.main_app = BankApp(usuario)
        self.main_app.show()
        self.close()
    
    def registrar_log(self, id_usuario, tipo, estado):

        fecha_actual = datetime.now()
        fecha_actual = fecha_actual.strftime('%d-%m-%Y %H:%M:%S')
        log = LogSesionSqlDTO(0, id_usuario, fecha_actual, tipo, estado)
        self.log_sesion_dao.registrar_log_sesion(log)


class BankApp(QMainWindow):
    def __init__(self, usuario: UsuarioDTO):
        super().__init__()
        self.sub_windows = []  # Lista para almacenar ventanas superpuestas
        self.usuario = usuario
        self.connection = get_connection()
        self.sucursal_dao = SucursalDAO(self.connection)
        self.empleado_dao = EmpleadoDAO(self.connection)
        self.usuario_dao = UsuarioDAO(self.connection)
        self.solicitud_prestamo_dao = SolicitudPrestamoDAO(self.connection)
        self.prestamo_dao = PrestamoDAO(self.connection)
        self.pago_dao = PagoDAO(self.connection)
        self.log_sesion_dao = LogSesionDAO(self.connection)
        
        self.setWindowTitle("Sistema de Gestión Bancaria")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.create_menu()

        QApplication.instance().aboutToQuit.connect(self.registrar_salida)
        self.showMaximized()

    
    def closeEvent(self, event):
        # Cerrar todas las ventanas hijas cuando se cierra la ventana principal
        for window in self.sub_windows:
            window.close()
        event.accept()  # Acepta el evento de cierre de la ventana principal

    def registrar_log(self, id_usuario, tipo, estado):
        fecha_actual = datetime.now()
        fecha_actual = fecha_actual.strftime('%d-%m-%Y %H:%M:%S')
        log = LogSesionSqlDTO(0, id_usuario, fecha_actual, tipo, estado)
        self.log_sesion_dao.registrar_log_sesion(log)

    def registrar_salida(self):
        """Método que se llama cuando la aplicación está a punto de cerrarse."""
        self.registrar_log(self.usuario.id_empleado, tipo='SALIDA', estado='EXITOSO')


    def create_menu(self):
        self.menu_bar = self.menuBar()

        if self.usuario.rol == "PRINCIPAL":
            self.open_admin_menu()
        elif self.usuario.rol == "TESORERIA":
            self.open_treasury_menu()
        elif self.usuario.rol == "EMPLEADO":
            self.open_employee_menu()

    def open_admin_menu(self):
        self.menu_bar = self.menuBar()
        self.create_admin_menus()
        QMessageBox.information(self, "Bienvenido", "Has iniciado sesión como Administrador")

    def open_treasury_menu(self):
        self.menu_bar = self.menuBar()
        self.create_treasury_menus()
        QMessageBox.information(self, "Bienvenido", "Has iniciado sesión como Tesorería")

    def open_employee_menu(self):
        self.menu_bar = self.menuBar()
        self.create_employee_menus()
        QMessageBox.information(self, "Bienvenido", "Has iniciado sesión como Empleado")

    def create_admin_menus(self):
        file_menu = self.menu_bar.addMenu("Archivo")
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        logout_action = QAction("Cerrar Sesión", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        entities_menu = self.menu_bar.addMenu("Entidades")
        manage_branches_action = QAction("Gestionar Sucursales", self)
        manage_branches_action.triggered.connect(self.show_branch_management)
        entities_menu.addAction(manage_branches_action)

        manage_employees_action = QAction("Gestionar Empleados", self)
        manage_employees_action.triggered.connect(self.show_employee_management)
        entities_menu.addAction(manage_employees_action)

        manage_users_action = QAction("Gestionar Usuarios", self)
        manage_users_action.triggered.connect(self.show_user_management)
        entities_menu.addAction(manage_users_action)

        manage_loans_action = QAction("Gestionar Prestamos", self)
        manage_loans_action.triggered.connect(self.show_loans_management)
        entities_menu.addAction(manage_loans_action)

        transactions_menu = self.menu_bar.addMenu("Transacciones")
        loan_request_action = QAction("Solicitudes de Préstamo", self)
        loan_request_action.triggered.connect(self.show_loan_request_management)
        transactions_menu.addAction(loan_request_action)

        loan_payments_action = QAction("Pagos", self)
        loan_payments_action.triggered.connect(self.show_payment_management)
        transactions_menu.addAction(loan_payments_action)

        reports_menu = self.menu_bar.addMenu("Reportes y Consultas")
        morosos_report_action = QAction("Reporte de Morosos", self)
        morosos_report_action.triggered.connect(self.generate_morosos_report)
        reports_menu.addAction(morosos_report_action)

        session_logs_action = QAction("Logs de Sesion", self)
        session_logs_action.triggered.connect(self.show_log_management)
        reports_menu.addAction(session_logs_action)

    def create_treasury_menus(self):
        file_menu = self.menu_bar.addMenu("Archivo")
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        logout_action = QAction("Cerrar Sesión", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        entities_menu = self.menu_bar.addMenu("Entidades")
        manage_branches_action = QAction("Gestionar Sucursales", self)
        manage_branches_action.triggered.connect(self.show_branch_management)
        entities_menu.addAction(manage_branches_action)

        manage_employees_action = QAction("Gestionar Empleados", self)
        manage_employees_action.triggered.connect(self.show_employee_management)
        entities_menu.addAction(manage_employees_action)

        manage_loans_action = QAction("Gestionar Prestamos", self)
        manage_loans_action.triggered.connect(self.show_loans_management)
        entities_menu.addAction(manage_loans_action)

        transactions_menu = self.menu_bar.addMenu("Transacciones")
        loan_request_action = QAction("Solicitudes de Préstamo", self)
        loan_request_action.triggered.connect(self.show_loan_request_management)
        transactions_menu.addAction(loan_request_action)

        loan_payments_action = QAction("Pagos", self)
        loan_payments_action.triggered.connect(self.show_payment_management)
        transactions_menu.addAction(loan_payments_action)


    def create_employee_menus(self):
        file_menu = self.menu_bar.addMenu("Archivo")
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        logout_action = QAction("Cerrar Sesión", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        entities_menu = self.menu_bar.addMenu("Entidades")
        manage_loans_action = QAction("Gestionar Prestamos", self)
        manage_loans_action.triggered.connect(self.show_loans_empleado_management)
        entities_menu.addAction(manage_loans_action)

        transactions_menu = self.menu_bar.addMenu("Transacciones")
        loan_request_action = QAction("Solicitudes de Préstamo", self)
        loan_request_action.triggered.connect(self.show_loan_request_empleado_management)
        transactions_menu.addAction(loan_request_action)

        loan_payments_action = QAction("Pagos", self)
        loan_payments_action.triggered.connect(self.show_payment_empleado_management)
        transactions_menu.addAction(loan_payments_action)

    def logout(self):
        # Registrar log de salida
        self.registrar_salida()
        # Mostrar un mensaje confirmando que el usuario ha cerrado sesión
        QMessageBox.information(self, "Cierre de Sesión", "Has cerrado sesión correctamente.")
        # Cerrar la ventana principal
        self.close()  # Esto cierra la aplicación o la ventana actual
        self.login_window = LoginWindow()  # Crea una nueva instancia de la ventana de inicio de sesión
        self.login_window.show()  # Muestra la ventana de inicio de sesión

    def show_branch_management(self):
        # Limpiar el layout central antes de agregar el nuevo contenido
        self.clear_layout()

        # Crear un combobox para seleccionar la sucursal que se va a eliminar
        self.branch_combo = QComboBox()
        self.cargar_sucursal_combo()  # Cargar los códigos y nombres de las sucursales en el combobox
        self.layout.addWidget(self.branch_combo)
        
        # Campos de búsqueda
        search_layout = QHBoxLayout()

        self.search_code_input = QLineEdit()
        search_layout.addWidget(QLabel("Código:"))
        search_layout.addWidget(self.search_code_input)

        self.search_name_input = QLineEdit()
        search_layout.addWidget(QLabel("Nombre:"))
        search_layout.addWidget(self.search_name_input)

        self.search_department_input = QLineEdit()
        search_layout.addWidget(QLabel("Departamento:"))
        search_layout.addWidget(self.search_department_input)

        self.search_municipality_input = QLineEdit()
        search_layout.addWidget(QLabel("Municipio:"))
        search_layout.addWidget(self.search_municipality_input)

        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_branches)
        search_layout.addWidget(self.search_button)

        self.layout.addLayout(search_layout)

        # Crear la tabla para mostrar sucursales
        self.branch_table = QTableWidget()
        self.branch_table.setColumnCount(6)
        self.branch_table.setHorizontalHeaderLabels(["Código", "Nombre", "Departamento", "Municipio", "Director", "Presupuesto"])
        self.branch_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.branch_table)
        self.branch_table.setColumnWidth(1, 150) 

        self.load_branches()

        # Botón para abrir el formulario de nueva sucursal
        self.new_branch_button = QPushButton("Nueva Sucursal")
        self.new_branch_button.clicked.connect(self.open_new_branch_form)
        self.layout.addWidget(self.new_branch_button)

        # Botón para eliminar la sucursal seleccionada
        self.delete_branch_button = QPushButton("Eliminar Sucursal")
        self.delete_branch_button.clicked.connect(self.delete_branch)
        self.layout.addWidget(self.delete_branch_button)

    def open_new_branch_form(self):
        # Crear una nueva ventana para el formulario de sucursales
        self.branch_form_window = QWidget()
        
        self.sub_windows.append(self.branch_form_window)


        self.branch_form_window.setWindowTitle("Nueva Sucursal")
        self.branch_form_window.setGeometry(450, 200, 400, 300)

        form_layout = QFormLayout()

        self.branch_code_input = QLineEdit()
        form_layout.addRow("Código:", self.branch_code_input)

        self.branch_name_input = QLineEdit()
        self.branch_name_input.textChanged.connect(self.transform_to_uppercase_sucursal)
        form_layout.addRow("Nombre:", self.branch_name_input)

        self.department_input = QLineEdit()
        self.department_input.textChanged.connect(self.transform_to_uppercase_sucursal)
        form_layout.addRow("Departamento:", self.department_input)

        self.municipality_input = QLineEdit()
        self.municipality_input.textChanged.connect(self.transform_to_uppercase_sucursal)
        form_layout.addRow("Municipio:", self.municipality_input)

        self.director_input = QLineEdit()
        self.director_input.textChanged.connect(self.transform_to_uppercase_sucursal)
        form_layout.addRow("Director:", self.director_input)

        self.budget_input = QLineEdit()
        max_value = sys.float_info.max  # Obtener el valor máximo posible para un float en Python

        validator = QDoubleValidator(0, max_value, 2, self)  # Cambia el rango según tus necesidades
        validator.setNotation(QDoubleValidator.StandardNotation)  # Usa notación estándar
        self.budget_input.setValidator(validator)
        form_layout.addRow("Presupuesto Anual:", self.budget_input)

        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save_branch)
        form_layout.addWidget(self.save_button)

        self.branch_form_window.setLayout(form_layout)
        self.branch_form_window.show()

    def transform_to_uppercase_sucursal(self):
        # Transformar texto en ambos campos a mayúsculas
        self.branch_name_input.setText(self.branch_name_input.text().upper())
        self.department_input.setText(self.department_input.text().upper())
        self.municipality_input.setText(self.municipality_input.text().upper())
        self.director_input.setText(self.director_input.text().upper())

    def cargar_sucursal_combo(self):
        # Obtener la lista de sucursales desde el DAO
        branches = self.sucursal_dao.obtener_todas_las_sucursales()
        
        # Limpiar el combo box antes de agregar los nuevos elementos
        self.branch_combo.clear()
        
        # Agregar una opción predeterminada
        self.branch_combo.addItem("Selecciona una Sucursal", "")
        
        # Recorrer la lista de objetos SucursalDTO e insertar los datos en el combo box
        for branch in branches:
            branch_id = branch.codigo  # Asignar el código
            branch_name = branch.nombre  # Asignar el nombre
            branch_departamento = branch.departamento  # Asignar el departamento
            branch_municipio = branch.municipio  # Asignar el municipio
            
            # Agregar el elemento al combo box con el formato deseado
            display_text = f"{branch_name} - {branch_municipio} / {branch_departamento} - {branch_id}"
            self.branch_combo.addItem(display_text, branch_id)


    def load_branches(self):
        # Obtener la lista de objetos SucursalDTO desde el DAO
        branches = self.sucursal_dao.obtener_todas_las_sucursales()

        # Configurar la cantidad de filas en la tabla según el número de sucursales
        self.branch_table.setRowCount(len(branches))
        
        # Recorrer la lista de SucursalDTO e insertar los datos en la tabla
        for i, branch in enumerate(branches):
            # Asignar cada atributo de SucursalDTO a una columna
            self.branch_table.setItem(i, 0, QTableWidgetItem(str(branch.codigo)))
            self.branch_table.setItem(i, 1, QTableWidgetItem(branch.nombre))
            self.branch_table.setItem(i, 2, QTableWidgetItem(branch.departamento))
            self.branch_table.setItem(i, 3, QTableWidgetItem(branch.municipio))
            self.branch_table.setItem(i, 4, QTableWidgetItem(branch.director))
            self.branch_table.setItem(i, 5, QTableWidgetItem(str(branch.presupuesto)))

    def save_branch(self):
        code = self.branch_code_input.text()
        name = self.branch_name_input.text()
        department = self.department_input.text()
        municipality = self.municipality_input.text()
        director = self.director_input.text()
        budget = self.budget_input.text()

        if not code or not name or not department or not municipality or not director or not budget:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return

        sucursal = SucursalDTO(code, name, department, municipality, director, budget)
        try:
            self.sucursal_dao.insertar_sucursal(sucursal)
            QMessageBox.information(self, "Éxito", "Sucursal guardada correctamente")
            self.branch_form_window.close()
            self.load_branches()  # Recargar la tabla
            self.cargar_sucursal_combo()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar la sucursal: {str(e)}")

    def delete_branch(self):
        selected_code = self.branch_combo.currentData()
        if selected_code:
            confirm = QMessageBox.question(
                self, "Confirmar Eliminación", 
                f"¿Está seguro de que desea eliminar el empleado con código {selected_code}?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                try:
                    self.sucursal_dao.eliminar_sucursal(selected_code)
                    QMessageBox.information(self, "Éxito", "Sucursal eliminada correctamente")
                    self.load_branches()
                    self.cargar_sucursal_combo()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error al eliminar la sucursal: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No se ha seleccionado ninguna Sucusal")
        
    def search_branches(self):
        code = self.search_code_input.text().strip()
        name = self.search_name_input.text().strip().upper()
        department = self.search_department_input.text().strip().upper()
        municipality = self.search_municipality_input.text().strip().upper()

        # Llamar al DAO para buscar las sucursales
        branches = self.sucursal_dao.buscar_sucursales(code, name, department, municipality)

        # Mostrar los resultados en la tabla
        self.branch_table.setRowCount(len(branches))
        for i, branch in enumerate(branches):
            # Asignar cada atributo de SucursalDTO a una columna de la tabla
            self.branch_table.setItem(i, 0, QTableWidgetItem(str(branch.codigo)))
            self.branch_table.setItem(i, 1, QTableWidgetItem(branch.nombre))
            self.branch_table.setItem(i, 2, QTableWidgetItem(branch.departamento))
            self.branch_table.setItem(i, 3, QTableWidgetItem(branch.municipio))
            self.branch_table.setItem(i, 4, QTableWidgetItem(branch.director))
            self.branch_table.setItem(i, 5, QTableWidgetItem(str(branch.presupuesto)))

        # Actualizar el ComboBox con los nuevos registros
        self.branch_combo.clear()
        self.branch_combo.addItem("Selecciona una Sucursal", "")  # Opción predeterminada
        for branch in branches:
            # Acceder directamente a los atributos de SucursalDTO
            branch_id = branch.codigo
            branch_name = branch.nombre
            branch_departamento = branch.departamento
            branch_municipio = branch.municipio
            # Formatear y añadir el elemento al ComboBox
            self.branch_combo.addItem(f"{branch_name}-{branch_municipio}/{branch_departamento}-{branch_id}", branch_id)

    def show_employee_management(self):
        # Limpiar el layout central antes de agregar el nuevo contenido
        self.clear_layout()

        # Crear un combobox para seleccionar el empleado que se va a eliminar
        self.employee_combo = QComboBox()
        self.cargar_empleados_combo()  # Cargar los códigos y nombres de los empleados en el combobox
        self.layout.addWidget(self.employee_combo)

        # Crear el formulario de búsqueda
        search_layout = QHBoxLayout()

        # Campos de búsqueda
        self.search_id_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Cambia el rango según tus necesidades
        self.search_id_input.setValidator(validator)

        search_layout.addWidget(QLabel("ID Empleado:"))
        search_layout.addWidget(self.search_id_input)

        self.search_name_input = QLineEdit()
        search_layout.addWidget(QLabel("Nombre:"))
        search_layout.addWidget(self.search_name_input)

        self.search_lastname_input = QLineEdit()
        search_layout.addWidget(QLabel("Apellido:"))
        search_layout.addWidget(self.search_lastname_input)

        self.search_branch_input = QLineEdit()
        search_layout.addWidget(QLabel("Código Sucursal:"))
        search_layout.addWidget(self.search_branch_input)

        self.search_position_combo = QComboBox()
        self.search_position_combo.addItems(["", "OPERARIO", "ADMINISTRATIVO", "EJECUTIVO", "OTROS"])
        search_layout.addWidget(QLabel("Puesto:"))
        search_layout.addWidget(self.search_position_combo)

        # Botón para buscar empleados
        self.search_employee_button = QPushButton("Buscar")
        self.search_employee_button.clicked.connect(self.search_employees)
        search_layout.addWidget(self.search_employee_button)

        self.layout.addLayout(search_layout)

        # Crear la tabla para mostrar empleados
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(6)
        self.employee_table.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Sucursal", "Puesto", "Salario"])
        self.employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.employee_table)



        self.load_employees()

        # Botón para abrir el formulario de nuevo empleado
        self.new_employee_button = QPushButton("Nuevo Empleado")
        self.new_employee_button.clicked.connect(self.open_new_employee_form)
        self.layout.addWidget(self.new_employee_button)

        # Botón para eliminar el empleado seleccionado
        self.delete_employee_button = QPushButton("Eliminar Empleado")
        self.delete_employee_button.clicked.connect(self.delete_employee)
        self.layout.addWidget(self.delete_employee_button)

    def load_employees(self):
        # Cargar empleados desde la base de datos usando EmpleadoDAO
        empleados = self.empleado_dao.obtener_todos_los_empleados()
        
        self.employee_table.setRowCount(len(empleados))
        for i, empleado in enumerate(empleados):
            self.employee_table.setItem(i, 0, QTableWidgetItem(str(empleado.id_empleado)))
            self.employee_table.setItem(i, 1, QTableWidgetItem(empleado.nombre))
            self.employee_table.setItem(i, 2, QTableWidgetItem(empleado.apellido))
            self.employee_table.setItem(i, 3, QTableWidgetItem(str(empleado.sucursal_codigo)))
            self.employee_table.setItem(i, 4, QTableWidgetItem(empleado.puesto))
            self.employee_table.setItem(i, 5, QTableWidgetItem(str(empleado.salario)))

    def open_new_employee_form(self):
        # Crear una nueva ventana para el formulario de empleados
        self.employee_form_window = QWidget()
        self.sub_windows.append(self.employee_form_window)

        self.employee_form_window.setWindowTitle("Nuevo Empleado")
        self.employee_form_window.setGeometry(450, 200, 400, 300)

        form_layout = QFormLayout()

        # ComboBox para seleccionar empleado
        self.branch_combo = QComboBox()
        self.cargar_sucursal_combo()  # Cargar empleados al ComboBox
        form_layout.addRow("Sucursal:", self.branch_combo)

        self.employee_id_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Cambia el rango según tus necesidades
        self.employee_id_input.setValidator(validator)
        form_layout.addRow("ID Empleado:", self.employee_id_input)

        self.employee_name_input = QLineEdit()
        self.employee_name_input.textChanged.connect(self.transform_to_uppercase_empleado)
        form_layout.addRow("Nombre:", self.employee_name_input)

        self.employee_lastname_input = QLineEdit()
        self.employee_lastname_input.textChanged.connect(self.transform_to_uppercase_empleado)
        form_layout.addRow("Apellido:", self.employee_lastname_input)


        # Cambiar el campo de Puesto a un QComboBox
        self.position_combo = QComboBox()
        self.position_combo.addItem("Seleccione un Puesto")
        self.position_combo.addItems(["OPERARIO", "ADMINISTRATIVO", "EJECUTIVO", "OTROS"])
        self.position_combo.currentIndexChanged.connect(self.update_salary)
        form_layout.addRow("Puesto:", self.position_combo)

        self.salary_input = QLineEdit()
        form_layout.addRow("Salario:", self.salary_input)
        self.salary_input.setReadOnly(True)  # Solo lectura ya que será automático

        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save_employee)
        form_layout.addWidget(self.save_button)

        self.employee_form_window.setLayout(form_layout)
        self.employee_form_window.show()

    def transform_to_uppercase_empleado(self):
        # Transformar texto en ambos campos a mayúsculas
        self.employee_name_input.setText(self.employee_name_input.text().upper())
        self.employee_lastname_input.setText(self.employee_lastname_input.text().upper())

    def cargar_empleados_combo(self):
        # Obtener la lista de empleados desde el DAO
        empleados = self.empleado_dao.obtener_todos_los_empleados()
        
        # Limpiar el combo box antes de agregar los nuevos elementos
        self.employee_combo.clear()
        
        # Agregar una opción predeterminada
        self.employee_combo.addItem("Selecciona un empleado", "")
        
        # Recorrer la lista de objetos EmpleadoDTO e insertar los datos en el combo box
        for empleado in empleados:
            empleado_id = empleado.id_empleado  # Asignar el ID
            empleado_nombre = empleado.nombre  # Asignar el nombre
            empleado_apellido = empleado.apellido  # Asignar el apellido
            
            # Agregar el elemento al combo box con el formato deseado
            display_text = f"{empleado_nombre} {empleado_apellido} - {empleado_id}"
            self.employee_combo.addItem(display_text, empleado_id)

    def update_salary(self):
    # Obtener el puesto seleccionado y actualizar el salario automáticamente
        position = self.position_combo.currentText()
        max_salary = SALARY_RANGES.get(position, 0)

        # Formatear el salario para que use solo el punto como separador decimal
        formatted_salary = f"{max_salary}"
        
        self.salary_input.setText(formatted_salary)


    def save_employee(self):
        branch_id = self.branch_combo.currentData()  # Obtener el ID del empleado seleccionado
        emp_id = self.employee_id_input.text()
        name = self.employee_name_input.text()
        lastname = self.employee_lastname_input.text()
        position = self.position_combo.currentText()
        salary = self.salary_input.text()


        if not emp_id or not name or not lastname or not branch_id or position == "Seleccione un Puesto" or not salary:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        
        if not emp_id.isdigit():
            QMessageBox.warning(self, "Error", "El ID del Empleado debe ser un número")
            return
        
        empleado = EmpleadoDTO(emp_id, name, lastname, branch_id, position, salary)
    
        # Conectar a la base de datos y guardar el empleado
        
        try:
            bandera = self.empleado_dao.insertar_empleado(empleado)
            if bandera:
                QMessageBox.information(self, "Éxito", "Empleado guardado correctamente")
                self.employee_form_window.close()
                self.load_employees()  # Recargar la tabla
                self.cargar_empleados_combo()  # Recargar el combobox
            else:
                self.employee_form_window.close()
                QMessageBox.warning(self, "Error", "El Empleado ya existe")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar el empleado: {str(e)}")

    def delete_employee(self):
        # Método para eliminar el empleado seleccionada
        selected_code = self.employee_combo.currentData()  # Obtener el código de la sucursal seleccionada

        if selected_code:
            confirm = QMessageBox.question(
                self, "Confirmar Eliminación", 
                f"¿Está seguro de que desea eliminar el empleado con código {selected_code}?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                try:
                    self.empleado_dao.eliminar_empleado(selected_code)
                    QMessageBox.information(self, "Éxito", "Empleado eliminado correctamente")
                    self.load_employees()  # Recargar la tabla
                    self.cargar_empleados_combo()  # Recargar el combobox
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error al eliminar El Empleado: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No se ha seleccionado ningun Empleado")

    def search_employees(self):
        # Obtener los parámetros de búsqueda
        emp_id = self.search_id_input.text().strip()
        name = self.search_name_input.text().strip().upper()
        lastname = self.search_lastname_input.text().strip().upper()
        branch_code = self.search_branch_input.text().strip().upper()
        position = self.search_position_combo.currentText()

        employees = self.empleado_dao.buscar_empleados(emp_id, name, lastname, branch_code, position)
        self.employee_table.setRowCount(len(employees))
        for i, employee in enumerate(employees):
            # Asignar cada atributo de SucursalDTO a una columna de la tabla
            self.employee_table.setItem(i, 0, QTableWidgetItem(str(employee.id_empleado)))
            self.employee_table.setItem(i, 1, QTableWidgetItem(employee.nombre))
            self.employee_table.setItem(i, 2, QTableWidgetItem(employee.apellido))
            self.employee_table.setItem(i, 3, QTableWidgetItem(employee.sucursal_codigo))
            self.employee_table.setItem(i, 4, QTableWidgetItem(employee.puesto))
            self.employee_table.setItem(i, 5, QTableWidgetItem(str(employee.salario)))

        # Actualizar el ComboBox con los nuevos registros
        self.employee_combo.clear()
        self.employee_combo.addItem("Selecciona un empleado", "")  # Opción predeterminada
        for employee in employees:
            # Acceder directamente a los atributos de SucursalDTO
            emp_id = employee.id_empleado
            emp_name = employee.nombre
            emp_lastname = employee.apellido
            # Formatear y añadir el elemento al ComboBox
            self.employee_combo.addItem(f"{emp_name} {emp_lastname} - {emp_id}", emp_id)


    def show_user_management(self):
        self.clear_layout()
        
        # Crear un combobox para seleccionar el empleado que se va a eliminar
        self.user_combo = QComboBox()
        self.cargar_usuarios_combo()  # Cargar los códigos y nombres de los empleados en el combobox
        self.layout.addWidget(self.user_combo)

        # Crear el formulario de búsqueda
        search_layout = QHBoxLayout()

        # Campos de búsqueda
        self.search_id_empleado_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Cambia el rango según tus necesidades
        self.search_id_empleado_input.setValidator(validator)

        search_layout.addWidget(QLabel("ID Empleado:"))
        search_layout.addWidget(self.search_id_empleado_input)

        self.search_name_input = QLineEdit()
        search_layout.addWidget(QLabel("Nombre de Usuario:"))
        search_layout.addWidget(self.search_name_input)

        self.search_email_input = QLineEdit()
        search_layout.addWidget(QLabel("Email:"))
        search_layout.addWidget(self.search_email_input)

        self.search_rol_combo = QComboBox()
        self.search_rol_combo.addItems(["", "PRINCIPAL", "TESORERIA", "EMPLEADO"])
        search_layout.addWidget(QLabel("Rol:"))
        search_layout.addWidget(self.search_rol_combo)

        # Botón para buscar usuarios
        self.search_usuario_button = QPushButton("Buscar")
        self.search_usuario_button.clicked.connect(self.search_users)
        search_layout.addWidget(self.search_usuario_button)

        self.layout.addLayout(search_layout)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)  # Actualizar el número de columnas
        self.user_table.setHorizontalHeaderLabels(["ID Empleado", "Nombre de Usuario", "Email", "Rol"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.user_table)

        self.load_users()

        self.new_user_button = QPushButton("Nuevo Usuario")
        self.new_user_button.clicked.connect(self.open_new_user_form)
        self.layout.addWidget(self.new_user_button)

        # Botón para eliminar el empleado seleccionado
        self.delete_user_button = QPushButton("Eliminar Usuario")
        self.delete_user_button.clicked.connect(self.delete_user)
        self.layout.addWidget(self.delete_user_button)

    def load_users(self):
        
        usuarios = self.usuario_dao.obtener_todas_los_usuarios()
        # Configurar la tabla
        self.user_table.setRowCount(len(usuarios))
        for i, usuario in enumerate(usuarios):
            self.user_table.setItem(i, 0, QTableWidgetItem(str(usuario.id_empleado)))
            self.user_table.setItem(i, 1, QTableWidgetItem(usuario.nombre_usuario))
            self.user_table.setItem(i, 2, QTableWidgetItem(usuario.email))
            self.user_table.setItem(i, 3, QTableWidgetItem(usuario.rol))

    def open_new_user_form(self):
        self.user_form_window = QWidget()
        self.sub_windows.append(self.user_form_window)

        self.user_form_window.setWindowTitle("Nuevo Usuario")
        self.user_form_window.setGeometry(450, 200, 400, 300)

        form_layout = QFormLayout()

        # ComboBox para seleccionar empleado
        self.employee_combo = QComboBox()
        self.cargar_empleados_combo()  # Cargar empleados al ComboBox
        form_layout.addRow("Empleado:", self.employee_combo)

        self.username_input = QLineEdit()
        form_layout.addRow("Nombre de Usuario:", self.username_input)

        self.email_input = QLineEdit()
        self.email_input.textChanged.connect(self.transform_to_uppercase_usuario)
        form_layout.addRow("Email:", self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Contraseña:", self.password_input)

        self.role_combo = QComboBox()
        self.role_combo.addItem("Seleccione un Rol")
        self.role_combo.addItems(["TESORERIA", "EMPLEADO"])
        form_layout.addRow("Rol:", self.role_combo)

        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save_user)
        form_layout.addWidget(self.save_button)

        self.user_form_window.setLayout(form_layout)
        self.user_form_window.show()

    def transform_to_uppercase_usuario(self):
        # Transformar texto en ambos campos a mayúsculas
        self.email_input.setText(self.email_input.text().upper())

    def cargar_usuarios_combo(self):
        usuarios = self.usuario_dao.obtener_todas_los_usuarios()

        self.user_combo.clear()
        self.user_combo.addItem("Seleccionar un Usuario", "")  # Opción predeterminada
        # Recorrer la lista de objetos EmpleadoDTO e insertar los datos en el combo box
        for usuario in usuarios:
            usuario_id = usuario.id_empleado  # Asignar el ID
            usuario_nombre = usuario.nombre_usuario  # Asignar el nombre
            usuario_email = usuario.email  # Asignar el apellido
            usuario_rol = usuario.rol

            # Agregar el elemento al combo box con el formato deseado
            display_text = f"{usuario_email}-{usuario_nombre}-{usuario_rol}-{usuario_id}"
            self.user_combo.addItem(display_text, usuario_id)

    def save_user(self):
        user_id = self.employee_combo.currentData()  # Obtener el ID del empleado seleccionado
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        role = self.role_combo.currentText()

        if not user_id or not username or not email or not password or role == "Seleccione un Rol":
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        
        password_encrypted = self.hash_password(password)

        usuario = UsuarioDTO(user_id, username.upper(), email, password_encrypted, role)

        try:
            bandera = self.usuario_dao.insertar_usuario(usuario)

            if bandera:
                QMessageBox.information(self, "Éxito", "Usuario guardado correctamente")
                self.user_form_window.close()
                self.load_users()
                self.cargar_usuarios_combo()
            else:
                self.user_form_window.close()
                QMessageBox.warning(self, "Error", "El Empleado ya tiene un Usuario")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar el usuario: {str(e)}")
            
    def delete_user(self):
        # Método para eliminar el usuario seleccionado
        selected_code = self.user_combo.currentData()  # Obtener el código del usuario seleccionado

        if selected_code:
            confirm = QMessageBox.question(
                self, "Confirmar Eliminación", 
                f"¿Está seguro de que desea eliminar el usuario con código {selected_code}?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                try:
                    self.usuario_dao.eliminar_usuario(selected_code)
                    QMessageBox.information(self, "Éxito", "Usuario eliminado correctamente")
                    self.load_users()  # Recargar la tabla
                    self.cargar_usuarios_combo()  # Recargar el combobox
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error al eliminar El Usuario: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No se ha seleccionado ningun Usuario")

    def search_users(self):
        emp_id = self.search_id_empleado_input.text().strip()
        name = self.search_name_input.text().strip().upper()
        email = self.search_email_input.text().strip().upper()
        rol = self.search_rol_combo.currentText()

        users = self.usuario_dao.buscar_usuarios(emp_id, name, email, rol)
        self.user_table.setRowCount(len(users))
        for i, usuario in enumerate(users):
            # Asignar cada atributo de SucursalDTO a una columna de la tabla
            self.user_table.setItem(i, 0, QTableWidgetItem(str(usuario.id_empleado)))
            self.user_table.setItem(i, 1, QTableWidgetItem(usuario.nombre_usuario))
            self.user_table.setItem(i, 2, QTableWidgetItem(usuario.email))
            self.user_table.setItem(i, 3, QTableWidgetItem(usuario.rol))
            

        # Actualizar el ComboBox con los nuevos registros
        self.user_combo.clear()
        self.user_combo.addItem("Selecciona un Usuario", "")  # Opción predeterminada
        for usuario in users:
            # Acceder directamente a los atributos de SucursalDTO
            usuario_id = usuario.id_empleado
            usuario_nombre = usuario.nombre_usuario
            usuario_email = usuario.email
            usuario_rol = usuario.rol
            # Formatear y añadir el elemento al ComboBox
            self.user_combo.addItem(f"{usuario_email}-{usuario_nombre}-{usuario_rol}-{usuario_id}", usuario_id)
    
    def hash_password(self, password):
        # Crear un objeto hash SHA-256
        sha256 = hashlib.sha256()
        # Actualizar el objeto hash con la contraseña en bytes
        sha256.update(password.encode('utf-8'))
        # Obtener el hash en formato hexadecimal
        return sha256.hexdigest()
    
    def show_loan_request_management(self):
        # Limpiar el layout central antes de agregar el nuevo contenido
        self.clear_layout()

        # Crear un combobox para seleccionar los préstamos
        self.loan_request_combo = QComboBox()
        self.cargar_solicitudes_prestamos_combo()
        self.layout.addWidget(self.loan_request_combo)

        # Combobox para seleccionar el estado
        self.status_combo = QComboBox()
        self.status_combo.addItem("Seleccionar el Estado de la Solicitud", "")  # Opción predeterminada
        self.status_combo.addItems(["APROBADA", "CANCELADA", "NO_APROBADA", "EN_ESTUDIO"])
        self.layout.addWidget(self.status_combo)

        # Campos de búsqueda
        search_layout = QHBoxLayout()

        self.search_loan_request_id_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Cambia el rango según tus necesidades
        self.search_loan_request_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Solicitud:"))
        search_layout.addWidget(self.search_loan_request_id_input)

        self.search_employee_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Cambia el rango según tus necesidades
        self.search_employee_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Empleado:"))
        search_layout.addWidget(self.search_employee_input)

        self.search_estado_combo = QComboBox()
        self.search_estado_combo.addItems(["", "PENDIENTE", "APROBADA", "CANCELADA", "NO_APROBADA"])
        search_layout.addWidget(QLabel("Estado:"))
        search_layout.addWidget(self.search_estado_combo)

       # Campo de selección de fecha de inicio
        self.start_date_checkbox = QCheckBox("Usar Fecha Inicio")
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setEnabled(False)  # Deshabilitar campo inicialmente
        self.start_date_checkbox.toggled.connect(self.start_date_input.setEnabled)
        search_layout.addWidget(self.start_date_checkbox)
        search_layout.addWidget(self.start_date_input)

        # Campo de selección de fecha de fin
        self.end_date_checkbox = QCheckBox("Usar Fecha Fin")
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setEnabled(False)  # Deshabilitar campo inicialmente
        self.end_date_checkbox.toggled.connect(self.end_date_input.setEnabled)
        search_layout.addWidget(self.end_date_checkbox)
        search_layout.addWidget(self.end_date_input)

        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_loan_requests)
        search_layout.addWidget(self.search_button)

        self.layout.addLayout(search_layout)

        # Crear la tabla para mostrar solicitudes de préstamos
        self.loan_request_table = QTableWidget()
        self.loan_request_table.setColumnCount(7)
        self.loan_request_table.setHorizontalHeaderLabels(["ID", "ID Empleado", "Monto", "Periodo", "Interés", "Fecha Solicitud", "Estado", "Fecha Vencimiento"])
        self.loan_request_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.loan_request_table)

        self.load_loan_requests()

        # Botón para aceptar cambios
        self.accept_button = QPushButton("Aceptar")
        self.accept_button.clicked.connect(self.accept_changes)
        self.layout.addWidget(self.accept_button)

    def load_loan_requests(self):

        solicitudes_prestamos = self.solicitud_prestamo_dao.cargar_todas_las_solicitudes_prestamos()
        self.loan_request_table.setRowCount(len(solicitudes_prestamos))
        for i, solicitud in enumerate(solicitudes_prestamos):
            self.loan_request_table.setItem(i, 0, QTableWidgetItem(str(solicitud.id)))
            self.loan_request_table.setItem(i, 1, QTableWidgetItem(str(solicitud.id_empleado)))
            self.loan_request_table.setItem(i, 2, QTableWidgetItem(str(solicitud.monto)))
            self.loan_request_table.setItem(i, 3, QTableWidgetItem(str(solicitud.periodo)))
            self.loan_request_table.setItem(i, 4, QTableWidgetItem(str(solicitud.interes)))
            self.loan_request_table.setItem(i, 5, QTableWidgetItem(str(solicitud.fecha_solicitud)))
            self.loan_request_table.setItem(i, 6, QTableWidgetItem(solicitud.estado))

    def cargar_solicitudes_prestamos_combo(self):
        
        solicitudes_prestamos = self.solicitud_prestamo_dao.cargar_todas_las_solicitudes_prestamos()
        self.loan_request_combo.clear()
        self.loan_request_combo.addItem("Seleccionar una Solicitud", "")  # Opción predeterminada
        for solicitud in solicitudes_prestamos:
            solicitud_id = solicitud.id  # Asignar el ID
            solicitud_estado = solicitud.estado  # Asignar el nombre            

            display_text = f"{solicitud_id} - {solicitud_estado}"
            self.loan_request_combo.addItem(display_text, solicitud_id)

        
    def search_loan_requests(self):
        loan_request_id = self.search_loan_request_id_input.text().strip()
        employee_id = self.search_employee_input.text().strip()
        estado = self.search_estado_combo.currentText()  # Obtener el texto seleccionado en el combobox
        start_date = self.start_date_input.date().toPyDate() if self.start_date_checkbox.isChecked() else None
        end_date = self.end_date_input.date().toPyDate() if self.end_date_checkbox.isChecked() else None

        solicitudes_prestamos = self.solicitud_prestamo_dao.buscar_solicitudes_prestamos(loan_request_id, employee_id, estado, start_date, end_date)
      
        self.loan_request_table.setRowCount(len(solicitudes_prestamos))
        for i, solicitud in enumerate(solicitudes_prestamos):
                self.loan_request_table.setItem(i, 0, QTableWidgetItem(str(solicitud.id)))
                self.loan_request_table.setItem(i, 1, QTableWidgetItem(str(solicitud.id_empleado)))
                self.loan_request_table.setItem(i, 2, QTableWidgetItem(str(solicitud.monto)))
                self.loan_request_table.setItem(i, 3, QTableWidgetItem(str(solicitud.periodo)))
                self.loan_request_table.setItem(i, 4, QTableWidgetItem(str(solicitud.interes)))
                self.loan_request_table.setItem(i, 5, QTableWidgetItem(str(solicitud.fecha_solicitud)))
                self.loan_request_table.setItem(i, 6, QTableWidgetItem(solicitud.estado))

        self.loan_request_combo.clear()
        self.loan_request_combo.addItem("Seleccionar una Solicitud", "")  # Opción predeterminada
        for solicitud in solicitudes_prestamos:
            solicitud_id = solicitud.id
            solicitud_estado = solicitud.estado
            self.loan_request_combo.addItem(f"{solicitud_id} - {solicitud_estado}", solicitud_id)


    def accept_changes(self):
        # Método para aceptar los cambios (aprobar, cancelar, no aprobado)
        selected_request_id = self.loan_request_combo.currentData()
        new_status = self.status_combo.currentText()

        if not selected_request_id:
            QMessageBox.warning(self, "Error", "No se ha seleccionado ninguna solicitud")
            return

        if new_status == "Seleccionar el Estado de la Solicitud":
            QMessageBox.warning(self, "Error", "Debe seleccionar un estado")
            return

        try:
            # Obtener el estado actual de la solicitud
            solicitud = self.solicitud_prestamo_dao.cargar_solicitud_por_id(selected_request_id)
            if not solicitud:
                QMessageBox.warning(self, "Error", "La solicitud no existe")
                return

            current_status = solicitud.estado
            monto = solicitud.monto
            periodo = solicitud.periodo
            interes = solicitud.interes

            if new_status == "APROBADA":
                if current_status != "PENDIENTE":
                    QMessageBox.warning(self, "Error", "Solo se pueden aprobar solicitudes pendientes")
                    return
                # Calcular la fecha de vencimiento sumando el periodo a la fecha de aprobación
                fecha_aprobacion = QDateTime.currentDateTime().toPyDateTime()
                fecha_vencimiento = fecha_aprobacion + timedelta(days=periodo*30)
                
                #Actualizar la fehca de vencimiento cuando se apruba la solciitud mas los meses del periodo
                self.solicitud_prestamo_dao.actualizar_estado_solicitud(selected_request_id, new_status)

                monto_total = monto + monto * (interes / 100)

                # Crear el registro en la tabla Prestamo
                prestamo = PrestamoSqlDTO(0, selected_request_id, fecha_aprobacion, fecha_vencimiento, monto_total, "")
                self.prestamo_dao.insertar_prestamo(prestamo)

            elif new_status == "CANCELADA":
                if current_status != "APROBADA":
                    QMessageBox.warning(self, "Error", "Solo se pueden cancelar solicitudes aprobadas")
                    return

                self.solicitud_prestamo_dao.cancelar_solicitud_prestamo_por_id(selected_request_id)
                self.prestamo_dao.cancelar_prestamo_por_id_solicitud(selected_request_id)

            elif new_status == "EN_ESTUDIO":
                if current_status != "PENDIENTE":
                    QMessageBox.warning(self, "Error", "Solo se pueden estudiar solicitudes pendientes")
                    return
                # Actualizar el estado a "NO_APROBADA"
                self.solicitud_prestamo_dao.actualizar_estado_solicitud(selected_request_id, new_status)

            elif new_status == "NO_APROBADA":
                if current_status != "PENDIENTE":
                    QMessageBox.warning(self, "Error", "Solo se pueden rechazar solicitudes pendientes")
                    return
                # Actualizar el estado a "NO_APROBADA"
                self.solicitud_prestamo_dao.actualizar_estado_solicitud(selected_request_id, new_status)

            QMessageBox.information(self, "Éxito", "Estado actualizado correctamente")
            self.load_loan_requests()  # Recargar la tabla
            self.cargar_solicitudes_prestamos_combo()  # Recargar el combobox

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al actualizar el estado: {str(e)}")
      
    def show_loan_request_empleado_management(self):
        # Limpiar el layout central antes de agregar el nuevo contenido
        self.clear_layout()

        # Campos de búsqueda
        search_layout = QHBoxLayout()

        self.search_loan_request_id_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Cambia el rango según tus necesidades
        self.search_loan_request_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Solicitud:"))
        search_layout.addWidget(self.search_loan_request_id_input)

        self.search_estado_combo = QComboBox()
        self.search_estado_combo.addItems(["", "PENDIENTE", "APROBADA", "CANCELADA", "NO_APROBADA"])
        search_layout.addWidget(QLabel("Estado:"))
        search_layout.addWidget(self.search_estado_combo)

       # Campo de selección de fecha de inicio
        self.start_date_checkbox = QCheckBox("Usar Fecha Inicio")
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setEnabled(False)  # Deshabilitar campo inicialmente
        self.start_date_checkbox.toggled.connect(self.start_date_input.setEnabled)
        search_layout.addWidget(self.start_date_checkbox)
        search_layout.addWidget(self.start_date_input)

        # Campo de selección de fecha de fin
        self.end_date_checkbox = QCheckBox("Usar Fecha Fin")
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setEnabled(False)  # Deshabilitar campo inicialmente
        self.end_date_checkbox.toggled.connect(self.end_date_input.setEnabled)
        search_layout.addWidget(self.end_date_checkbox)
        search_layout.addWidget(self.end_date_input)

        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_loan_requests_empleado)
        search_layout.addWidget(self.search_button)

        self.layout.addLayout(search_layout)

        # Crear la tabla para mostrar solicitudes de préstamos
        self.loan_request_table = QTableWidget()
        self.loan_request_table.setColumnCount(7)
        self.loan_request_table.setHorizontalHeaderLabels(["ID", "ID Empleado", "Monto", "Periodo", "Interés", "Fecha Solicitud", "Estado", "Fecha Vencimiento"])
        self.loan_request_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.loan_request_table)

        self.load_loan_requests_empleado()

        # Botón para aceptar cambios
        self.accept_button = QPushButton("Crear Solicitud")
        self.accept_button.clicked.connect(self.open_new_loan_request_employee_form)
        self.layout.addWidget(self.accept_button)

    def load_loan_requests_empleado(self):

        solicitudes_prestamos = self.solicitud_prestamo_dao.cargar_solicitudes_prestamos_por_id_empleado(self.usuario.id_empleado)
        self.loan_request_table.setRowCount(len(solicitudes_prestamos))
        for i, solicitud in enumerate(solicitudes_prestamos):
            self.loan_request_table.setItem(i, 0, QTableWidgetItem(str(solicitud.id)))
            self.loan_request_table.setItem(i, 1, QTableWidgetItem(str(solicitud.id_empleado)))
            self.loan_request_table.setItem(i, 2, QTableWidgetItem(str(solicitud.monto)))
            self.loan_request_table.setItem(i, 3, QTableWidgetItem(str(solicitud.periodo)))
            self.loan_request_table.setItem(i, 4, QTableWidgetItem(str(solicitud.interes)))
            self.loan_request_table.setItem(i, 5, QTableWidgetItem(str(solicitud.fecha_solicitud)))
            self.loan_request_table.setItem(i, 6, QTableWidgetItem(solicitud.estado))
        
    def search_loan_requests_empleado(self):
        loan_request_id = self.search_loan_request_id_input.text().strip()
        employee_id = self.usuario.id_empleado
        estado = self.search_estado_combo.currentText()  # Obtener el texto seleccionado en el combobox
        start_date = self.start_date_input.date().toPyDate() if self.start_date_checkbox.isChecked() else None
        end_date = self.end_date_input.date().toPyDate() if self.end_date_checkbox.isChecked() else None

        solicitudes_prestamos = self.solicitud_prestamo_dao.buscar_solicitudes_prestamos(loan_request_id, employee_id, estado, start_date, end_date)
      
        self.loan_request_table.setRowCount(len(solicitudes_prestamos))
        for i, solicitud in enumerate(solicitudes_prestamos):
                self.loan_request_table.setItem(i, 0, QTableWidgetItem(str(solicitud.id)))
                self.loan_request_table.setItem(i, 1, QTableWidgetItem(str(solicitud.id_empleado)))
                self.loan_request_table.setItem(i, 2, QTableWidgetItem(str(solicitud.monto)))
                self.loan_request_table.setItem(i, 3, QTableWidgetItem(str(solicitud.periodo)))
                self.loan_request_table.setItem(i, 4, QTableWidgetItem(str(solicitud.interes)))
                self.loan_request_table.setItem(i, 5, QTableWidgetItem(str(solicitud.fecha_solicitud)))
                self.loan_request_table.setItem(i, 6, QTableWidgetItem(solicitud.estado))

    def open_new_loan_request_employee_form(self):
        self.loan_request_employee_form = QWidget()
        self.sub_windows.append(self.loan_request_employee_form)

        self.loan_request_employee_form.setWindowTitle("Nueva Solicitud de Préstamo")
        self.loan_request_employee_form.setGeometry(450, 200, 400, 200)

        form_layout = QFormLayout()

        # Campo para monto del préstamo
        self.amount_input = QLineEdit()
        amount_validator = QDoubleValidator(0.0, 1e6, 2, self)
        self.amount_input.setValidator(amount_validator)
        form_layout.addRow("Monto:", self.amount_input)

        # Campo para período en meses
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Seleccione un Período", "24", "36", "48", "60", "72"])
        self.period_combo.currentIndexChanged.connect(self.update_interest)
        form_layout.addRow("Período (meses):", self.period_combo)

        self.interest_input = QLineEdit()
        form_layout.addRow("Interes:", self.interest_input)
        self.interest_input.setReadOnly(True)  # Solo lectura ya que será automático

        # Botón para guardar la solicitud
        self.save_button = QPushButton("Guardar Solicitud")
        self.save_button.clicked.connect(self.save_loan_request)
        form_layout.addWidget(self.save_button)

        self.loan_request_employee_form.setLayout(form_layout)
        self.loan_request_employee_form.show()

    def update_interest(self):
        # Calcular el interés basado en el período
        period = self.period_combo.currentText()
        interest_rate = {
            "24": 7,
            "36": 7.5,
            "48": 8,
            "60": 8.3,
            "72": 8.6
        }.get(period, 0)
        self.interest_input.setText(f'{interest_rate}')

    def save_loan_request(self):
        monto = self.amount_input.text()
        periodo = self.period_combo.currentText()
        interes = self.interest_input.text()


        if not monto or periodo == "Seleccione un Período":
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        
        empleado = self.empleado_dao.obtener_empleado_por_id(self.usuario.id_empleado)

        if empleado.puesto == "OPERARIO":
            if float(monto) > 10000000:
                QMessageBox.warning(self, "Error", "Su Capacidad Maxima de Prestamo es de 10000000$")
                return       
        elif empleado.puesto == "ADMINISTRATIVO":
            if float(monto) > 15000000:
                QMessageBox.warning(self, "Error", "Su Capacidad Maxima de Prestamo es de 15000000$")
                return   
        elif empleado.puesto == "EJECUTIVO":
            if float(monto) > 20000000:
                QMessageBox.warning(self, "Error", "Su Capacidad Maxima de Prestamo es de 20000000$")
                return 
        else:
            if float(monto) > 12000000:
                QMessageBox.warning(self, "Error", "Su Capacidad Maxima de Prestamo es de 12000000$")
                return 

        fecha_actual = datetime.now()
        fecha_actual = fecha_actual.strftime('%d-%m-%Y %H:%M:%S')
        
        solicitud = SolicitudPrestamoDTO(0, self.usuario.id_empleado, monto, periodo, interes, fecha_actual, "PENDIENTE")    
        # Conectar a la base de datos y guardar el empleado
        
        try:
            self.solicitud_prestamo_dao.insertar_solicitud_prestamo(solicitud)
            QMessageBox.information(self, "Éxito", "Solicitud creada correctamente")
            self.loan_request_employee_form.close()
            self.load_loan_requests_empleado()  # Recargar la tabla
        except Exception as e:
            self.loan_request_employee_form.close()
            QMessageBox.warning(self, "Error", f"Error al guardar el empleado: {str(e)}")


    def show_loans_management(self):
        # Limpiar el layout central antes de agregar el nuevo contenido
        self.clear_layout()

        # Crear un combobox para seleccionar los préstamos
        self.loan_combo = QComboBox()
        self.cargar_prestamos_combo()
        self.layout.addWidget(self.loan_combo)

        # Campos de búsqueda
        search_layout = QHBoxLayout()

        self.search_loans_id_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Cambia el rango según tus necesidades
        self.search_loans_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Préstamo:"))
        search_layout.addWidget(self.search_loans_id_input)

        self.search_solicitud_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Cambia el rango según tus necesidades
        self.search_solicitud_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Solicitud:"))
        search_layout.addWidget(self.search_solicitud_input)

        self.search_employee_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Cambia el rango según tus necesidades
        self.search_employee_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Empleado:"))
        search_layout.addWidget(self.search_employee_input)

        self.search_estado_combo = QComboBox()
        self.search_estado_combo.addItems(["", "ACTIVO", "CANCELADO", "PAGADO", "MORA"])
        search_layout.addWidget(QLabel("Estado:"))
        search_layout.addWidget(self.search_estado_combo)

        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_loans)
        search_layout.addWidget(self.search_button)

        self.layout.addLayout(search_layout)

        # Crear la tabla para mostrar préstamos
        self.loan_table = QTableWidget()
        self.loan_table.setColumnCount(10)
        self.loan_table.setHorizontalHeaderLabels(["ID", "ID Solicitud", "ID Empleado", "Fecha Ultimo Pago", "Saldo Pendiente", "Saldo Acumulado", "#Pagos", "Fecha Aceptacion", "Fecha Vencimiento", "Estado"])
        self.loan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.loan_table)


        self.load_loans()

        # Botón para aceptar cambios
        self.accept_button = QPushButton("Pagar Cuota")
        self.accept_button.clicked.connect(self.pagar_cuota)
        self.layout.addWidget(self.accept_button)

    def load_loans(self):
        
        prestamos = self.prestamo_dao.cargar_todos_los_prestamos()

        self.loan_table.setRowCount(len(prestamos))
        for i, prestamo in enumerate(prestamos):
            self.loan_table.setItem(i, 0, QTableWidgetItem(str(prestamo.id)))
            self.loan_table.setItem(i, 1, QTableWidgetItem(str(prestamo.id_solicitud)))
            self.loan_table.setItem(i, 2, QTableWidgetItem(str(prestamo.id_empleado)))
            self.loan_table.setItem(i, 3, QTableWidgetItem(str(prestamo.fecha_ult_pago)))
            self.loan_table.setItem(i, 4, QTableWidgetItem(str(prestamo.saldo_pendiente)))
            self.loan_table.setItem(i, 5, QTableWidgetItem(str(prestamo.saldo_acumulado)))
            self.loan_table.setItem(i, 6, QTableWidgetItem(str(prestamo.numero_pagos)))
            self.loan_table.setItem(i, 7, QTableWidgetItem(str(prestamo.fecha_aceptacion)))
            self.loan_table.setItem(i, 8, QTableWidgetItem(str(prestamo.fecha_vencimiento)))
            self.loan_table.setItem(i, 9, QTableWidgetItem(str(prestamo.estado_prestamo)))

    def cargar_prestamos_combo(self):
        
        prestamos = self.prestamo_dao.cargar_todos_los_prestamos()
        self.loan_combo.clear()
        self.loan_combo.addItem("Seleccionar un Préstamo", "")  # Opción predeterminada
        
        for prestamo in prestamos:
            prestamo_id = prestamo.id  # Asignar el ID
            prestamo_id_solicitud = prestamo.id_solicitud  # Asignar el nombre            
            prestamo_id_empleado = prestamo.id_empleado
            prestamo_estado = prestamo.estado_prestamo

            display_text = f"{prestamo_id} - {prestamo_id_solicitud} - {prestamo_id_empleado} - {prestamo_estado}"
            self.loan_combo.addItem(display_text, prestamo_id)
        

    def search_loans(self):
        id_prestamo = self.search_loans_id_input.text()
        id_solicitud = self.search_solicitud_input.text()
        id_empleado = self.search_employee_input.text()
        estado = self.search_estado_combo.currentText()

        # Construir la consulta SQL dinámica basada en los filtros aplicados
        prestamos = self.prestamo_dao.buscar_prestamos(id_prestamo, id_solicitud, id_empleado, estado)

        # Mostrar los préstamos encontrados
        self.loan_table.setRowCount(len(prestamos))
        for i, prestamo in enumerate(prestamos):
            self.loan_table.setItem(i, 0, QTableWidgetItem(str(prestamo.id)))
            self.loan_table.setItem(i, 1, QTableWidgetItem(str(prestamo.id_solicitud)))
            self.loan_table.setItem(i, 2, QTableWidgetItem(str(prestamo.id_empleado)))
            self.loan_table.setItem(i, 3, QTableWidgetItem(str(prestamo.fecha_ult_pago)))
            self.loan_table.setItem(i, 4, QTableWidgetItem(str(prestamo.saldo_pendiente)))
            self.loan_table.setItem(i, 5, QTableWidgetItem(str(prestamo.saldo_acumulado)))
            self.loan_table.setItem(i, 6, QTableWidgetItem(str(prestamo.numero_pagos)))
            self.loan_table.setItem(i, 7, QTableWidgetItem(str(prestamo.fecha_aceptacion)))
            self.loan_table.setItem(i, 8, QTableWidgetItem(str(prestamo.fecha_vencimiento)))
            self.loan_table.setItem(i, 9, QTableWidgetItem(str(prestamo.estado_prestamo)))
            # Actualizar el ComboBox con los nuevos registros

        self.loan_combo.clear()
        self.loan_combo.addItem("Seleccionar un Préstamo", "")  # Opción predeterminada
        for prestamo in prestamos:
            prestamo_id = prestamo.id
            prestamo_id_solicitud = prestamo.id_solicitud
            prestamo_id_empleado = prestamo.id_empleado
            prestamo_estado_prestamo = prestamo.estado_prestamo
            self.loan_combo.addItem(f"{prestamo_id} - {prestamo_id_solicitud} - {prestamo_id_empleado} - {prestamo_estado_prestamo}", prestamo_id)
        

    def show_loans_empleado_management(self):
        # Limpiar el layout central antes de agregar el nuevo contenido
        self.clear_layout()

        # Crear un combobox para seleccionar los préstamos
        self.loan_combo = QComboBox()
        self.cargar_prestamos_empleado_combo()
        self.layout.addWidget(self.loan_combo)

        # Campos de búsqueda
        search_layout = QHBoxLayout()

        self.search_loans_id_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Cambia el rango según tus necesidades
        self.search_loans_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Préstamo:"))
        search_layout.addWidget(self.search_loans_id_input)

        self.search_solicitud_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Cambia el rango según tus necesidades
        self.search_solicitud_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Solicitud:"))
        search_layout.addWidget(self.search_solicitud_input)

        self.search_estado_combo = QComboBox()
        self.search_estado_combo.addItems(["", "ACTIVO", "CANCELADO", "PAGADO", "MORA"])
        search_layout.addWidget(QLabel("Estado:"))
        search_layout.addWidget(self.search_estado_combo)

        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_loans_empleado)
        search_layout.addWidget(self.search_button)

        self.layout.addLayout(search_layout)

        # Crear la tabla para mostrar préstamos
        self.loan_table = QTableWidget()
        self.loan_table.setColumnCount(10)
        self.loan_table.setHorizontalHeaderLabels(["ID", "ID Solicitud", "ID Empleado", "Fecha Ultimo Pago", "Saldo Pendiente", "Saldo Acumulado", "#Pagos", "Fecha Aceptacion", "Fecha Vencimiento", "Estado"])
        self.loan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.loan_table)


        self.load_loans_empleado()

        # Botón para aceptar cambios
        self.accept_button = QPushButton("Pagar Cuota")
        self.accept_button.clicked.connect(self.pagar_cuota)
        self.layout.addWidget(self.accept_button)

    def load_loans_empleado(self):
        
        prestamos = self.prestamo_dao.cargar_prestamos_por_empleado(self.usuario.id_empleado)

        self.loan_table.setRowCount(len(prestamos))
        for i, prestamo in enumerate(prestamos):
            self.loan_table.setItem(i, 0, QTableWidgetItem(str(prestamo.id)))
            self.loan_table.setItem(i, 1, QTableWidgetItem(str(prestamo.id_solicitud)))
            self.loan_table.setItem(i, 2, QTableWidgetItem(str(prestamo.id_empleado)))
            self.loan_table.setItem(i, 3, QTableWidgetItem(str(prestamo.fecha_ult_pago)))
            self.loan_table.setItem(i, 4, QTableWidgetItem(str(prestamo.saldo_pendiente)))
            self.loan_table.setItem(i, 5, QTableWidgetItem(str(prestamo.saldo_acumulado)))
            self.loan_table.setItem(i, 6, QTableWidgetItem(str(prestamo.numero_pagos)))
            self.loan_table.setItem(i, 7, QTableWidgetItem(str(prestamo.fecha_aceptacion)))
            self.loan_table.setItem(i, 8, QTableWidgetItem(str(prestamo.fecha_vencimiento)))
            self.loan_table.setItem(i, 9, QTableWidgetItem(str(prestamo.estado_prestamo)))

    def cargar_prestamos_empleado_combo(self):
        
        prestamos = self.prestamo_dao.cargar_prestamos_por_empleado(self.usuario.id_empleado)
        self.loan_combo.clear()
        self.loan_combo.addItem("Seleccionar un Préstamo", "")  # Opción predeterminada
        
        for prestamo in prestamos:
            prestamo_id = prestamo.id  # Asignar el ID
            prestamo_id_solicitud = prestamo.id_solicitud  # Asignar el nombre            
            prestamo_id_empleado = prestamo.id_empleado
            prestamo_estado = prestamo.estado_prestamo

            display_text = f"{prestamo_id} - {prestamo_id_solicitud} - {prestamo_id_empleado} - {prestamo_estado}"
            self.loan_combo.addItem(display_text, prestamo_id)
        

    def search_loans_empleado(self):
        id_prestamo = self.search_loans_id_input.text()
        id_solicitud = self.search_solicitud_input.text()
        id_empleado = self.usuario.id_empleado
        estado = self.search_estado_combo.currentText()

        # Construir la consulta SQL dinámica basada en los filtros aplicados
        prestamos = self.prestamo_dao.buscar_prestamos(id_prestamo, id_solicitud, id_empleado, estado)

        # Mostrar los préstamos encontrados
        self.loan_table.setRowCount(len(prestamos))
        for i, prestamo in enumerate(prestamos):
            self.loan_table.setItem(i, 0, QTableWidgetItem(str(prestamo.id)))
            self.loan_table.setItem(i, 1, QTableWidgetItem(str(prestamo.id_solicitud)))
            self.loan_table.setItem(i, 2, QTableWidgetItem(str(prestamo.id_empleado)))
            self.loan_table.setItem(i, 3, QTableWidgetItem(str(prestamo.fecha_ult_pago)))
            self.loan_table.setItem(i, 4, QTableWidgetItem(str(prestamo.saldo_pendiente)))
            self.loan_table.setItem(i, 5, QTableWidgetItem(str(prestamo.saldo_acumulado)))
            self.loan_table.setItem(i, 6, QTableWidgetItem(str(prestamo.numero_pagos)))
            self.loan_table.setItem(i, 7, QTableWidgetItem(str(prestamo.fecha_aceptacion)))
            self.loan_table.setItem(i, 8, QTableWidgetItem(str(prestamo.fecha_vencimiento)))
            self.loan_table.setItem(i, 9, QTableWidgetItem(str(prestamo.estado_prestamo)))
            # Actualizar el ComboBox con los nuevos registros

        self.loan_combo.clear()
        self.loan_combo.addItem("Seleccionar un Préstamo", "")  # Opción predeterminada
        for prestamo in prestamos:
            prestamo_id = prestamo.id
            prestamo_id_solicitud = prestamo.id_solicitud
            prestamo_id_empleado = prestamo.id_empleado
            prestamo_estado_prestamo = prestamo.estado_prestamo
            self.loan_combo.addItem(f"{prestamo_id} - {prestamo_id_solicitud} - {prestamo_id_empleado} - {prestamo_estado_prestamo}", prestamo_id)


    def calcular_pagos_pendientes(self, fecha_ultimo_pago, fecha_inicio_prestamo):
        fecha_actual = datetime.now()
        if  fecha_ultimo_pago is None or fecha_ultimo_pago == "None":
            fecha_ultimo_pago = fecha_inicio_prestamo
        else:
            fecha_ultimo_pago = datetime.strptime(fecha_ultimo_pago, '%Y-%m-%d %H:%M:%S')
        
        pagos_pendientes = 0
        
        # Fecha límite del siguiente pago: el día 10 del mes siguiente al último pago
        fecha_limite_pago_actual = datetime(fecha_ultimo_pago.year, fecha_ultimo_pago.month, 10, 12) + timedelta(days=31)
        fecha_limite_pago_actual = fecha_limite_pago_actual.replace(day=10, hour=12)
        
        while fecha_actual > fecha_limite_pago_actual:
            pagos_pendientes += 1
            
            siguiente_mes = fecha_limite_pago_actual.month + 1
            anio_siguiente = fecha_limite_pago_actual.year
            if siguiente_mes > 12:
                siguiente_mes = 1
                anio_siguiente += 1
            
            fecha_limite_pago_actual = fecha_limite_pago_actual.replace(year=anio_siguiente, month=siguiente_mes, day=10)
        
        return pagos_pendientes

    def pagar_cuota(self):
        id_prestamo_seleccionado = self.loan_combo.currentData()

        if not id_prestamo_seleccionado:
            QMessageBox.warning(self, "Error", "No se ha seleccionado ningun prestamo")
            return
        
        prestamo_detalle = self.prestamo_dao.obtener_datos_solicitud_prestamo_por_id_prestamo(id_prestamo_seleccionado)
        
        monto = prestamo_detalle.monto
        interes = prestamo_detalle.interes
        periodo = prestamo_detalle.periodo
        saldo_pendiente = prestamo_detalle.saldo_pendiente 
        estado = prestamo_detalle.estado_prestamo
        fecha_inicio = prestamo_detalle.fecha_aprobacion

        if estado in ('PAGADO', 'CANCELADO'):
            QMessageBox.information(None, "Información", f"El préstamo está {estado}. No se puede realizar el pago.")
            return

        fecha_ultimo_pago = str(self.pago_dao.obtener_fecha_ultimo_pago(id_prestamo_seleccionado))
        if fecha_ultimo_pago and fecha_ultimo_pago != "None":
            fecha_ultimo_pago_dt = datetime.strptime(fecha_ultimo_pago, '%Y-%m-%d %H:%M:%S')
            fecha_limite_pago = fecha_ultimo_pago_dt.replace(day=10) + timedelta(days=31)
            fecha_limite_pago = fecha_limite_pago.replace(day=10, hour=23, minute=59)
            # Si el último pago fue reciente y aún no ha pasado la fecha límite del próximo pago, bloquea el nuevo pago
            if datetime.now() < fecha_limite_pago:
                QMessageBox.information(None, "Información", f"Ya ha realizado el pago más reciente. El próximo pago es después del {fecha_limite_pago.strftime('%d/%m/%Y')}.")
                return
        pagos_pendientes = self.calcular_pagos_pendientes(fecha_ultimo_pago, fecha_inicio)
        cuota = (monto + (monto * (interes / 100))) / periodo
        monto_total_a_pagar = cuota * (pagos_pendientes + 1) if pagos_pendientes > 0 else cuota
        self.ventana_pago(id_prestamo_seleccionado, monto_total_a_pagar, pagos_pendientes, saldo_pendiente)


    def ventana_pago(self, id_prestamo, monto_total_a_pagar, pagos_pendientes, saldo_pendiente):
        self.ventana = QWidget()
        self.sub_windows.append(self.ventana)

        self.ventana.setWindowTitle("Pago de Préstamo")
        self.ventana.setGeometry(450, 200, 400, 300)

        layout = QVBoxLayout()

        self.label_monto_total = QLabel(f"Monto total de la cuota: {monto_total_a_pagar:.2f}")
        layout.addWidget(self.label_monto_total)

        self.label_pagos_pendientes = QLabel(f"Pagos pendientes: {pagos_pendientes}")
        layout.addWidget(self.label_pagos_pendientes)

        self.label_saldo_pendiente = QLabel(f"Saldo pendiente: {saldo_pendiente:.2f}")
        layout.addWidget(self.label_saldo_pendiente)

        self.label_monto = QLabel("Monto a pagar:")
        layout.addWidget(self.label_monto)

        self.entry_monto = QLineEdit()
        self.entry_monto.setReadOnly(True)  # Campo de solo lectura
        layout.addWidget(self.entry_monto)

        # Checkbox para "Pagar saldo completo"
        self.check_pagar_todo = QCheckBox("Pagar saldo completo")
        layout.addWidget(self.check_pagar_todo)

        # Checkbox para "Pagar cuota total"
        self.check_pagar_cuota = QCheckBox("Pagar cuota total")
        layout.addWidget(self.check_pagar_cuota)

        self.entry_monto.setReadOnly(True)  # Marcar como lectura

        # Función para manejar los checkboxes
        def actualizar_monto():
            if self.check_pagar_todo.isChecked():
                self.entry_monto.setText(f"{saldo_pendiente:.2f}")
                self.check_pagar_cuota.setDisabled(True)  # Desactivar el otro checkbox
            elif self.check_pagar_cuota.isChecked():
                self.entry_monto.setText(f"{monto_total_a_pagar:.2f}")
                self.check_pagar_todo.setDisabled(True)  # Desactivar el otro checkbox
            else:
                self.entry_monto.clear()  # Limpiar el campo si ambos están desmarcados
                self.check_pagar_todo.setDisabled(False)
                self.check_pagar_cuota.setDisabled(False)

        # Conectar los CheckBoxes a la función
        self.check_pagar_todo.stateChanged.connect(actualizar_monto)
        self.check_pagar_cuota.stateChanged.connect(actualizar_monto)

        self.label_metodo = QLabel("Método de pago:")
        layout.addWidget(self.label_metodo)

        self.entry_metodo = QLineEdit()
        layout.addWidget(self.entry_metodo)

        self.boton_pagar = QPushButton("Pagar")
        layout.addWidget(self.boton_pagar)

        # Procesar el pago
        def procesar_pago():
            try:
                monto_pagado = float(self.entry_monto.text())
                metodo_pago = self.entry_metodo.text()

                if monto_pagado <= 0:
                    QMessageBox.warning(self.ventana, "Advertencia", "El monto ingresado no es válido.")
                    return
                
                if not metodo_pago:
                    QMessageBox.warning(self.ventana, "Advertencia", "El método de pago ingresado no es válido")
                    return

                self.realizar_pago_prestamo(id_prestamo, monto_pagado, metodo_pago)
                self.ventana.close()

            except ValueError:
                QMessageBox.warning(self.ventana, "Advertencia", "Por favor ingresa un monto válido.")

        self.boton_pagar.clicked.connect(procesar_pago)

        self.ventana.setLayout(layout)
        self.ventana.show()

    def realizar_pago_prestamo(self, id_prestamo, monto_pagado, metodo_pago):
        try:
            # Obtener saldo pendiente y estado del préstamo
            prestamo = self.prestamo_dao.obtener_saldo_y_estado_prestamo(id_prestamo)
            
            if not prestamo:
                QMessageBox.critical(None, "Error", "Préstamo no encontrado.")
                return
            
            saldo_pendiente, estado = prestamo
            
            # Verificar si el préstamo está pagado o cancelado
            if estado in ('PAGADO', 'CANCELADO'):
                QMessageBox.information(None, "Información", f"El préstamo está {estado}. No se puede realizar el pago.")
                return
            
            # Calcular nuevo saldo pendiente
            saldo_pendiente -= monto_pagado
            
            # Actualizar el estado si el saldo es cero
            if saldo_pendiente <= 0:
                saldo_pendiente = 0
                estado = 'PAGADO'

            fecha_pago = datetime.now()

            pago = PagoSqlDTO(0, id_prestamo, monto_pagado, fecha_pago, metodo_pago)

            # Actualizar saldo y estado del préstamo
            if self.prestamo_dao.actualizar_saldo_y_estado_prestamo(id_prestamo, saldo_pendiente, estado):
                # Registrar el pago
                if self.pago_dao.registrar_pago(pago):
                    if self.usuario.rol == "EMPLEADO":
                        self.load_loans_empleado()
                        self.cargar_prestamos_empleado_combo()
                    else:
                        self.load_loans()
                        self.cargar_prestamos_combo()
                    QMessageBox.information(None, "Éxito", f"Pago realizado con éxito. Monto pagado: {monto_pagado:.2f}")
                else:
                    QMessageBox.critical(None, "Error", "Error al registrar el pago.")
            else:
                QMessageBox.critical(None, "Error", "Error al actualizar el préstamo.")
                
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al realizar el pago: {str(e)}")

    def show_payment_management(self):
        # Limpiar el layout central antes de agregar el nuevo contenido
        self.clear_layout()

        # Campos de búsqueda
        search_layout = QHBoxLayout()

        # ID del Pago
        self.search_payment_id_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Validar solo números enteros
        self.search_payment_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Pago:"))
        search_layout.addWidget(self.search_payment_id_input)

        # ID del Préstamo
        self.search_loan_id_input = QLineEdit()
        self.search_loan_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Préstamo:"))
        search_layout.addWidget(self.search_loan_id_input)

        # ID del Préstamo
        self.search_employee_id_input = QLineEdit()
        self.search_employee_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Empleado:"))
        search_layout.addWidget(self.search_employee_id_input)
        
        # Campo de selección de fecha de inicio de pago
        self.start_date_checkbox = QCheckBox("Usar Fecha Inicio")
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setEnabled(False)  # Deshabilitar campo inicialmente
        self.start_date_checkbox.toggled.connect(self.start_date_input.setEnabled)
        search_layout.addWidget(self.start_date_checkbox)
        search_layout.addWidget(self.start_date_input)

        # Campo de selección de fecha de fin de pago
        self.end_date_checkbox = QCheckBox("Usar Fecha Fin")
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setEnabled(False)  # Deshabilitar campo inicialmente
        self.end_date_checkbox.toggled.connect(self.end_date_input.setEnabled)
        search_layout.addWidget(self.end_date_checkbox)
        search_layout.addWidget(self.end_date_input)

        # Botón de búsqueda
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_loan_payments)
        search_layout.addWidget(self.search_button)

        # Agregar layout de búsqueda al layout principal
        self.layout.addLayout(search_layout)

        # Crear la tabla para mostrar los pagos
        self.loan_payment_table = QTableWidget()
        self.loan_payment_table.setColumnCount(6)
        self.loan_payment_table.setHorizontalHeaderLabels([
            "ID Pago", "ID Préstamo", "ID Empleado", "Monto Pagado", "Fecha de Pago", "Método de Pago"
        ])
        self.loan_payment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.loan_payment_table)



        # Cargar los registros de pagos en la tabla
        self.load_loan_payments()



    def load_loan_payments(self):
        # Obtener todos los pagos desde la base de datos
        pagos = self.pago_dao.cargar_todos_los_pagos()

        # Limpiar la tabla antes de cargar nuevos datos
        self.loan_payment_table.setRowCount(len(pagos))

        for i, pago in enumerate(pagos):
            self.loan_payment_table.setItem(i, 0, QTableWidgetItem(str(pago.id)))
            self.loan_payment_table.setItem(i, 1, QTableWidgetItem(str(pago.id_prestamo)))
            self.loan_payment_table.setItem(i, 2, QTableWidgetItem(str(pago.id_empleado)))
            self.loan_payment_table.setItem(i, 3, QTableWidgetItem(f"{pago.monto_pagado:.2f}"))
            self.loan_payment_table.setItem(i, 4, QTableWidgetItem(str(pago.fecha_pago)))
            self.loan_payment_table.setItem(i, 5, QTableWidgetItem(pago.metodo_pago))


    def search_loan_payments(self):
        # Obtener los filtros de búsqueda si los hay
        payment_id = self.search_payment_id_input.text().strip()
        loan_id = self.search_loan_id_input.text().strip()
        employee_id = self.search_employee_id_input.text().strip()
        start_date = self.start_date_input.date().toPyDate() if self.start_date_checkbox.isChecked() else None
        end_date = self.end_date_input.date().toPyDate() if self.end_date_checkbox.isChecked() else None

        # Buscar los pagos en base a los filtros
        pagos = self.pago_dao.buscar_pagos(payment_id, loan_id, employee_id, start_date, end_date)

        # Limpiar la tabla y cargar los resultados de búsqueda
        self.loan_payment_table.setRowCount(len(pagos))

        for i, pago in enumerate(pagos):
            self.loan_payment_table.setItem(i, 0, QTableWidgetItem(str(pago.id)))
            self.loan_payment_table.setItem(i, 1, QTableWidgetItem(str(pago.id_prestamo)))
            self.loan_payment_table.setItem(i, 2, QTableWidgetItem(str(pago.id_empleado)))
            self.loan_payment_table.setItem(i, 3, QTableWidgetItem(f"{pago.monto_pagado:.2f}"))
            self.loan_payment_table.setItem(i, 4, QTableWidgetItem(str(pago.fecha_pago)))
            self.loan_payment_table.setItem(i, 5, QTableWidgetItem(pago.metodo_pago))
    
    def show_payment_empleado_management(self):
        # Limpiar el layout central antes de agregar el nuevo contenido
        self.clear_layout()

        # Campos de búsqueda
        search_layout = QHBoxLayout()

        # ID del Pago
        self.search_payment_id_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Validar solo números enteros
        self.search_payment_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Pago:"))
        search_layout.addWidget(self.search_payment_id_input)

        # ID del Préstamo
        self.search_loan_id_input = QLineEdit()
        self.search_loan_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Préstamo:"))
        search_layout.addWidget(self.search_loan_id_input)

        # Campo de selección de fecha de inicio de pago
        self.start_date_checkbox = QCheckBox("Usar Fecha Inicio")
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setEnabled(False)  # Deshabilitar campo inicialmente
        self.start_date_checkbox.toggled.connect(self.start_date_input.setEnabled)
        search_layout.addWidget(self.start_date_checkbox)
        search_layout.addWidget(self.start_date_input)

        # Campo de selección de fecha de fin de pago
        self.end_date_checkbox = QCheckBox("Usar Fecha Fin")
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setEnabled(False)  # Deshabilitar campo inicialmente
        self.end_date_checkbox.toggled.connect(self.end_date_input.setEnabled)
        search_layout.addWidget(self.end_date_checkbox)
        search_layout.addWidget(self.end_date_input)

        # Botón de búsqueda
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_loan_empleado_payments)
        search_layout.addWidget(self.search_button)

        # Agregar layout de búsqueda al layout principal
        self.layout.addLayout(search_layout)

        # Crear la tabla para mostrar los pagos
        self.loan_payment_table = QTableWidget()
        self.loan_payment_table.setColumnCount(6)
        self.loan_payment_table.setHorizontalHeaderLabels([
            "ID Pago", "ID Préstamo", "ID Empleado", "Monto Pagado", "Fecha de Pago", "Método de Pago"
        ])
        self.loan_payment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.loan_payment_table)


        # Cargar los registros de pagos en la tabla
        self.load_loan_empleado_payments()



    def load_loan_empleado_payments(self):
        # Obtener todos los pagos desde la base de datos
        pagos = self.pago_dao.cargar_pagos_por_empleado(self.usuario.id_empleado)

        # Limpiar la tabla antes de cargar nuevos datos
        self.loan_payment_table.setRowCount(len(pagos))

        for i, pago in enumerate(pagos):
            self.loan_payment_table.setItem(i, 0, QTableWidgetItem(str(pago.id)))
            self.loan_payment_table.setItem(i, 1, QTableWidgetItem(str(pago.id_prestamo)))
            self.loan_payment_table.setItem(i, 2, QTableWidgetItem(str(pago.id_empleado)))
            self.loan_payment_table.setItem(i, 3, QTableWidgetItem(f"{pago.monto_pagado:.2f}"))
            self.loan_payment_table.setItem(i, 4, QTableWidgetItem(str(pago.fecha_pago)))
            self.loan_payment_table.setItem(i, 5, QTableWidgetItem(pago.metodo_pago))


    def search_loan_empleado_payments(self):
        # Obtener los filtros de búsqueda si los hay
        payment_id = self.search_payment_id_input.text().strip()
        loan_id = self.search_loan_id_input.text().strip()
        employee_id = self.usuario.id_empleado
        start_date = self.start_date_input.date().toPyDate() if self.start_date_checkbox.isChecked() else None
        end_date = self.end_date_input.date().toPyDate() if self.end_date_checkbox.isChecked() else None

        # Buscar los pagos en base a los filtros
        pagos = self.pago_dao.buscar_pagos(payment_id, loan_id, employee_id, start_date, end_date)

        # Limpiar la tabla y cargar los resultados de búsqueda
        self.loan_payment_table.setRowCount(len(pagos))

        for i, pago in enumerate(pagos):
            self.loan_payment_table.setItem(i, 0, QTableWidgetItem(str(pago.id)))
            self.loan_payment_table.setItem(i, 1, QTableWidgetItem(str(pago.id_prestamo)))
            self.loan_payment_table.setItem(i, 2, QTableWidgetItem(str(pago.id_empleado)))
            self.loan_payment_table.setItem(i, 3, QTableWidgetItem(f"{pago.monto_pagado:.2f}"))
            self.loan_payment_table.setItem(i, 4, QTableWidgetItem(str(pago.fecha_pago)))
            self.loan_payment_table.setItem(i, 5, QTableWidgetItem(pago.metodo_pago))

    def show_log_management(self):
        self.clear_layout()

        search_layout = QHBoxLayout()

        self.search_log_id_input = QLineEdit()
        validator = QIntValidator(0, 2147483646, self)  # Validar solo números enteros
        self.search_log_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Log:"))
        search_layout.addWidget(self.search_log_id_input)

        self.search_user_id_input = QLineEdit()
        self.search_user_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Usuario:"))
        search_layout.addWidget(self.search_user_id_input)

        self.search_employee_id_input = QLineEdit()
        self.search_employee_id_input.setValidator(validator)
        search_layout.addWidget(QLabel("ID Empleado:"))
        search_layout.addWidget(self.search_employee_id_input)

        self.start_date_checkbox = QCheckBox("Usar Fecha Inicio")
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setEnabled(False)  # Deshabilitar campo inicialmente
        self.start_date_checkbox.toggled.connect(self.start_date_input.setEnabled)
        search_layout.addWidget(self.start_date_checkbox)
        search_layout.addWidget(self.start_date_input)

        self.end_date_checkbox = QCheckBox("Usar Fecha Fin")
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setEnabled(False)  # Deshabilitar campo inicialmente
        self.end_date_checkbox.toggled.connect(self.end_date_input.setEnabled)
        search_layout.addWidget(self.end_date_checkbox)
        search_layout.addWidget(self.end_date_input)

        self.search_tipo_input = QComboBox()
        self.search_tipo_input.addItems(['', 'ENTRADA', 'SALIDA'])  # Campo vacío para buscar todos los tipos
        search_layout.addWidget(QLabel("Tipo:"))
        search_layout.addWidget(self.search_tipo_input)

        self.search_estado_input = QComboBox()
        self.search_estado_input.addItems(['', 'EXITOSO', 'FALLIDO'])  # Campo vacío para buscar todos los estados
        search_layout.addWidget(QLabel("Estado:"))
        search_layout.addWidget(self.search_estado_input)

        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_log_sessions)
        search_layout.addWidget(self.search_button)

        self.layout.addLayout(search_layout)

        # Crear la tabla para mostrar los registros de inicio de sesión
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(8)
        self.log_table.setHorizontalHeaderLabels([
            "ID Log", "ID Usuario", "ID Empleado", "Nombre", "Apellido", "Fecha", "Tipo", "Estado"
        ])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.log_table)


        self.load_log_sessions()

    def load_log_sessions(self):
        # Obtener todos los registros de inicio de sesión desde la base de datos
        logs = self.log_sesion_dao.cargar_todos_los_logs_sesion()

        # Limpiar la tabla antes de cargar nuevos datos
        self.log_table.setRowCount(len(logs))

        for i, log in enumerate(logs):
            self.log_table.setItem(i, 0, QTableWidgetItem(str(log.id)))
            self.log_table.setItem(i, 1, QTableWidgetItem(str(log.id_usuario)))
            self.log_table.setItem(i, 2, QTableWidgetItem(str(log.id_empleado)))
            self.log_table.setItem(i, 3, QTableWidgetItem(log.nombre_empleado))
            self.log_table.setItem(i, 4, QTableWidgetItem(log.apellido_empleado))
            self.log_table.setItem(i, 5, QTableWidgetItem(str(log.fecha)))
            self.log_table.setItem(i, 6, QTableWidgetItem(log.tipo))
            self.log_table.setItem(i, 7, QTableWidgetItem(log.estado))

    def search_log_sessions(self):
        # Obtener los filtros de búsqueda si los hay
        log_id = self.search_log_id_input.text().strip()
        user_id = self.search_user_id_input.text().strip()
        employee_id = self.search_employee_id_input.text().strip()
        start_date = self.start_date_input.date().toPyDate() if self.start_date_checkbox.isChecked() else None
        end_date = self.end_date_input.date().toPyDate() if self.end_date_checkbox.isChecked() else None
        tipo = self.search_tipo_input.currentText().strip()
        estado = self.search_estado_input.currentText().strip()

        logs = self.log_sesion_dao.buscar_logs(log_id, user_id, employee_id, start_date, end_date, tipo, estado)

        # Limpiar la tabla y cargar los resultados de búsqueda
        self.log_table.setRowCount(len(logs))

        for i, log in enumerate(logs):
            self.log_table.setItem(i, 0, QTableWidgetItem(str(log.id)))
            self.log_table.setItem(i, 1, QTableWidgetItem(str(log.id_usuario)))
            self.log_table.setItem(i, 2, QTableWidgetItem(str(log.id_empleado)))
            self.log_table.setItem(i, 3, QTableWidgetItem(log.nombre_empleado))
            self.log_table.setItem(i, 4, QTableWidgetItem(log.apellido_empleado))
            self.log_table.setItem(i, 5, QTableWidgetItem(str(log.fecha)))
            self.log_table.setItem(i, 6, QTableWidgetItem(log.tipo))
            self.log_table.setItem(i, 7, QTableWidgetItem(log.estado))


    def generate_morosos_report(self):
        report_data = generate_morosos_report()
        self.create_pdf_report(report_data, "reporte_morosos.pdf")

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # Eliminar el widget
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clear_sub_layout(sub_layout)

    def clear_sub_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clear_sub_layout(sub_layout)

    def create_pdf_report(self, report_data, file_name):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(file_name, pagesize=letter)
        c.drawString(100, 750, "Reporte de Morosos")
        # Agrega más lógica para escribir los datos del reporte
        y = 730
        for line in report_data:
            c.drawString(100, y, line)
            y -= 15
        c.save()

if __name__ == "__main__":
    app = QApplication([])
        # Cargar la hoja de estilos CSS
    with open("styles.css", "r") as f:
        stylesheet = f.read()
        app.setStyleSheet(stylesheet)
        
    login_window = LoginWindow()
    login_window.show()  # Muestra la ventana de login
    app.exec_()       