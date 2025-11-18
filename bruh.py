# simulador_unitario_bigben.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import os
import math
import re

# ---------------------------
# Teclado Matemático
# ---------------------------
class TecladoMatematico:
    def __init__(self, parent, entry_widget):
        self.parent = parent
        self.entry = entry_widget
        self.window = None
        
    def mostrar(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("Teclado Matemático")
        self.window.geometry("600x400")
        self.window.resizable(False, False)
        
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Display de la función actual
        self.func_display = ttk.Entry(main_frame, font=("Arial", 12), width=50)
        self.func_display.pack(pady=5)
        self.func_display.bind('<KeyRelease>', self.actualizar_entry)
        
        # Frames para diferentes tipos de teclas
        frame_numeros = ttk.Frame(main_frame)
        frame_numeros.pack(fill="x", pady=5)
        
        frame_operadores = ttk.Frame(main_frame)
        frame_operadores.pack(fill="x", pady=5)
        
        frame_funciones = ttk.Frame(main_frame)
        frame_funciones.pack(fill="x", pady=5)
        
        frame_avanzadas = ttk.Frame(main_frame)
        frame_avanzadas.pack(fill="x", pady=5)
        
        frame_controles = ttk.Frame(main_frame)
        frame_controles.pack(fill="x", pady=10)
        
        # Teclas numéricas
        numeros = [
            ['7', '8', '9'],
            ['4', '5', '6'], 
            ['1', '2', '3'],
            ['0', '.', 'π']
        ]
        
        for i, fila in enumerate(numeros):
            for j, num in enumerate(fila):
                cmd = lambda x=num: self.insertar_texto(x)
                btn = ttk.Button(frame_numeros, text=num, command=cmd, width=8)
                btn.grid(row=i, column=j, padx=2, pady=2)
        
        # Operadores básicos
        operadores = ['+', '-', '*', '/', '^', '(', ')']
        for i, op in enumerate(operadores):
            cmd = lambda x=op: self.insertar_texto(x)
            btn = ttk.Button(frame_operadores, text=op, command=cmd, width=8)
            btn.grid(row=0, column=i, padx=2, pady=2)
        
        # Funciones trigonométricas
        funciones = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']
        for i, func in enumerate(funciones):
            cmd = lambda x=func: self.insertar_texto(f"{x}(")
            btn = ttk.Button(frame_funciones, text=func, command=cmd, width=8)
            btn.grid(row=0, column=i, padx=2, pady=2)
        
        # Funciones avanzadas
        avanzadas = ['log', 'ln', 'sqrt', 'exp', 'abs', 'x']
        for i, adv in enumerate(avanzadas):
            if adv == 'x':
                cmd = lambda: self.insertar_texto("x")
            else:
                cmd = lambda x=adv: self.insertar_texto(f"{x}(")
            btn = ttk.Button(frame_avanzadas, text=adv, command=cmd, width=8)
            btn.grid(row=0, column=i, padx=2, pady=2)
        
        # Controles
        ttk.Button(frame_controles, text="Borrar", 
                  command=self.borrar, width=8).grid(row=0, column=0, padx=2)
        ttk.Button(frame_controles, text="Borrar Todo", 
                  command=self.borrar_todo, width=10).grid(row=0, column=1, padx=2)
        ttk.Button(frame_controles, text="Insertar", 
                  command=self.insertar_en_entry, width=8).grid(row=0, column=2, padx=2)
        ttk.Button(frame_controles, text="Cerrar", 
                  command=self.window.destroy, width=8).grid(row=0, column=3, padx=2)
        
        # Sincronizar con el entry original
        self.actualizar_display()
        
    def insertar_texto(self, texto):
        current = self.func_display.get()
        cursor_pos = self.func_display.index(tk.INSERT)
        new_text = current[:cursor_pos] + texto + current[cursor_pos:]
        self.func_display.delete(0, tk.END)
        self.func_display.insert(0, new_text)
        self.func_display.focus()
        self.func_display.icursor(cursor_pos + len(texto))
        
    def borrar(self):
        current = self.func_display.get()
        cursor_pos = self.func_display.index(tk.INSERT)
        if cursor_pos > 0:
            new_text = current[:cursor_pos-1] + current[cursor_pos:]
            self.func_display.delete(0, tk.END)
            self.func_display.insert(0, new_text)
            self.func_display.focus()
            self.func_display.icursor(cursor_pos - 1)
            
    def borrar_todo(self):
        self.func_display.delete(0, tk.END)
        self.func_display.focus()
        
    def actualizar_display(self):
        if self.entry:
            self.func_display.delete(0, tk.END)
            self.func_display.insert(0, self.entry.get())
            
    def actualizar_entry(self, event=None):
        if self.entry:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.func_display.get())
            
    def insertar_en_entry(self):
        if self.entry:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.func_display.get())
        self.window.destroy()

# ---------------------------
# Evaluador de Funciones
# ---------------------------
class EvaluadorFunciones:
    @staticmethod
    def evaluar_funcion(func_str, x_val):
        """Evalúa una función matemática en un punto x dado"""
        try:
            # Reemplazar constantes matemáticas
            func_str = func_str.replace('π', 'math.pi')
            func_str = func_str.replace('e', 'math.e')
            
            # Reemplazar funciones matemáticas
            func_str = func_str.replace('^', '**')
            func_str = re.sub(r'sin\(', 'math.sin(', func_str)
            func_str = re.sub(r'cos\(', 'math.cos(', func_str)
            func_str = re.sub(r'tan\(', 'math.tan(', func_str)
            func_str = re.sub(r'asin\(', 'math.asin(', func_str)
            func_str = re.sub(r'acos\(', 'math.acos(', func_str)
            func_str = re.sub(r'atan\(', 'math.atan(', func_str)
            func_str = re.sub(r'log\(', 'math.log10(', func_str)
            func_str = re.sub(r'ln\(', 'math.log(', func_str)
            func_str = re.sub(r'sqrt\(', 'math.sqrt(', func_str)
            func_str = re.sub(r'exp\(', 'math.exp(', func_str)
            func_str = re.sub(r'abs\(', 'math.fabs(', func_str)
            
            # Crear un entorno seguro para eval
            safe_dict = {
                'math': math,
                'sin': math.sin,
                'cos': math.cos, 
                'tan': math.tan,
                'asin': math.asin,
                'acos': math.acos,
                'atan': math.atan,
                'log': math.log10,
                'ln': math.log,
                'sqrt': math.sqrt,
                'exp': math.exp,
                'abs': math.fabs,
                'pi': math.pi,
                'e': math.e,
                'x': x_val
            }
            
            # Evaluar la función
            result = eval(func_str, {"__builtins__": {}}, safe_dict)
            return float(result)
            
        except Exception as e:
            raise ValueError(f"Error al evaluar la función: {str(e)}")

# ---------------------------
# Menú Principal
# ---------------------------
class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Matemático – Círculo Unitario & Big Ben")
        self.root.geometry("900x500")

        titulo = tk.Label(root, text="Simulador Matemático", font=("Arial", 30, "bold"))
        titulo.pack(pady=20)

        tk.Button(
            root, text="Simulación del Círculo Unitario",
            command=self.abrir_circulo, width=35, height=2, font=("Arial", 16)
        ).pack(pady=10)

        tk.Button(
            root, text="Simulación del Big Ben",
            command=self.abrir_bigben, width=35, height=2, font=("Arial", 16)
        ).pack(pady=10)

        tk.Button(
            root, text="Salir del Programa",
            command=self.root.destroy, width=20, height=2, font=("Arial", 14)
        ).pack(pady=30)

    def abrir_circulo(self):
        CirculoUnitarioVentana(self.root)

    def abrir_bigben(self):
        BigBenVentana(self.root)

# ---------------------------
# Circulo Unitario (VERSIÓN GEOGEBRA - CON CHECKBOXES)
# ---------------------------
class CirculoUnitarioVentana:
    def __init__(self, menu_root):
        self.menu_root = menu_root
        self.win = tk.Toplevel()
        self.win.title("Simulación del Círculo Unitario - Estilo GeoGebra")
        self.win.geometry("1400x900")

        # Evaluador de funciones
        self.evaluador = EvaluadorFunciones()

        # Variables para checkboxes (como en GeoGebra)
        self.mostrar_seno = tk.BooleanVar(value=True)
        self.mostrar_coseno = tk.BooleanVar(value=True)
        self.mostrar_tangente = tk.BooleanVar(value=False)
        self.mostrar_cotangente = tk.BooleanVar(value=False)
        self.mostrar_secante = tk.BooleanVar(value=False)
        self.mostrar_cosecante = tk.BooleanVar(value=False)
        self.mostrar_triangulo = tk.BooleanVar(value=True)

        # frames principales
        main_container = ttk.Frame(self.win)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Left frame para el círculo y controles
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Right frame para la calculadora
        right_frame = ttk.Frame(main_container, width=400)
        right_frame.pack(side="right", fill="y", padx=5, pady=5)
        right_frame.pack_propagate(False)

        # ========== CONTROLES DEL CÍRCULO ==========
        controls_frame = ttk.Frame(left_frame)
        controls_frame.pack(fill="x", padx=12, pady=8)

        # Input de ángulo con teclado
        input_frame = ttk.Frame(controls_frame)
        input_frame.grid(row=0, column=0, padx=6, pady=4, sticky="w")
        
        ttk.Label(input_frame, text="Ángulo (°):", font=("Arial", 12)).grid(row=0, column=0, padx=6, pady=4, sticky="e")
        self.ang_var = tk.DoubleVar(value=45)
        self.ang_entry = ttk.Entry(input_frame, textvariable=self.ang_var, width=10, font=("Arial", 12))
        self.ang_entry.grid(row=0, column=1, padx=6, pady=4)
        
        # Botón del teclado numérico
        ttk.Button(input_frame, text="⌨", command=self.mostrar_teclado_angulo, width=3).grid(row=0, column=2, padx=2, pady=4)

        # Botones de control del círculo
        ttk.Button(controls_frame, text="Actualizar", command=self.actualizar_circulo, width=15).grid(row=0, column=1, padx=8, pady=4)
        ttk.Button(controls_frame, text="Guardar imagen", command=self.guardar_imagen, width=15).grid(row=0, column=2, padx=8, pady=4)
        
        # Controles de zoom y movimiento
        ttk.Label(controls_frame, text="Controles:", font=("Arial", 12)).grid(row=0, column=3, padx=6, pady=4, sticky="e")
        ttk.Button(controls_frame, text="Zoom +", command=lambda: self._zoom(1.2), width=10).grid(row=0, column=4, padx=4, pady=4)
        ttk.Button(controls_frame, text="Zoom -", command=lambda: self._zoom(0.8), width=10).grid(row=0, column=5, padx=4, pady=4)
        ttk.Button(controls_frame, text="Reset View", command=self._reset_view, width=10).grid(row=0, column=6, padx=4, pady=4)
        
        ttk.Button(controls_frame, text="Regresar al menú", command=self.win.destroy, width=15).grid(row=0, column=7, padx=8, pady=4)

        # ========== CHECKBOXES AL ESTILO GEOGEBRA ==========
        checkboxes_frame = ttk.Frame(left_frame)
        checkboxes_frame.pack(fill="x", padx=12, pady=8)

        # Fila 1 de checkboxes
        ttk.Checkbutton(checkboxes_frame, text="seno (MP)", variable=self.mostrar_seno, 
                       command=self.actualizar_circulo).grid(row=0, column=0, padx=10, pady=2, sticky="w")
        ttk.Checkbutton(checkboxes_frame, text="coseno (OM)", variable=self.mostrar_coseno, 
                       command=self.actualizar_circulo).grid(row=0, column=1, padx=10, pady=2, sticky="w")
        ttk.Checkbutton(checkboxes_frame, text="tangente (AQ)", variable=self.mostrar_tangente, 
                       command=self.actualizar_circulo).grid(row=0, column=2, padx=10, pady=2, sticky="w")
        ttk.Checkbutton(checkboxes_frame, text="cotangente (BR)", variable=self.mostrar_cotangente, 
                       command=self.actualizar_circulo).grid(row=0, column=3, padx=10, pady=2, sticky="w")

        # Fila 2 de checkboxes
        ttk.Checkbutton(checkboxes_frame, text="secante (OQ)", variable=self.mostrar_secante, 
                       command=self.actualizar_circulo).grid(row=1, column=0, padx=10, pady=2, sticky="w")
        ttk.Checkbutton(checkboxes_frame, text="cosecante (OR)", variable=self.mostrar_cosecante, 
                       command=self.actualizar_circulo).grid(row=1, column=1, padx=10, pady=2, sticky="w")
        ttk.Checkbutton(checkboxes_frame, text="triángulo", variable=self.mostrar_triangulo, 
                       command=self.actualizar_circulo).grid(row=1, column=2, padx=10, pady=2, sticky="w")

        # ========== GRÁFICA DEL CÍRCULO ==========
        circle_frame = ttk.Frame(left_frame)
        circle_frame.pack(fill="both", expand=True, padx=12, pady=6)

        # Figura y canvas del círculo
        self.fig, self.ax = plt.subplots(figsize=(7, 7))
        self.ax.set_aspect("equal")
        self.ax.set_xlim(-1.8, 1.8)  # Más espacio para mostrar tangente, etc.
        self.ax.set_ylim(-1.8, 1.8)

        # Ejes visibles y marcados
        self.ax.axhline(0, color="black", linewidth=1)
        self.ax.axvline(0, color="black", linewidth=1)
        self.ax.set_xlabel("Eje X")
        self.ax.set_ylabel("Eje Y")
        self.ax.set_title("Círculo Unitario — Coordenadas y Funciones Trigonométricas", fontsize=14, fontweight="bold")

        # Grid medio faint
        self.ax.grid(alpha=0.15, linestyle='-', linewidth=0.5)

        # dibujar círculo unitario
        t = np.linspace(0, 2*np.pi, 400)
        self.ax.plot(np.cos(t), np.sin(t), 'black', lw=2, zorder=1)

        # Dibujar ejes de tangente y cotangente (líneas vertical y horizontal en x=1, y=1)
        self.ax.axvline(1, color='gray', alpha=0.3, linestyle='-', linewidth=1)
        self.ax.axhline(1, color='gray', alpha=0.3, linestyle='-', linewidth=1)

        # Elementos gráficos (se crearán dinámicamente)
        self.point = None
        self.line_radius = None
        self.line_seno = None
        self.line_coseno = None
        self.line_tangente = None
        self.line_cotangente = None
        self.line_secante = None
        self.line_cosecante = None
        self.triangle = None
        self.text_info = None

        # Tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=circle_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Eventos para interactividad
        self.fig.canvas.mpl_connect("scroll_event", self._zoom_handler)
        self.press = None
        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self._on_press)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self._on_release)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event', self._on_motion)

        # ========== CALCULADORA Y GRAFICADORA (IGUAL QUE ANTES) ==========
        calc_title = ttk.Label(right_frame, text="Calculadora y Graficadora", 
                              font=("Arial", 16, "bold"))
        calc_title.pack(pady=10)

        # Entrada de función
        func_frame = ttk.Frame(right_frame)
        func_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(func_frame, text="Función f(x):", font=("Arial", 12)).pack(anchor="w")
        self.func_var = tk.StringVar(value="sin(x)")
        self.func_entry = ttk.Entry(func_frame, textvariable=self.func_var, width=30, font=("Arial", 12))
        self.func_entry.pack(fill="x", pady=5)
        
        # Botón del teclado matemático
        ttk.Button(func_frame, text="⌨ Teclado Matemático", 
                  command=self.mostrar_teclado_funcion, width=20).pack(pady=5)

        # Rango de x
        range_frame = ttk.Frame(right_frame)
        range_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(range_frame, text="Rango x:", font=("Arial", 12)).pack(anchor="w")
        
        range_input_frame = ttk.Frame(range_frame)
        range_input_frame.pack(fill="x", pady=5)
        
        self.xmin_var = tk.DoubleVar(value=-2*np.pi)
        self.xmax_var = tk.DoubleVar(value=2*np.pi)
        
        ttk.Entry(range_input_frame, textvariable=self.xmin_var, width=8, font=("Arial", 10)).pack(side="left", padx=2)
        ttk.Label(range_input_frame, text=" a ", font=("Arial", 10)).pack(side="left")
        ttk.Entry(range_input_frame, textvariable=self.xmax_var, width=8, font=("Arial", 10)).pack(side="left", padx=2)

        # Botones de acción
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(action_frame, text="Graficar Función", command=self.graficar_funcion, width=20).pack(pady=5)
        ttk.Button(action_frame, text="Evaluar en Ángulo Actual", command=self.evaluar_en_angulo, width=20).pack(pady=5)
        ttk.Button(action_frame, text="Limpiar Gráfica", command=self.limpiar_grafica_funcion, width=20).pack(pady=5)

        # Resultados
        result_frame = ttk.Frame(right_frame)
        result_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(result_frame, text="Resultados:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.result_text = tk.Text(result_frame, height=8, width=35, font=("Arial", 10))
        self.result_text.pack(fill="both", expand=True, pady=5)
        
        # Gráfica de función pequeña
        graph_frame = ttk.Frame(right_frame)
        graph_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.fig_func, self.ax_func = plt.subplots(figsize=(4, 3))
        self.ax_func.grid(True, alpha=0.3)
        self.ax_func.set_xlabel('x')
        self.ax_func.set_ylabel('f(x)')
        self.ax_func.set_title('Gráfica de Función')
        
        self.canvas_func = FigureCanvasTkAgg(self.fig_func, master=graph_frame)
        self.canvas_func.get_tk_widget().pack(fill="both", expand=True)

        # Inicializar el círculo
        self.actualizar_circulo()

    def mostrar_teclado_angulo(self):
        """Muestra el teclado para ingresar el ángulo"""
        teclado = TecladoMatematico(self.win, self.ang_entry)
        teclado.mostrar()

    def mostrar_teclado_funcion(self):
        """Muestra el teclado matemático para ingresar funciones"""
        teclado = TecladoMatematico(self.win, self.func_entry)
        teclado.mostrar()

    def actualizar_circulo(self):
        """Actualiza el círculo unitario con todas las funciones trigonométricas según los checkboxes"""
        try:
            ang = float(self.ang_var.get())
        except Exception:
            messagebox.showerror("Error", "Ángulo inválido")
            return

        rad = np.radians(ang)
        x = np.cos(rad)
        y = np.sin(rad)

        # Limpiar elementos anteriores
        for element in [self.point, self.line_radius, self.line_seno, self.line_coseno, 
                       self.line_tangente, self.line_cotangente, self.line_secante, 
                       self.line_cosecante, self.triangle, self.text_info]:
            if element is not None:
                try:
                    element.remove()
                except:
                    pass

        # Punto en la circunferencia
        self.point, = self.ax.plot(x, y, "o", color="red", markersize=8, zorder=10)

        # Radio (siempre visible)
        self.line_radius, = self.ax.plot([0, x], [0, y], "-", color="black", lw=2, zorder=5)

        # SENO (MP) - Proyección vertical
        if self.mostrar_seno.get():
            self.line_seno, = self.ax.plot([x, x], [0, y], "--", color="green", lw=2, zorder=4)
            self.ax.text(x + 0.05, y/2, f"sin={y:.3f}", color="green", fontsize=10, 
                        bbox=dict(facecolor='white', alpha=0.7))

        # COSENO (OM) - Proyección horizontal
        if self.mostrar_coseno.get():
            self.line_coseno, = self.ax.plot([0, x], [y, y], "--", color="blue", lw=2, zorder=4)
            self.ax.text(x/2, y + 0.05, f"cos={x:.3f}", color="blue", fontsize=10,
                        bbox=dict(facecolor='white', alpha=0.7))

        # TANGENTE (AQ)
        if self.mostrar_tangente.get() and abs(x) > 1e-10:  # Evitar división por cero
            tan_val = y / x
            # Punto Q en la línea x=1
            qx, qy = 1, tan_val
            if abs(tan_val) <= 1.8:  # Solo dibujar si está en el rango visible
                self.line_tangente, = self.ax.plot([x, qx], [y, qy], "--", color="orange", lw=2, zorder=4)
                self.ax.plot(qx, qy, 'o', color="orange", markersize=6)
                self.ax.text(qx + 0.05, qy, f"tan={tan_val:.3f}", color="orange", fontsize=10,
                            bbox=dict(facecolor='white', alpha=0.7))

        # COTANGENTE (BR)
        if self.mostrar_cotangente.get() and abs(y) > 1e-10:  # Evitar división por cero
            cot_val = x / y
            # Punto R en la línea y=1
            rx, ry = cot_val, 1
            if abs(cot_val) <= 1.8:  # Solo dibujar si está en el rango visible
                self.line_cotangente, = self.ax.plot([x, rx], [y, ry], "--", color="purple", lw=2, zorder=4)
                self.ax.plot(rx, ry, 'o', color="purple", markersize=6)
                self.ax.text(rx, ry + 0.05, f"cot={cot_val:.3f}", color="purple", fontsize=10,
                            bbox=dict(facecolor='white', alpha=0.7))

        # SECANTE (OQ)
        if self.mostrar_secante.get():
            if abs(x) > 1e-10:  # Evitar división por cero
                sec_val = 1 / x
                # La secante es la línea desde el origen hasta el punto de tangente
                self.line_secante, = self.ax.plot([0, 1], [0, sec_val], "--", color="brown", lw=2, zorder=3)
                self.ax.text(0.5, sec_val/2 + 0.1, f"sec={sec_val:.3f}", color="brown", fontsize=10,
                            bbox=dict(facecolor='white', alpha=0.7))

        # COSECANTE (OR)
        if self.mostrar_cosecante.get():
            if abs(y) > 1e-10:  # Evitar división por cero
                csc_val = 1 / y
                # La cosecante es la línea desde el origen hasta el punto de cotangente
                self.line_cosecante, = self.ax.plot([0, csc_val], [0, 1], "--", color="pink", lw=2, zorder=3)
                self.ax.text(csc_val/2, 0.5, f"csc={csc_val:.3f}", color="pink", fontsize=10,
                            bbox=dict(facecolor='white', alpha=0.7))

        # TRIÁNGULO RECTÁNGULO
        if self.mostrar_triangulo.get():
            triangle_x = [0, x, x]
            triangle_y = [0, 0, y]
            self.triangle = self.ax.fill(triangle_x, triangle_y, alpha=0.2, color='gray')[0]

        # INFORMACIÓN NUMÉRICA
        info_text = f"Ángulo: {ang:.1f}°\n"
        info_text += f"sin(θ) = {y:.3f}\n"
        info_text += f"cos(θ) = {x:.3f}\n"
        if abs(x) > 1e-10:
            info_text += f"tan(θ) = {y/x:.3f}\n"
        if abs(y) > 1e-10:
            info_text += f"cot(θ) = {x/y:.3f}\n"
        if abs(x) > 1e-10:
            info_text += f"sec(θ) = {1/x:.3f}\n"
        if abs(y) > 1e-10:
            info_text += f"csc(θ) = {1/y:.3f}"

        self.text_info = self.ax.text(-1.7, 1.6, info_text, fontsize=11,
                                     bbox=dict(facecolor="white", alpha=0.9, edgecolor='black'),
                                     verticalalignment='top')

        self.canvas.draw_idle()

    # Los métodos restantes (graficar_funcion, evaluar_en_angulo, etc.) se mantienen igual
    def graficar_funcion(self):
        """Grafica la función ingresada por el usuario"""
        try:
            # Obtener función y rango
            func_str = self.func_var.get().strip()
            x_min = self.xmin_var.get()
            x_max = self.xmax_var.get()
            
            if x_min >= x_max:
                messagebox.showerror("Error", "El valor mínimo de x debe ser menor que el máximo")
                return
            
            # Generar puntos x
            x_vals = np.linspace(x_min, x_max, 1000)
            y_vals = []
            
            # Evaluar función en cada punto
            for x_val in x_vals:
                try:
                    y_val = self.evaluador.evaluar_funcion(func_str, x_val)
                    y_vals.append(y_val)
                except ValueError as e:
                    messagebox.showerror("Error de evaluación", str(e))
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Error al evaluar en x={x_val:.2f}: {str(e)}")
                    return
            
            # Limpiar gráfica anterior
            self.ax_func.clear()
            
            # Graficar nueva función
            self.ax_func.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'f(x) = {func_str}')
            self.ax_func.grid(True, alpha=0.3)
            self.ax_func.set_xlabel('x')
            self.ax_func.set_ylabel('f(x)')
            self.ax_func.set_title(f'f(x) = {func_str}')
            self.ax_func.legend()
            
            # Ajustar límites automáticamente
            y_vals_arr = np.array(y_vals)
            valid_vals = y_vals_arr[np.isfinite(y_vals_arr)]
            
            if len(valid_vals) > 0:
                y_range = np.max(valid_vals) - np.min(valid_vals)
                if y_range > 0:
                    margin = y_range * 0.1
                    self.ax_func.set_ylim(np.min(valid_vals) - margin, np.max(valid_vals) + margin)
            
            self.canvas_func.draw()
            
            # Mostrar resultado
            self.mostrar_resultado(f"Función graficada: f(x) = {func_str}\n"
                                 f"Rango: x ∈ [{x_min:.2f}, {x_max:.2f}]")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al graficar la función: {str(e)}")

    def evaluar_en_angulo(self):
        """Evalúa la función en el ángulo actual del círculo unitario"""
        try:
            ang = float(self.ang_var.get())
            func_str = self.func_var.get().strip()
            
            # Convertir ángulo a valor x (usando radianes para evaluación)
            x_val = np.radians(ang)
            
            # Evaluar función
            resultado = self.evaluador.evaluar_funcion(func_str, x_val)
            
            # Mostrar resultado
            self.mostrar_resultado(f"Evaluación en ángulo actual:\n"
                                 f"Ángulo: {ang:.2f}°\n"
                                 f"x (radianes): {x_val:.4f}\n"
                                 f"f({x_val:.4f}) = {resultado:.6f}\n\n"
                                 f"Función: {func_str}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al evaluar la función: {str(e)}")

    def limpiar_grafica_funcion(self):
        """Limpia la gráfica de función"""
        self.ax_func.clear()
        self.ax_func.grid(True, alpha=0.3)
        self.ax_func.set_xlabel('x')
        self.ax_func.set_ylabel('f(x)')
        self.ax_func.set_title('Gráfica de Función')
        self.canvas_func.draw()
        self.mostrar_resultado("Gráfica limpiada")

    def mostrar_resultado(self, texto):
        """Muestra texto en el área de resultados"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, texto)

    def guardar_imagen(self):
        fname = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG image", "*.png"), ("All files", "*.*")],
                                             initialfile="circulo_unitario_geogebra.png")
        if not fname:
            return
        self.fig.savefig(fname, dpi=300)
        messagebox.showinfo("Guardado", f"Imagen guardada en:\n{fname}")

    def _zoom(self, factor):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        center_x = (cur_xlim[0] + cur_xlim[1]) / 2
        center_y = (cur_ylim[0] + cur_ylim[1]) / 2
        
        width = (cur_xlim[1] - cur_xlim[0]) * factor
        height = (cur_ylim[1] - cur_ylim[0]) * factor
        
        self.ax.set_xlim([center_x - width/2, center_x + width/2])
        self.ax.set_ylim([center_y - height/2, center_y + height/2])
        self.canvas.draw_idle()

    def _reset_view(self):
        self.ax.set_xlim(-1.8, 1.8)
        self.ax.set_ylim(-1.8, 1.8)
        self.canvas.draw_idle()

    def _zoom_handler(self, event):
        base_scale = 1.1
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            return

        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        self.canvas.draw_idle()

    def _on_press(self, event):
        if event.button != 1:
            return
        self.press = (event.x, event.y, self.ax.get_xlim(), self.ax.get_ylim())

    def _on_release(self, event):
        self.press = None

    def _on_motion(self, event):
        if self.press is None or event.button != 1:
            return
        xpress, ypress, (x0, x1), (y0, y1) = self.press
        dx = event.x - xpress
        dy = event.y - ypress
        width = self.canvas.get_tk_widget().winfo_width()
        height = self.canvas.get_tk_widget().winfo_height()
        if width == 0 or height == 0:
            return
        dx_data = -dx * (x1 - x0) / width
        dy_data = dy * (y1 - y0) / height
        self.ax.set_xlim(x0 + dx_data, x1 + dx_data)
        self.ax.set_ylim(y0 + dy_data, y1 + dy_data)
        self.canvas.draw_idle()
# ---------------------------
# Big Ben (VERSIÓN MEJORADA - MÁS GRANDE Y CON CHECKBOXES)
# ---------------------------
class BigBenVentana:
    def __init__(self, menu_root):
        self.menu_root = menu_root
        self.win = tk.Toplevel()
        self.win.title("Simulación del Big Ben - Estilo GeoGebra")
        self.win.geometry("1600x1200")  # Ventana más grande

        # Variables para checkboxes (como en GeoGebra)
        self.mostrar_seno = tk.BooleanVar(value=True)
        self.mostrar_coseno = tk.BooleanVar(value=True)
        self.mostrar_tangente = tk.BooleanVar(value=False)
        self.mostrar_cotangente = tk.BooleanVar(value=False)
        self.mostrar_secante = tk.BooleanVar(value=False)
        self.mostrar_cosecante = tk.BooleanVar(value=False)
        self.mostrar_triangulo = tk.BooleanVar(value=True)
        self.mostrar_manecilla_hora = tk.BooleanVar(value=True)
        self.mostrar_manecilla_minuto = tk.BooleanVar(value=True)
        self.mostrar_onda_seno = tk.BooleanVar(value=True)
        self.mostrar_onda_coseno = tk.BooleanVar(value=True)

        main = ttk.Frame(self.win)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Contenedor para el canvas y controles
        left_frame = ttk.Frame(main)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        right_frame = ttk.Frame(main)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        main.columnconfigure(0, weight=4)  # Más espacio para gráficos
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # ========== CHECKBOXES PARA EL BIG BEN ==========
        checkboxes_frame = ttk.Frame(right_frame)
        checkboxes_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(checkboxes_frame, text="Mostrar Elementos:", 
                 font=("Arial", 14, "bold")).pack(anchor="w", pady=5)

        # Fila 1 de checkboxes
        frame1 = ttk.Frame(checkboxes_frame)
        frame1.pack(fill="x", pady=2)
        ttk.Checkbutton(frame1, text="Seno (MP)", variable=self.mostrar_seno, 
                       command=self.actualizar_reloj).pack(side="left", padx=5)
        ttk.Checkbutton(frame1, text="Coseno (OM)", variable=self.mostrar_coseno, 
                       command=self.actualizar_reloj).pack(side="left", padx=5)

        # Fila 2 de checkboxes
        frame2 = ttk.Frame(checkboxes_frame)
        frame2.pack(fill="x", pady=2)
        ttk.Checkbutton(frame2, text="Tangente (AQ)", variable=self.mostrar_tangente, 
                       command=self.actualizar_reloj).pack(side="left", padx=5)
        ttk.Checkbutton(frame2, text="Cotangente (BR)", variable=self.mostrar_cotangente, 
                       command=self.actualizar_reloj).pack(side="left", padx=5)

        # Fila 3 de checkboxes
        frame3 = ttk.Frame(checkboxes_frame)
        frame3.pack(fill="x", pady=2)
        ttk.Checkbutton(frame3, text="Secante (OQ)", variable=self.mostrar_secante, 
                       command=self.actualizar_reloj).pack(side="left", padx=5)
        ttk.Checkbutton(frame3, text="Cosecante (OR)", variable=self.mostrar_cosecante, 
                       command=self.actualizar_reloj).pack(side="left", padx=5)

        # Fila 4 de checkboxes
        frame4 = ttk.Frame(checkboxes_frame)
        frame4.pack(fill="x", pady=2)
        ttk.Checkbutton(frame4, text="Triángulo", variable=self.mostrar_triangulo, 
                       command=self.actualizar_reloj).pack(side="left", padx=5)
        ttk.Checkbutton(frame4, text="Manecilla Hora", variable=self.mostrar_manecilla_hora, 
                       command=self.actualizar_reloj).pack(side="left", padx=5)

        # Fila 5 de checkboxes
        frame5 = ttk.Frame(checkboxes_frame)
        frame5.pack(fill="x", pady=2)
        ttk.Checkbutton(frame5, text="Manecilla Minuto", variable=self.mostrar_manecilla_minuto, 
                       command=self.actualizar_reloj).pack(side="left", padx=5)
        ttk.Checkbutton(frame5, text="Onda Seno", variable=self.mostrar_onda_seno, 
                       command=self.actualizar_reloj).pack(side="left", padx=5)

        # Fila 6 de checkboxes
        frame6 = ttk.Frame(checkboxes_frame)
        frame6.pack(fill="x", pady=2)
        ttk.Checkbutton(frame6, text="Onda Coseno", variable=self.mostrar_onda_coseno, 
                       command=self.actualizar_reloj).pack(side="left", padx=5)

        # Figura con DOS subplots: reloj arriba, ondas abajo - MÁS GRANDES
        self.fig, (self.ax, self.ax_wave) = plt.subplots(2, 1, figsize=(10, 12))
        
        # Configuración del reloj (arriba) - MÁS GRANDE
        self.ax.set_aspect("equal")
        self.ax.set_xlim(-2.0, 2.0)  # Más espacio
        self.ax.set_ylim(-2.0, 2.0)  # Más espacio
        self.ax.axhline(0, color="black", linewidth=1, alpha=0.5)
        self.ax.axvline(0, color="black", linewidth=1, alpha=0.5)
        self.ax.grid(alpha=0.2, linestyle='-', linewidth=0.5)
        self.ax.set_xlabel("Eje X", fontsize=12)
        self.ax.set_ylabel("Eje Y", fontsize=12)
        self.ax.set_title("Big Ben — Reloj Trigonométrico Completo", fontsize=16, fontweight="bold")

        # Configuración del gráfico de ondas (abajo) - MÁS GRANDE
        self.ax_wave.set_xlim(0, 720)
        self.ax_wave.set_ylim(-1.5, 1.5)
        self.ax_wave.grid(alpha=0.3)
        self.ax_wave.set_xlabel("Tiempo (minutos)", fontsize=12)
        self.ax_wave.set_ylabel("Valor", fontsize=12)
        self.ax_wave.set_title("Funciones Trigonométricas vs Tiempo", fontsize=14, fontweight="bold")

        # Dibujar ejes de tangente y cotangente
        self.ax.axvline(1, color='gray', alpha=0.3, linestyle='-', linewidth=1)
        self.ax.axhline(1, color='gray', alpha=0.3, linestyle='-', linewidth=1)

        # círculo unitario
        circ = plt.Circle((0, 0), 1, fill=False, linewidth=3, color='black')
        self.ax.add_patch(circ)

        # Números del reloj más grandes
        for h in range(1, 13):
            ang = np.radians(90 - h * 30)
            x = np.cos(ang) * 0.85
            y = np.sin(ang) * 0.85
            self.ax.text(x, y, str(h), fontsize=24, ha="center", va="center", 
                        fontweight='bold', color='darkblue')

        # manecillas
        self.hour_hand, = self.ax.plot([0, 0], [0, 0], lw=8, color="#b5302b")
        self.min_hand, = self.ax.plot([0, 0], [0, 0], lw=5, color="#2b4fb5")

        # canvas tk
        self.canvas = FigureCanvasTkAgg(self.fig, master=left_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Controles en el lado derecho
        controls_container = ttk.Frame(right_frame)
        controls_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # slider tiempo
        slider_frame = ttk.Frame(controls_container)
        slider_frame.pack(fill="x", pady=15)
        
        ttk.Label(slider_frame, text="Tiempo (minutos)", font=("Arial", 14, "bold")).pack(pady=5)
        self.slider = ttk.Scale(slider_frame, from_=0, to=720, orient="horizontal", 
                               command=self.actualizar_reloj, length=250)
        self.slider.pack(fill="x", pady=5)

        # info labels
        info_frame = ttk.Frame(controls_container)
        info_frame.pack(fill="x", pady=15)
        
        self.lbl_hora = tk.Label(info_frame, text="", font=("Arial", 16, "bold"), fg="darkblue")
        self.lbl_hora.pack(pady=8)
        self.lbl_trig = tk.Label(info_frame, text="", font=("Arial", 12), justify=tk.LEFT)
        self.lbl_trig.pack(pady=5)

        # play / pause / step
        ctl_frame = ttk.Frame(controls_container)
        ctl_frame.pack(fill="x", pady=20)
        
        self.playing = False
        self.anim_speed = 0.9

        self.play_btn = ttk.Button(ctl_frame, text="▶ Play", command=self.toggle_play, width=20)
        self.play_btn.pack(pady=8)
        ttk.Button(ctl_frame, text="⏭ Step +1min", command=self.step_minute, width=20).pack(pady=8)
        ttk.Button(ctl_frame, text="⏭ Step +5min", command=lambda: self.step_minute(5), width=20).pack(pady=8)
        ttk.Button(ctl_frame, text="⏭ Step +60min", command=lambda: self.step_minute(60), width=20).pack(pady=8)

        # botones de acción
        action_frame = ttk.Frame(controls_container)
        action_frame.pack(fill="x", pady=20)
        
        ttk.Button(action_frame, text="Mostrar gráfica completa", 
                  command=self.mostrar_grafica_mov, width=25).pack(pady=8)
        ttk.Button(action_frame, text="Guardar imagen del reloj", 
                  command=self.guardar_imagen_reloj, width=25).pack(pady=8)
        ttk.Button(action_frame, text="Zoom Reset", 
                  command=self.reset_zoom, width=25).pack(pady=8)

        # botones de navegación
        nav_frame = ttk.Frame(controls_container)
        nav_frame.pack(fill="x", pady=20)
        
        ttk.Button(nav_frame, text="Regresar al menú", 
                  command=self.win.destroy, width=20).pack(pady=8)
        ttk.Button(nav_frame, text="Salir del programa", 
                  command=self.menu_root.destroy, width=20).pack(pady=8)

        # Elementos gráficos dinámicos
        self.point = None
        self.line_radius = None
        self.line_seno = None
        self.line_coseno = None
        self.line_tangente = None
        self.line_cotangente = None
        self.line_secante = None
        self.line_cosecante = None
        self.triangle = None
        self.text_info = None
        self.sin_wave_line = None
        self.cos_wave_line = None
        self.current_time_line = None
        
        # NUEVAS VARIABLES PARA LOS TEXTOS - PARA EVITAR DUPLICADOS
        self.sin_text = None
        self.cos_text = None
        self.tan_text = None
        self.cot_text = None
        self.sec_text = None
        self.csc_text = None

        # Eventos para interactividad
        self.fig.canvas.mpl_connect("scroll_event", self._zoom_handler)
        self.press = None
        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self._on_press)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self._on_release)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event', self._on_motion)

        # iniciar
        self.actualizar_reloj(0)

    def actualizar_reloj(self, value):
        t = float(value)

        # ángulos
        ang_hour = (t / 60) * 30  # 30 grados por hora
        ang_min = t * 6  # 6 grados por minuto

        rad_hour = np.radians(90 - ang_hour)
        rad_min = np.radians(90 - ang_min)

        # Coordenadas de las manecillas
        xh, yh = np.cos(rad_hour) * 0.55, np.sin(rad_hour) * 0.55
        xm, ym = np.cos(rad_min) * 0.90, np.sin(rad_min) * 0.90

        # actualizar manecillas
        if self.mostrar_manecilla_hora.get():
            self.hour_hand.set_data([0, xh], [0, yh])
            self.hour_hand.set_visible(True)
        else:
            self.hour_hand.set_visible(False)

        if self.mostrar_manecilla_minuto.get():
            self.min_hand.set_data([0, xm], [0, ym])
            self.min_hand.set_visible(True)
        else:
            self.min_hand.set_visible(False)

        # Limpiar elementos anteriores
        elements = [self.point, self.line_radius, self.line_seno, self.line_coseno,
                   self.line_tangente, self.line_cotangente, self.line_secante,
                   self.line_cosecante, self.triangle]
        
        for element in elements:
            if element is not None:
                try:
                    element.remove()
                except:
                    pass

        # Limpiar textos anteriores - SOLO LOS TEXTOS ESPECÍFICOS
        text_elements = [self.sin_text, self.cos_text, self.tan_text, 
                        self.cot_text, self.sec_text, self.csc_text]
        for text_element in text_elements:
            if text_element is not None:
                try:
                    text_element.remove()
                except:
                    pass
        
        # Reinicializar las variables de texto
        self.sin_text = None
        self.cos_text = None
        self.tan_text = None
        self.cot_text = None
        self.sec_text = None
        self.csc_text = None

        # punto en unidad (usando ángulo de la manecilla de hora)
        x_unit = np.cos(rad_hour)
        y_unit = np.sin(rad_hour)

        # Radio (siempre visible)
        self.line_radius, = self.ax.plot([0, x_unit], [0, y_unit], "-", color="black", lw=2, zorder=5)

        # Punto en la circunferencia
        self.point, = self.ax.plot(x_unit, y_unit, "o", color="red", markersize=10, zorder=10)

        # SENO (MP) - Proyección vertical
        if self.mostrar_seno.get():
            self.line_seno, = self.ax.plot([x_unit, x_unit], [0, y_unit], "--", color="green", lw=3, zorder=4)
            # SOLO UNA CAJA DE TEXTO PARA SENO
            self.sin_text = self.ax.text(x_unit + 0.1, y_unit/2, f"sin={y_unit:.3f}", color="green", fontsize=11,
                        bbox=dict(facecolor='white', alpha=0.8))

        # COSENO (OM) - Proyección horizontal
        if self.mostrar_coseno.get():
            self.line_coseno, = self.ax.plot([0, x_unit], [y_unit, y_unit], "--", color="blue", lw=3, zorder=4)
            # SOLO UNA CAJA DE TEXTO PARA COSENO
            self.cos_text = self.ax.text(x_unit/2, y_unit + 0.1, f"cos={x_unit:.3f}", color="blue", fontsize=11,
                        bbox=dict(facecolor='white', alpha=0.8))

        # TANGENTE (AQ)
        if self.mostrar_tangente.get() and abs(x_unit) > 1e-10:
            tan_val = y_unit / x_unit
            qx, qy = 1, tan_val
            if abs(tan_val) <= 2.0:
                self.line_tangente, = self.ax.plot([x_unit, qx], [y_unit, qy], "--", color="orange", lw=2, zorder=4)
                self.ax.plot(qx, qy, 'o', color="orange", markersize=6)
                # SOLO UNA CAJA DE TEXTO PARA TANGENTE
                self.tan_text = self.ax.text(qx + 0.1, qy, f"tan={tan_val:.3f}", color="orange", fontsize=10,
                            bbox=dict(facecolor='white', alpha=0.7))

        # COTANGENTE (BR)
        if self.mostrar_cotangente.get() and abs(y_unit) > 1e-10:
            cot_val = x_unit / y_unit
            rx, ry = cot_val, 1
            if abs(cot_val) <= 2.0:
                self.line_cotangente, = self.ax.plot([x_unit, rx], [y_unit, ry], "--", color="purple", lw=2, zorder=4)
                self.ax.plot(rx, ry, 'o', color="purple", markersize=6)
                # SOLO UNA CAJA DE TEXTO PARA COTANGENTE
                self.cot_text = self.ax.text(rx, ry + 0.1, f"cot={cot_val:.3f}", color="purple", fontsize=10,
                            bbox=dict(facecolor='white', alpha=0.7))

        # SECANTE (OQ)
        if self.mostrar_secante.get() and abs(x_unit) > 1e-10:
            sec_val = 1 / x_unit
            self.line_secante, = self.ax.plot([0, 1], [0, sec_val], "--", color="brown", lw=2, zorder=3)
            # SOLO UNA CAJA DE TEXTO PARA SECANTE
            self.sec_text = self.ax.text(0.5, sec_val/2 + 0.2, f"sec={sec_val:.3f}", color="brown", fontsize=10,
                        bbox=dict(facecolor='white', alpha=0.7))

        # COSECANTE (OR)
        if self.mostrar_cosecante.get() and abs(y_unit) > 1e-10:
            csc_val = 1 / y_unit
            self.line_cosecante, = self.ax.plot([0, csc_val], [0, 1], "--", color="pink", lw=2, zorder=3)
            # SOLO UNA CAJA DE TEXTO PARA COSECANTE
            self.csc_text = self.ax.text(csc_val/2, 0.5, f"csc={csc_val:.3f}", color="pink", fontsize=10,
                        bbox=dict(facecolor='white', alpha=0.7))

        # TRIÁNGULO RECTÁNGULO
        if self.mostrar_triangulo.get():
            triangle_x = [0, x_unit, x_unit]
            triangle_y = [0, 0, y_unit]
            self.triangle = self.ax.fill(triangle_x, triangle_y, alpha=0.2, color='gray')[0]

        # ACTUALIZAR GRÁFICA DE ONDAS
        self.ax_wave.clear()
        self.ax_wave.set_xlim(0, 720)
        self.ax_wave.set_ylim(-1.5, 1.5)
        self.ax_wave.grid(alpha=0.3)
        self.ax_wave.set_xlabel("Tiempo (minutos)", fontsize=12)
        self.ax_wave.set_ylabel("Valor", fontsize=12)
        self.ax_wave.set_title("Funciones Trigonométricas vs Tiempo", fontsize=14, fontweight="bold")

        # Dibujar ondas según checkboxes
        t_complete = np.linspace(0, 720, 1000)
        ang_complete = (t_complete / 60) * 30
        rad_complete = np.radians(ang_complete)
        
        if self.mostrar_onda_seno.get():
            sin_complete = np.sin(rad_complete)
            self.ax_wave.plot(t_complete, sin_complete, 'g-', lw=2, alpha=0.8, label='sin(θ)')
        
        if self.mostrar_onda_coseno.get():
            cos_complete = np.cos(rad_complete)
            self.ax_wave.plot(t_complete, cos_complete, 'b-', lw=2, alpha=0.8, label='cos(θ)')
        
        self.ax_wave.legend()

        # Línea vertical del tiempo actual
        self.current_time_line = self.ax_wave.axvline(t, color='red', linestyle='--', alpha=0.9, lw=3)

        # INFORMACIÓN NUMÉRICA - ACTUALIZAR EN LUGAR DE CREAR NUEVO
        if self.text_info is not None:
            try:
                self.text_info.remove()
            except:
                pass
        
        info_text = f"Ángulo: {ang_hour:.1f}°\n"
        info_text += f"sin(θ) = {y_unit:.3f}\n"
        info_text += f"cos(θ) = {x_unit:.3f}\n"
        if abs(x_unit) > 1e-10:
            info_text += f"tan(θ) = {y_unit/x_unit:.3f}\n"
        if abs(y_unit) > 1e-10:
            info_text += f"cot(θ) = {x_unit/y_unit:.3f}\n"
        if abs(x_unit) > 1e-10:
            info_text += f"sec(θ) = {1/x_unit:.3f}\n"
        if abs(y_unit) > 1e-10:
            info_text += f"csc(θ) = {1/y_unit:.3f}"

        self.text_info = self.ax.text(-1.9, 1.8, info_text, fontsize=12,
                                     bbox=dict(facecolor="white", alpha=0.95, edgecolor='black'),
                                     verticalalignment='top')

        # labels de información
        h = int(t // 60)
        m = int(t % 60)
        self.lbl_hora.config(text=f"Hora: {h:02d}:{m:02d}")
        trig_text = f"Ángulo: {ang_hour:.2f}°\nRad: {np.radians(ang_hour):.3f}\n"
        trig_text += f"sin = {y_unit:.3f}\ncos = {x_unit:.3f}"
        self.lbl_trig.config(text=trig_text)

        self.canvas.draw_idle()

    def toggle_play(self):
        if self.playing:
            self.playing = False
            self.play_btn.config(text="▶ Play")
        else:
            self.playing = True
            self.play_btn.config(text="⏸ Pause")
            self._animate_step()

    def _animate_step(self):
        if not self.playing:
            return
        current = self.slider.get()
        nxt = (current + 1) % 720
        self.slider.set(nxt)
        self.actualizar_reloj(nxt)
        self.win.after(int(self.anim_speed * 1000), self._animate_step)

    def step_minute(self, minutes=1):
        current = self.slider.get()
        nxt = (current + minutes) % 720
        self.slider.set(nxt)
        self.actualizar_reloj(nxt)

    def mostrar_grafica_mov(self):
        t = np.linspace(0, 720, 2000)
        ang = (t / 60) * 30
        rad = np.radians(ang)
        sin_vals = np.sin(rad)
        cos_vals = np.cos(rad)

        fig, ax = plt.subplots(figsize=(14, 8))
        ax.plot(t, sin_vals, label="sin(θ(t))", lw=3)
        ax.plot(t, cos_vals, label="cos(θ(t))", lw=3)
        
        current_t = self.slider.get()
        ax.axvline(x=current_t, color='red', linestyle='--', alpha=0.8, lw=2, label='Tiempo actual')
        
        ax.set_title("Movimiento de la manecilla - Funciones Trigonométricas", fontsize=18, fontweight="bold")
        ax.set_xlabel("Tiempo (min)", fontsize=14)
        ax.set_ylabel("Valor trigonométrico", fontsize=14)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=12)
        plt.show()

    def guardar_imagen_reloj(self):
        fname = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG image", "*.png"), ("All files", "*.*")],
                                             initialfile="bigben_trigonometrico.png")
        if not fname:
            return
        self.fig.savefig(fname, dpi=300, bbox_inches='tight')
        messagebox.showinfo("Guardado", f"Imagen guardada en:\n{fname}")

    def reset_zoom(self):
        self.ax.set_xlim(-2.0, 2.0)
        self.ax.set_ylim(-2.0, 2.0)
        self.canvas.draw_idle()

    def _zoom(self, factor):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        center_x = (cur_xlim[0] + cur_xlim[1]) / 2
        center_y = (cur_ylim[0] + cur_ylim[1]) / 2
        
        width = (cur_xlim[1] - cur_xlim[0]) * factor
        height = (cur_ylim[1] - cur_ylim[0]) * factor
        
        self.ax.set_xlim([center_x - width/2, center_x + width/2])
        self.ax.set_ylim([center_y - height/2, center_y + height/2])
        self.canvas.draw_idle()

    def _zoom_handler(self, event):
        if event.inaxes != self.ax:
            return
            
        base_scale = 1.1
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            return

        self._zoom(scale_factor)

    def _on_press(self, event):
        if event.button != 1 or event.inaxes != self.ax:
            return
        self.press = (event.x, event.y, self.ax.get_xlim(), self.ax.get_ylim())

    def _on_release(self, event):
        self.press = None

    def _on_motion(self, event):
        if self.press is None or event.button != 1 or event.inaxes != self.ax:
            return
        xpress, ypress, (x0, x1), (y0, y1) = self.press
        dx = event.x - xpress
        dy = event.y - ypress
        width = self.canvas.get_tk_widget().winfo_width()
        height = self.canvas.get_tk_widget().winfo_height()
        if width == 0 or height == 0:
            return
        dx_data = -dx * (x1 - x0) / width
        dy_data = dy * (y1 - y0) / height
        self.ax.set_xlim(x0 + dx_data, x1 + dx_data)
        self.ax.set_ylim(y0 + dy_data, y1 + dy_data)
        self.canvas.draw_idle()
# ---------------------------
# MAIN
# ---------------------------
def main():
    root = tk.Tk()
    app = MenuPrincipal(root)
    root.mainloop()

if __name__ == "__main__":
    main()