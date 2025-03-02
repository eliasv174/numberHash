import random
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(script_dir, "numeros.txt") 

NUM_COUNT = 10_000_000
MIN_NUM = -50_000_000
MAX_NUM = 50_000_000

class NumerosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Buscador de Números")
        self.conjunto_numeros = None
        self.loading = False
        self.generating = False
        
        # Configurar interfaz
        self.create_widgets()
        self.check_file_exists()
    
    def create_widgets(self):
        # Marco principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Botones
        self.btn_generar = ttk.Button(
            main_frame, 
            text="Generar Números", 
            command=self.iniciar_generacion
        )
        self.btn_generar.pack(pady=5, fill=tk.X)
        
        # Buscador
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(pady=10, fill=tk.X)
        
        self.entrada_numero = ttk.Entry(search_frame)
        self.entrada_numero.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.btn_buscar = ttk.Button(
            search_frame, 
            text="Buscar", 
            command=self.iniciar_busqueda,
            state=tk.DISABLED
        )
        self.btn_buscar.pack(side=tk.LEFT)
        
        # Estado
        self.lbl_estado = ttk.Label(main_frame, text="", foreground="gray")
        self.lbl_estado.pack(pady=5)
        
        # Resultado
        self.lbl_resultado = ttk.Label(main_frame, text="", font=('Helvetica', 12))
        self.lbl_resultado.pack(pady=10)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
    
    def check_file_exists(self):
        if os.path.exists(FILE_NAME):
            self.btn_buscar.config(state=tk.NORMAL)
        else:
            self.btn_buscar.config(state=tk.DISABLED)
    
    def actualizar_estado(self, texto):
        self.lbl_estado.config(text=texto)
    
    def iniciar_generacion(self):
        if self.generating:
            return
        
        self.generating = True
        self.btn_generar.config(state=tk.DISABLED)
        self.actualizar_estado("Generando números...")
        self.progress.pack(pady=5)
        self.progress.start()
        
        threading.Thread(target=self.generar_numeros).start()
    
    def generar_numeros(self):
        try:
            with open(FILE_NAME, 'w') as archivo:
                for _ in range(NUM_COUNT):
                    num = random.randint(MIN_NUM, MAX_NUM)
                    archivo.write(f"{num}\n")
            
            self.root.after(0, self.generacion_completada)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    
    def generacion_completada(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_generar.config(state=tk.NORMAL)
        self.actualizar_estado(f"{NUM_COUNT} números generados!")
        self.generating = False
        self.check_file_exists()
    
    def iniciar_busqueda(self):
        if self.loading or not self.conjunto_numeros:
            self.cargar_numeros_en_background()
            return
        
        self.realizar_busqueda()
    
    def cargar_numeros_en_background(self):
        if self.loading:
            return
        
        self.loading = True
        self.actualizar_estado("Cargando números en memoria...")
        self.progress.pack(pady=5)
        self.progress.start()
        self.btn_buscar.config(state=tk.DISABLED)
        
        threading.Thread(target=self.cargar_numeros).start()
    
    def cargar_numeros(self):
        try:
            with open(FILE_NAME, 'r') as archivo:
                self.conjunto_numeros = set(int(linea.strip()) for linea in archivo)
            
            self.root.after(0, self.carga_completada)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    
    def carga_completada(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_buscar.config(state=tk.NORMAL)
        self.actualizar_estado("Números cargados en memoria")
        self.loading = False
        self.realizar_busqueda()
    
    def realizar_busqueda(self):
        try:
            numero = int(self.entrada_numero.get())
            
            # Medición de alta precisión con múltiples iteraciones
            inicio = time.perf_counter_ns()
            
            # Realizar múltiples búsquedas para medir tiempos pequeños
            for _ in range(1_000_000):
                existe = numero in self.conjunto_numeros
            
            fin = time.perf_counter_ns()
            
            # Calcular tiempo total y por operación
            tiempo_total_ns = fin - inicio
            tiempo_por_operacion_ns = tiempo_total_ns / 1_000_000
            tiempo_por_operacion_seg = tiempo_por_operacion_ns / 1e9
            
            resultado = (f"¡Número Encontrado! ({tiempo_por_operacion_seg:.3e} seg)" 
                        if existe else 
                        f"Numero no existe ({tiempo_por_operacion_seg:.3e} seg)")
            
            color = "green" if existe else "red"
            self.lbl_resultado.config(text=resultado, foreground=color)
        
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = NumerosApp(root)
    root.mainloop()