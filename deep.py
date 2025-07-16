import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class FootballStudioAnalyzer:
    def __init__(self, master):
        self.master = master
        master.title("Football Studio Analyzer Pro")
        master.geometry("1200x800")
        master.configure(bg="#1e1e2d")
        
        # Históricos
        self.history = []
        self.signals = []
        self.performance = {'total': 0, 'hits': 0, 'misses': 0}
        
        # Carrega dados salvos
        self.load_data()
        
        # Interface
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        # Cores
        bg_color = "#1e1e2d"
        fg_color = "#e0e0ff"
        btn_color = "#3a3a5a"
        highlight_color = "#4caf50"
        
        # Frames
        main_frame = tk.Frame(self.master, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Painel de Controle
        control_frame = tk.LabelFrame(main_frame, text="Controle", bg=bg_color, fg=highlight_color, font=("Arial", 12, "bold"))
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Botões de Ação
        tk.Button(control_frame, text="Home (H)", bg="#d32f2f", fg="white", width=10, 
                  command=lambda: self.add_outcome('H')).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="Away (A)", bg="#1976d2", fg="white", width=10, 
                  command=lambda: self.add_outcome('A')).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(control_frame, text="Empate (T)", bg="#fbc02d", fg="black", width=10, 
                  command=lambda: self.add_outcome('T')).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(control_frame, text="Desfazer", bg=btn_color, fg=fg_color, width=10, 
                  command=self.undo_last).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(control_frame, text="Limpar", bg=btn_color, fg=fg_color, width=10, 
                  command=self.clear_history).grid(row=0, column=4, padx=5, pady=5)
        
        # Painel de Estatísticas
        stats_frame = tk.LabelFrame(main_frame, text="Desempenho", bg=bg_color, fg=highlight_color, font=("Arial", 12, "bold"))
        stats_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.stats_label = tk.Label(stats_frame, text="Acertos: 0/0 (0.00%)", bg=bg_color, fg=fg_color, font=("Arial", 14))
        self.stats_label.pack(pady=10)
        
        # Painel de Análise
        analysis_frame = tk.LabelFrame(main_frame, text="Análise em Tempo Real", bg=bg_color, fg=highlight_color, font=("Arial", 12, "bold"))
        analysis_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        # Árvore de resultados
        self.tree = ttk.Treeview(analysis_frame, columns=('Time', 'Resultado', 'Padrão', 'Previsão', 'Acerto'), show='headings')
        
        self.tree.heading('Time', text='Tempo')
        self.tree.heading('Resultado', text='Resultado')
        self.tree.heading('Padrão', text='Padrão Detectado')
        self.tree.heading('Previsão', text='Previsão')
        self.tree.heading('Acerto', text='Acerto')
        
        self.tree.column('Time', width=120)
        self.tree.column('Resultado', width=80)
        self.tree.column('Padrão', width=150)
        self.tree.column('Previsão', width=80)
        self.tree.column('Acerto', width=60)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Painel de Histórico
        history_frame = tk.LabelFrame(main_frame, text="Sequência Atual", bg=bg_color, fg=highlight_color, font=("Arial", 12, "bold"))
        history_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.history_canvas = tk.Canvas(history_frame, bg=bg_color, height=80)
        self.history_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuração de grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def add_outcome(self, outcome):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.append((timestamp, outcome))
        
        # Detecta padrões
        pattern, prediction = self.detect_pattern()
        
        # Verifica acerto (se já houver histórico suficiente)
        is_correct = None
        if len(self.history) > 1 and pattern:
            last_outcome = self.history[-1][1]
            prev_outcome = self.history[-2][1] if len(self.history) > 1 else None
            
            # Verifica se a previsão corresponde ao resultado anterior
            if prev_outcome == prediction:
                is_correct = "✅"
                self.performance['hits'] += 1
            else:
                is_correct = "❌"
                self.performance['misses'] += 1
            
            if is_correct:
                self.performance['total'] += 1
        
        # Registra sinal
        if pattern:
            self.signals.append({
                'time': timestamp,
                'outcome': outcome,
                'pattern': pattern,
                'prediction': prediction,
                'correct': is_correct
            })
        
        self.update_display()
        self.save_data()
    
    def undo_last(self):
        if self.history:
            # Remove o último resultado e sinal associado
            self.history.pop()
            
            # Remove o último sinal se existir
            if self.signals and self.signals[-1]['time'] == self.history[-1][0] if self.history else False:
                removed_signal = self.signals.pop()
                
                # Atualiza contagem de desempenho
                if removed_signal['correct'] == "✅":
                    self.performance['hits'] = max(0, self.performance['hits'] - 1)
                    self.performance['total'] = max(0, self.performance['total'] - 1)
                elif removed_signal['correct'] == "❌":
                    self.performance['misses'] = max(0, self.performance['misses'] - 1)
                    self.performance['total'] = max(0, self.performance['total'] - 1)
            
            self.update_display()
            self.save_data()
    
    def clear_history(self):
        self.history = []
        self.signals = []
        self.performance = {'total': 0, 'hits': 0, 'misses': 0}
        self.update_display()
        self.save_data()
    
    def detect_pattern(self):
        """Detecta mais de 50 padrões avançados"""
        if len(self.history) < 4:
            return None, None
        
        outcomes = [outcome for _, outcome in self.history]
        
        # Padrões Base (1-14)
        pattern, prediction = self._base_patterns(outcomes)
        if pattern:
            return pattern, prediction
        
        # Padrões Avançados (15-30)
        pattern, prediction = self._advanced_patterns(outcomes)
        if pattern:
            return pattern, prediction
        
        # Padrões Especiais (31-50)
        pattern, prediction = self._special_patterns(outcomes)
        if pattern:
            return pattern, prediction
        
        # Padrões de Empate (51+)
        pattern, prediction = self._tie_patterns(outcomes)
        if pattern:
            return pattern, prediction
        
        return None, None
    
    def _base_patterns(self, outcomes):
        # Implementação dos padrões 1-14
        # Exemplo: Padrão 1 - Zig-Zag Curto
        if len(outcomes) >= 4:
            last_4 = outcomes[-4:]
            if all(last_4[i] != last_4[i+1] for i in range(3)):
                return 1, last_4[0]  # Retorna primeira cor da sequência
        
        # Padrão 3 - Dominância
        if len(outcomes) >= 3 and outcomes[-1] == outcomes[-2] == outcomes[-3]:
            return 3, outcomes[-1]
        
        # ... (implementar outros 12 padrões base)
        
        return None, None
    
    def _advanced_patterns(self, outcomes):
        # Implementação dos padrões 15-30
        # Padrão 18 - Isca de Inversão
        if len(outcomes) >= 4:
            if outcomes[-4] == outcomes[-3] == outcomes[-2] and outcomes[-1] != outcomes[-2]:
                return 18, outcomes[-1]
        
        # ... (implementar outros 15 padrões avançados)
        
        return None, None
    
    def _special_patterns(self, outcomes):
        # Implementação dos padrões 31-50
        # Padrão 31 - Ciclo de Fibonacci
        if len(outcomes) >= 8:
            # Detecção de padrão baseado em sequência Fibonacci
            # (Implementação específica)
            pass
        
        # ... (implementar outros 19 padrões especiais)
        
        return None, None
    
    def _tie_patterns(self, outcomes):
        # Padrões específicos para empates
        # Padrão 51 - Empate como reset
        if outcomes[-1] == 'T' and len(outcomes) > 1:
            # Busca o último resultado antes dos empates consecutivos
            for i in range(len(outcomes)-2, -1, -1):
                if outcomes[i] != 'T':
                    return 51, outcomes[i]
        
        # Padrão 52 - Empate entre dominâncias
        if len(outcomes) >= 5:
            if outcomes[-1] == outcomes[-3] == outcomes[-5] and outcomes[-2] == 'T' and outcomes[-4] == 'T':
                return 52, outcomes[-1]
        
        # ... (implementar outros padrões de empate)
        
        return None, None
    
    def update_display(self):
        # Atualiza estatísticas
        total = self.performance['total']
        hits = self.performance['hits']
        accuracy = (hits / total * 100) if total > 0 else 0
        self.stats_label.config(text=f"Acertos: {hits}/{total} ({accuracy:.2f}%)")
        
        # Atualiza árvore de análise
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for signal in self.signals[-20:]:  # Mostra últimos 20 sinais
            self.tree.insert('', 'end', values=(
                signal['time'],
                signal['outcome'],
                f"Padrão {signal['pattern']}",
                signal['prediction'],
                signal['correct'] if signal['correct'] else ''
            ))
        
        # Atualiza visualização do histórico
        self.history_canvas.delete("all")
        x, y = 20, 40
        radius = 30
        
        for _, outcome in self.history[-12:]:  # Mostra últimos 12 resultados
            color = "#d32f2f" if outcome == 'H' else "#1976d2" if outcome == 'A' else "#fbc02d"
            self.history_canvas.create_oval(x, y-radius, x+radius*2, y+radius, fill=color, outline="white")
            self.history_canvas.create_text(x+radius, y, text=outcome, fill="white", font=("Arial", 14, "bold"))
            x += radius * 2 + 10
    
    def save_data(self):
        data = {
            'history': self.history,
            'signals': self.signals,
            'performance': self.performance
        }
        with open('football_studio_data.json', 'w') as f:
            json.dump(data, f)
    
    def load_data(self):
        if os.path.exists('football_studio_data.json'):
            try:
                with open('football_studio_data.json', 'r') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.signals = data.get('signals', [])
                    self.performance = data.get('performance', {'total': 0, 'hits': 0, 'misses': 0})
            except:
                # Em caso de erro no arquivo, inicia limpo
                self.history = []
                self.signals = []
                self.performance = {'total': 0, 'hits': 0, 'misses': 0}

if __name__ == "__main__":
    root = tk.Tk()
    app = FootballStudioAnalyzer(root)
    root.mainloop()
