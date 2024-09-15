import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import chardet
from ttkthemes import ThemedTk

def detectar_codificacao(arquivo):
    with open(arquivo, 'rb') as f:
        resultado = chardet.detect(f.read())
    return resultado['encoding']

def carregar_produtos(arquivo):
    produtos = {}
    codificacao = detectar_codificacao(arquivo)
    with open(arquivo, 'r', encoding=codificacao) as f:
        leitor = csv.reader(f, delimiter=',')
        for linha in leitor:
            if len(linha) == 3:
                codigo, nome, preco = linha
                produtos[codigo] = {'nome': nome, 'preco': float(preco)}
                produtos[nome.lower()] = {'codigo': codigo, 'preco': float(preco)}
    return produtos

def pesquisar_produto(produtos, termo, filtro_preco=None):
    termo = termo.lower()
    resultados = []
    for chave, valor in produtos.items():
        if termo in chave.lower():
            if 'nome' in valor:  # É um código de barras
                item = (valor['nome'], chave, valor['preco'])
            else:  # É um nome de produto
                item = (chave, valor['codigo'], valor['preco'])
            
            if filtro_preco:
                min_preco, max_preco = filtro_preco
                if min_preco <= item[2] <= max_preco:
                    resultados.append(item)
            else:
                resultados.append(item)
    return resultados

class AppPesquisaProdutos:
    def __init__(self, master):
        self.master = master
        self.master.title("Pesquisa de Produtos")
        self.master.geometry("900x700")
        
        self.style = ttk.Style(self.master)
        self.style.theme_use('equilux')

        self.produtos = {}
        self.arquivo_atual = None
        self.tema_escuro = True

        self.criar_widgets()
        self.criar_menu()

    def criar_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo = ttk.Label(main_frame, text="Pesquisa de Produtos", font=('Helvetica', 18, 'bold'))
        titulo.pack(pady=(0, 20))

        # Frame de pesquisa
        frame_pesquisa = ttk.Frame(main_frame)
        frame_pesquisa.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(frame_pesquisa, text="Pesquisar:", font=('Helvetica', 12)).pack(side=tk.LEFT)
        self.entrada_pesquisa = ttk.Entry(frame_pesquisa, width=50, font=('Helvetica', 12))
        self.entrada_pesquisa.pack(side=tk.LEFT, padx=10)
        self.entrada_pesquisa.bind('<KeyRelease>', self.pesquisa_tempo_real)

        # Frame de filtros
        frame_filtros = ttk.Frame(main_frame)
        frame_filtros.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(frame_filtros, text="Filtrar por preço:", font=('Helvetica', 12)).pack(side=tk.LEFT)
        self.min_preco = ttk.Entry(frame_filtros, width=10, font=('Helvetica', 12))
        self.min_preco.pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_filtros, text="até", font=('Helvetica', 12)).pack(side=tk.LEFT)
        self.max_preco = ttk.Entry(frame_filtros, width=10, font=('Helvetica', 12))
        self.max_preco.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_filtros, text="Aplicar Filtro", command=self.aplicar_filtro).pack(side=tk.LEFT, padx=10)

        # Frame para a Treeview
        frame_tree = ttk.Frame(main_frame)
        frame_tree.pack(fill=tk.BOTH, expand=True)

        # Treeview para resultados
        self.tree = ttk.Treeview(frame_tree, columns=('Nome', 'Código', 'Preço'), show='headings')
        self.tree.heading('Nome', text='Nome', command=lambda: self.ordenar_coluna('Nome', False))
        self.tree.heading('Código', text='Código de Barras', command=lambda: self.ordenar_coluna('Código', False))
        self.tree.heading('Preço', text='Preço', command=lambda: self.ordenar_coluna('Preço', False))
        self.tree.column('Nome', width=300)
        self.tree.column('Código', width=200)
        self.tree.column('Preço', width=100)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Frame de estatísticas
        frame_stats = ttk.Frame(main_frame)
        frame_stats.pack(fill=tk.X, pady=(20, 0))

        self.label_total = ttk.Label(frame_stats, text="Total de produtos: 0", font=('Helvetica', 10))
        self.label_total.pack(side=tk.LEFT, padx=(0, 20))

        self.label_media = ttk.Label(frame_stats, text="Preço médio: R$ 0.00", font=('Helvetica', 10))
        self.label_media.pack(side=tk.LEFT)

        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Pronto para pesquisar", font=('Helvetica', 10))
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    def criar_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Abrir arquivo de produtos", command=self.abrir_arquivo)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.master.quit)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualização", menu=view_menu)
        view_menu.add_command(label="Alternar Tema", command=self.alternar_tema)

    def abrir_arquivo(self):
        filename = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")])
        if filename:
            try:
                self.produtos = carregar_produtos(filename)
                self.arquivo_atual = filename
                self.atualizar_estatisticas()
                self.status_bar.config(text=f"Arquivo carregado: {filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível carregar o arquivo: {str(e)}")

    def pesquisa_tempo_real(self, event):
        self.buscar()

    def buscar(self):
        termo = self.entrada_pesquisa.get()
        filtro_preco = self.obter_filtro_preco()

        for i in self.tree.get_children():
            self.tree.delete(i)

        if termo:
            resultados = pesquisar_produto(self.produtos, termo, filtro_preco)

            if resultados:
                for nome, codigo, preco in resultados:
                    self.tree.insert('', tk.END, values=(nome, codigo, f"R$ {preco:.2f}"))
                self.status_bar.config(text=f"{len(resultados)} produto(s) encontrado(s)")
            else:
                self.tree.insert('', tk.END, values=("Nenhum produto encontrado", "", ""))
                self.status_bar.config(text="Nenhum produto encontrado")
        else:
            self.status_bar.config(text="Digite um termo para pesquisar")

    def aplicar_filtro(self):
        self.buscar()

    def obter_filtro_preco(self):
        try:
            min_preco = float(self.min_preco.get()) if self.min_preco.get() else 0
            max_preco = float(self.max_preco.get()) if self.max_preco.get() else float('inf')
            return (min_preco, max_preco)
        except ValueError:
            messagebox.showwarning("Aviso", "Valores de preço inválidos. O filtro será ignorado.")
            return None

    def ordenar_coluna(self, coluna, reverso):
        l = [(self.tree.set(k, coluna), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverso)

        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        self.tree.heading(coluna, command=lambda: self.ordenar_coluna(coluna, not reverso))

    def atualizar_estatisticas(self):
        total_produtos = len(self.produtos) // 2  # Dividido por 2 porque cada produto está armazenado duas vezes
        preco_medio = sum(p['preco'] for p in self.produtos.values() if 'preco' in p) / total_produtos

        self.label_total.config(text=f"Total de produtos: {total_produtos}")
        self.label_media.config(text=f"Preço médio: R$ {preco_medio:.2f}")

    def alternar_tema(self):
        if self.tema_escuro:
            self.style.theme_use('arc')
            self.tema_escuro = False
        else:
            self.style.theme_use('equilux')
            self.tema_escuro = True

def main():
    root = ThemedTk(theme="equilux")
    app = AppPesquisaProdutos(root)
    root.mainloop()

if __name__ == "__main__":
    main()