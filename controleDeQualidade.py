import pandas as pd
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def estatisticas(itens_validos, itens_invalidos, total_pecas):
    quantidade_validos = len(itens_validos)
    quantidade_invalidos = len(itens_invalidos)
    
    percentual_validos = (quantidade_validos / total_pecas) * 100
    percentual_invalidos = (quantidade_invalidos / total_pecas) * 100

    stats = {
        "total": total_pecas,
        "aprovados": f"{quantidade_validos} ({percentual_validos:.2f}%)",
        "reprovados": f"{quantidade_invalidos} ({percentual_invalidos:.2f}%)",
    }
    return stats

def validar_dados(json_data):
    itens_invalidos = []
    itens_validos = []
    for item in json_data:
        tamanho = item.get("Tamanho (cm)", 0)
        peso = item.get("Peso (g)", 0)
        acabamento = item.get("Acabamento", 0)
        
        erros = []
        
        # Verificar tamanho
        if not (10 <= tamanho <= 20):
            erros.append("Tamanho fora do limite (10 a 20 cm)")
        
        # Verificar peso
        if not (50 <= peso <= 100):
            erros.append("Peso fora do limite (50 a 100 g)")
        
        # Verificar acabamento
        if acabamento <= 7:
            erros.append("Acabamento insuficiente (abaixo ou igual a 7)")
        
        if erros:
            item["Status"] = "Reprovada"
            item["Erro"] = ", ".join(erros)  # Combina todos os erros em uma string
            itens_invalidos.append(item)
        else:
            item["Status"] = "Aprovada"
            item["Erro"] = ""  # Nenhum erro para itens válidos
            itens_validos.append(item)
    
    return itens_validos, itens_invalidos

def carregar_csv():
    caminho_csv = filedialog.askopenfilename(
        title="Selecione o arquivo CSV",
        filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*"))
    )
    try:
        df = pd.read_csv(caminho_csv)
        return df
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar o arquivo CSV: {e}")
        return None

def converter_para_json(df):
    try:
        json_data = json.loads(df.to_json(orient='records', force_ascii=False))
        return json_data
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao converter para JSON: {e}")
        return None

def atualizar_tabela(tabela, itens_validos, itens_invalidos):
    tabela.delete(*tabela.get_children())  # Limpar tabela existente
    for item in itens_validos + itens_invalidos:
        tabela.insert("", "end", values=[item.get("ID", ""), item.get("Peso (g)", ""), item.get("Tamanho (cm)", ""), item.get("Acabamento", ""), item.get("Status", ""), item.get("Erro", "")])

def atualizar_estatisticas(stats_label, stats):
    stats_label.config(text=(
        f"Total de peças analisadas: {stats['total']} | "
        f"Peças aprovadas: {stats['aprovados']} | "
        f"Peças reprovadas: {stats['reprovados']}"
    ))

def selecionar_arquivo(tabela, stats_label):
    df = carregar_csv()
    if df is not None:
        json_data = converter_para_json(df)
        if json_data:
            itens_validos, itens_invalidos = validar_dados(json_data)
            total_pecas = len(json_data)
            stats = estatisticas(itens_validos, itens_invalidos, total_pecas)

            # Atualizar a tabela com os dados
            atualizar_tabela(tabela, itens_validos, itens_invalidos)
            
            # Atualizar estatísticas gerais
            atualizar_estatisticas(stats_label, stats)

            # Verificar se mais de 20% das peças foram reprovadas
            percentual_rejeicao = (len(itens_invalidos) / total_pecas) * 100
            if percentual_rejeicao > 20:
                messagebox.showwarning(
                    "Alerta",
                    f"Mais de 20% das peças foram reprovadas ({percentual_rejeicao:.2f}%). "
                    "Revisar o processo de fabricação."
                )

def exibir_interface():
    # Criar janela principal
    janela = tk.Tk()
    janela.title("Controle de Qualidade")
    janela.geometry("1000x600")
    
    # Título
    titulo = tk.Label(janela, text="Módulo B - SENAI Dev Experience", font=("Arial", 16, "bold"))
    titulo.pack(pady=10)

    subtitulo = tk.Label(janela, text="Sistema de Controle de Qualidade", font=("Arial", 12, "bold"))
    subtitulo.pack(pady=10)
    
    # Botão para selecionar arquivo CSV
    btn_selecionar = tk.Button(janela, text="Carregar base de dados (Arquivo CSV)", command=lambda: selecionar_arquivo(tabela, stats_label))
    btn_selecionar.pack(pady=5)
    
    # Criar frame para a tabela
    tabela_frame = tk.Frame(janela)
    tabela_frame.pack(expand=True, fill="both", pady=10)
    
    # Criar tabela
    tabela = ttk.Treeview(tabela_frame, columns=["ID", "Peso (g)", "Tamanho (cm)", "Acabamento", "Status", "Erro"], show="headings")
    tabela.heading("ID", text="ID")
    tabela.heading("Peso (g)", text="Peso (g)")
    tabela.heading("Tamanho (cm)", text="Tamanho (cm)")
    tabela.heading("Acabamento", text="Acabamento")
    tabela.heading("Status", text="Status")
    tabela.heading("Erro", text="Erro")
    
    # Ajustar tamanho das colunas
    for col in ["ID", "Peso (g)", "Tamanho (cm)", "Acabamento", "Status", "Erro"]:
        tabela.column(col, width=150)
    
    tabela.pack(expand=True, fill="both")
    
    # Criar label para estatísticas
    stats_label = tk.Label(janela, text="", font=("Arial", 12), relief="solid", borderwidth=1, anchor="w")
    stats_label.pack(fill="x", padx=10, pady=5)

    janela.mainloop()

if __name__ == "__main__":
    exibir_interface()
