import tkinter as tk
from tkinter import ttk, messagebox
import code
import sys
import io
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Importando SymPy para o motor de Álgebra Simbólica e Cálculo (CAS)
import sympy as sp

REFERENCES = {
    "Operações matemáticas básicas": "Operações Básicas:\n\nSoma: 2 + 2\nSubtração: 5 - 3\nMultiplicação: 4 * 3\nDivisão: 10 / 2\nPotência: 2 ** 3\nResto: 10 % 3\n\nExemplo:\na = 10\nb = 20\nprint(a + b)",
    "Trabalhar com matrizes numéricas": "Matrizes (NumPy):\n\nCriar matriz: m = array([[1, 2], [3, 4]])\nCriar vetor: v = array([1, 2, 3])\nTransposta: m.T ou transpose(m)\nMultiplicação: m.dot(m)\nInversa: np.linalg.inv(m)\nSoma de matrizes: m + m\n\nExemplo:\nm = array([[1, 2], [3, 4]])\nm * 2",
    "Criar um gráfico": "Gráficos (Matplotlib):\n\nLinha: plot(x, y)\nDispersão: scatter(x, y)\nTítulo: title('Meu Gráfico')\nEixos: xlabel('X'), ylabel('Y')\nMostrar: show()\n\nExemplo:\nx = array([1, 2, 3, 4])\ny = array([1, 4, 9, 16])\nplot(x, y)\nshow()",
    "Gerar funções trigonométricas": "Trigonometria:\n\nSeno: sin(x)\nCosseno: cos(x)\nTangente: tan(x)\nPi: np.pi\nEspaço linear: linspace(inicio, fim, pontos)\n\nExemplo:\nx = linspace(0, 2*np.pi, 100)\ny = sin(x)\nplot(x, y)\nshow()",
    "Espaço livre": "Espaço Livre:\n\nAqui você pode usar qualquer comando Python, criar loops, importar bibliotecas disponíveis e combinar matrizes, gráficos e trigonometria como quiser. Todas as abas compartilham a mesma memória."
}

EXAMPLES = {
    "Operações matemáticas básicas": "a = 15; b = 30; print(f'Resultado da soma: {a + b}')",
    "Trabalhar com matrizes numéricas": "array([[10, 20], [30, 40]])",
    "Criar um gráfico": "t = array([1, 2, 3, 4, 5]); plot(t, t**2); title('Parábola'); show()",
    "Gerar funções trigonométricas": "x = linspace(0, 2*np.pi, 100); plot(x, sin(x)); title('Seno'); show()",
    "Espaço livre": "print('Ambiente livre pronto para uso!')"
}

class MathEngine:
    def __init__(self, root):
        self.root = root
        
        # Variáveis simbólicas globais para o GeoGebra/SymPy
        self.x, self.y, self.z = sp.symbols('x y z')
        
        self.locals_context = {
            'np': np,
            'plt': plt,
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'linspace': np.linspace,
            'array': np.array,
            'plot': plt.plot,
            'scatter': plt.scatter,
            'title': plt.title,
            'xlabel': plt.xlabel,
            'ylabel': plt.ylabel,
            'show': self.custom_show,
            # Injetando SymPy no console
            'sp': sp,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'diff': sp.diff,
            'integrate': sp.integrate,
            'solve': sp.solve,
            'factor': sp.factor,
            'expand': sp.expand,
            'limit': sp.limit
        }
        self.console = code.InteractiveConsole(locals=self.locals_context)
        plt.figure()

    def custom_show(self):
        fig = plt.gcf()
        if not fig.axes:
            return
        
        win = tk.Toplevel(self.root)
        win.title("Visualização: Plano Cartesiano")
        win.geometry("600x450")
        
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        plt.figure()

    def execute_command(self, command: str) -> str:
        try:
            obj = eval(command, self.locals_context)
            if isinstance(obj, np.ndarray):
                self.show_matrix_window(obj)
        except Exception:
            pass

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = sys.stdout = io.StringIO()
        sys.stderr = redirected_output

        try:
            needs_more = self.console.push(command)
            output = redirected_output.getvalue()
            if needs_more:
                return "... "
            return output
        except Exception as e:
            return str(e)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def show_matrix_window(self, matrix):
        win = tk.Toplevel(self.root)
        win.title(f"Visualização: Matriz {matrix.shape}")
        win.geometry("400x300")
        
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        if matrix.ndim == 1:
            matrix = matrix.reshape(1, -1)
            
        if matrix.ndim > 2:
            ttk.Label(frame, text="Matrizes com mais de 2 dimensões não são desenhadas graficamente.").pack()
            return

        rows, cols = matrix.shape
        for r in range(rows):
            for c in range(cols):
                val = matrix[r, c]
                if isinstance(val, (float, np.floating)):
                    val = round(val, 4)
                lbl = tk.Label(frame, text=str(val), borderwidth=1, relief="solid", bg="white", font=("Consolas", 12))
                lbl.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
        
        for r in range(rows):
            frame.grid_rowconfigure(r, weight=1)
        for c in range(cols):
            frame.grid_columnconfigure(c, weight=1)

class GeoGebraWindow:
    def __init__(self, parent, engine):
        self.win = tk.Toplevel(parent)
        self.win.title("Free Geogebra - Ferramentas Matemáticas")
        self.win.geometry("900x600")
        self.engine = engine
        self.x = engine.x
        
        self.notebook = ttk.Notebook(self.win)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_graficos_tab()
        self.create_geometria_tab()
        self.create_algebra_tab()
        self.create_calculo_tab()
        
    def create_graficos_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Gráficos e Funções")
        
        ttk.Label(tab, text="Calculadora Gráfica Rápida", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=5)
        ttk.Label(tab, text="Digite uma função f(x):").pack(anchor=tk.W)
        
        self.func_entry = ttk.Entry(tab, font=("Consolas", 12), width=50)
        self.func_entry.pack(anchor=tk.W, pady=5)
        
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(anchor=tk.W, pady=5)
        
        ttk.Button(btn_frame, text="Plotar Função", command=self.plot_function).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Analisar Pontos", command=self.analyze_function).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💡 Exemplo", command=lambda: self.set_entry(self.func_entry, "x**3 - 4*x")).pack(side=tk.LEFT, padx=20)
        
        self.graf_result = tk.Text(tab, height=10, bg="#f0f0f0", font=("Consolas", 11))
        self.graf_result.pack(fill=tk.BOTH, expand=True, pady=10)
        self.graf_result.insert(tk.END, ">> Análise aparecerá aqui.")
        
    def set_entry(self, entry_widget, text):
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, text)
        
    def plot_function(self):
        func_str = self.func_entry.get()
        try:
            expr = sp.sympify(func_str)
            f_np = sp.lambdify(self.x, expr, 'numpy')
            x_vals = np.linspace(-10, 10, 400)
            y_vals = f_np(x_vals)
            
            plt.figure()
            plt.plot(x_vals, y_vals, label=f'f(x) = {func_str}', color='blue')
            plt.axhline(0, color='black', linewidth=1)
            plt.axvline(0, color='black', linewidth=1)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.title('Calculadora Gráfica')
            plt.legend()
            self.engine.custom_show()
        except Exception as e:
            self.log_result(self.graf_result, f"Erro ao plotar: {e}")
            
    def analyze_function(self):
        func_str = self.func_entry.get()
        try:
            expr = sp.sympify(func_str)
            roots = sp.solve(expr, self.x)
            deriv = sp.diff(expr, self.x)
            crit_points = sp.solve(deriv, self.x)
            
            msg = f"Análise da Função: f(x) = {func_str}\n"
            msg += f"-> Raízes (Cortes no eixo X): {roots}\n"
            msg += f"-> Derivada f'(x): {deriv}\n"
            msg += f"-> Pontos Críticos (Máx/Mín/Inflexão em X): {crit_points}\n"
            self.log_result(self.graf_result, msg)
        except Exception as e:
            self.log_result(self.graf_result, f"Erro na análise: {e}")

    def create_geometria_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Geometria Plana (2D)")
        
        ttk.Label(tab, text="Construção e Medições Exatas", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=5)
        ttk.Label(tab, text="Exemplo: Desenhar um polígono e calcular área/perímetro.").pack(anchor=tk.W)
        
        desc = """Para recursos geométricos complexos:
1. Defina pontos: A = (0,0), B = (4,0), C = (0,3)
2. Medições (Teorema de Pitágoras automático).
Esta aba processa medições geométricas simuladas."""
        tk.Label(tab, text=desc, justify=tk.LEFT, font=("Consolas", 11)).pack(anchor=tk.W, pady=10)
        
        ttk.Button(tab, text="💡 Exemplo: Triângulo (3,4,5)", command=self.draw_triangle).pack(anchor=tk.W)
        
    def draw_triangle(self):
        plt.figure()
        pts = np.array([[0,0], [4,0], [0,3], [0,0]])
        plt.plot(pts[:,0], pts[:,1], marker='o', color='green')
        plt.fill(pts[:,0], pts[:,1], alpha=0.3, color='lightgreen')
        plt.text(2, -0.3, "Base = 4")
        plt.text(-0.5, 1.5, "Alt = 3")
        plt.text(2, 1.7, "Hipotenusa = 5")
        plt.title('Geometria: Triângulo Retângulo\nÁrea = 6 | Perímetro = 12')
        plt.grid(True)
        plt.axis('equal')
        self.engine.custom_show()

    def create_algebra_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Álgebra Simbólica (CAS)")
        
        ttk.Label(tab, text="Resolução de Equações e Fatoração", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=5)
        ttk.Label(tab, text="Expressão Algébrica ou Equação:").pack(anchor=tk.W)
        
        self.alg_entry = ttk.Entry(tab, font=("Consolas", 12), width=50)
        self.alg_entry.pack(anchor=tk.W, pady=5)
        
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(anchor=tk.W, pady=5)
        
        ttk.Button(btn_frame, text="Resolver (x)", command=lambda: self.run_cas('solve')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Fatorar", command=lambda: self.run_cas('factor')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Expandir", command=lambda: self.run_cas('expand')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💡 Exemplo", command=lambda: self.set_entry(self.alg_entry, "x**2 - 5*x + 6")).pack(side=tk.LEFT, padx=20)
        
        self.alg_result = tk.Text(tab, height=8, bg="#e8f4f8", font=("Consolas", 12))
        self.alg_result.pack(fill=tk.BOTH, expand=True, pady=10)

    def run_cas(self, action):
        expr_str = self.alg_entry.get()
        try:
            expr = sp.sympify(expr_str)
            if action == 'solve':
                res = sp.solve(expr, self.x)
                msg = f"Equação: {expr} = 0\nSoluções para x: {res}"
            elif action == 'factor':
                res = sp.factor(expr)
                msg = f"Expressão original: {expr}\nForma Fatorada: {res}"
            elif action == 'expand':
                res = sp.expand(expr)
                msg = f"Expressão original: {expr}\nForma Expandida: {res}"
            self.log_result(self.alg_result, msg)
        except Exception as e:
            self.log_result(self.alg_result, f"Erro Álgebra: {e}")

    def create_calculo_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Cálculo Avançado")
        
        ttk.Label(tab, text="Derivadas, Integrais e Limites", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=5)
        ttk.Label(tab, text="Função f(x):").pack(anchor=tk.W)
        
        self.calc_entry = ttk.Entry(tab, font=("Consolas", 12), width=50)
        self.calc_entry.pack(anchor=tk.W, pady=5)
        
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(anchor=tk.W, pady=5)
        
        ttk.Button(btn_frame, text="Calcular Derivada d/dx", command=lambda: self.run_calc('diff')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Integral Indefinida ∫", command=lambda: self.run_calc('int')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💡 Exemplo", command=lambda: self.set_entry(self.calc_entry, "sin(x) * exp(x)")).pack(side=tk.LEFT, padx=20)
        
        self.calc_result = tk.Text(tab, height=8, bg="#fcf5e3", font=("Consolas", 12))
        self.calc_result.pack(fill=tk.BOTH, expand=True, pady=10)

    def run_calc(self, action):
        expr_str = self.calc_entry.get()
        try:
            expr = sp.sympify(expr_str)
            if action == 'diff':
                res = sp.diff(expr, self.x)
                msg = f"f(x) = {expr}\n\nDerivada f'(x) = {res}"
            elif action == 'int':
                res = sp.integrate(expr, self.x)
                msg = f"f(x) = {expr}\n\nIntegral ∫f(x)dx = {res} + C"
            self.log_result(self.calc_result, msg)
        except Exception as e:
            self.log_result(self.calc_result, f"Erro Cálculo: {e}")

    def log_result(self, widget, text):
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)

class HarmonicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyHarmonic - Computação & GeoGebra Integrado")
        self.root.geometry("1000x650")
        
        self.engine = MathEngine(root)
        self.setup_ui()

    def setup_ui(self):
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        self.menu_frame = ttk.Frame(self.paned, width=250, relief=tk.SUNKEN, padding=5)
        self.paned.add(self.menu_frame, weight=0)
        
        ttk.Label(self.menu_frame, text="Ambientes Numéricos", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.notebook = ttk.Notebook(self.paned)
        self.paned.add(self.notebook, weight=1)
        
        self.tabs = {}
        
        for name in REFERENCES.keys():
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=name)
            self.setup_tab(tab, name)
            self.tabs[name] = tab
            
            btn = ttk.Button(self.menu_frame, text=name, command=lambda n=name: self.select_tab(n))
            btn.pack(fill=tk.X, padx=5, pady=2)
            
        ttk.Separator(self.menu_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        ttk.Label(self.menu_frame, text="Módulos Avançados", font=("Arial", 12, "bold")).pack(pady=5)
        btn_geo = tk.Button(self.menu_frame, text="🌟 Free Geogebra", bg="#4285F4", fg="white", font=("Arial", 10, "bold"), command=self.open_geogebra)
        btn_geo.pack(fill=tk.X, padx=5, pady=5, ipady=5)

    def select_tab(self, name):
        self.notebook.select(self.tabs[name])

    def setup_tab(self, tab, name):
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text=name, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        entry_var = tk.StringVar()
        
        # Botões do Topo
        ref_btn = ttk.Button(top_frame, text="📖 Referência", command=lambda: self.show_reference(name))
        ref_btn.pack(side=tk.RIGHT, padx=5)
        
        ex_btn = ttk.Button(top_frame, text="💡 Exemplo", command=lambda: entry_var.set(EXAMPLES.get(name, "")))
        ex_btn.pack(side=tk.RIGHT, padx=5)
        
        output_text = tk.Text(tab, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 12))
        output_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        output_text.config(state=tk.DISABLED)
        
        input_frame = ttk.Frame(tab)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text=">>", font=("Consolas", 12)).pack(side=tk.LEFT)
        entry = tk.Entry(input_frame, textvariable=entry_var, font=("Consolas", 12))
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        entry.bind("<Return>", lambda event, e=entry_var, o=output_text: self.process_command(e, o))
        self.print_to_console(output_text, f"Ambiente de {name} carregado.\n>> ")

    def open_geogebra(self):
        GeoGebraWindow(self.root, self.engine)

    def show_reference(self, name):
        messagebox.showinfo(f"Referência: {name}", REFERENCES[name])

    def print_to_console(self, text_widget, text: str):
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, text)
        text_widget.see(tk.END)
        text_widget.config(state=tk.DISABLED)

    def process_command(self, entry_var, output_text):
        cmd = entry_var.get()
        if not cmd.strip(): return
        
        self.print_to_console(output_text, f"{cmd}\n")
        entry_var.set("")
        
        result = self.engine.execute_command(cmd)
        if result:
            self.print_to_console(output_text, f"{result}\n")
        
        self.print_to_console(output_text, ">> ")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
    app = HarmonicApp(root)
    root.mainloop()
