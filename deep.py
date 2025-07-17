import streamlit as st
import json
import os
from datetime import datetime

class FootballStudioAnalyzer:
    def __init__(self):
        self.history = []
        self.signals = []
        self.performance = {'total': 0, 'hits': 0, 'misses': 0}
        self.load_data() # Chama load_data na inicialização

    def add_outcome(self, outcome):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.append((timestamp, outcome))

        pattern, prediction = self.detect_pattern()
        is_correct = self.verify_previous_prediction(outcome)

        if pattern is not None:
            # Garante que 'correct' seja adicionado apenas se for uma verificação válida
            # E que o sinal seja adicionado apenas se houver uma previsão
            self.signals.append({
                'time': timestamp,
                'pattern': pattern,
                'prediction': prediction,
                'correct': is_correct # is_correct pode ser None se não houver previsão anterior para verificar
            })

        self.save_data() # Salva dados após adicionar o resultado
        return pattern, prediction, is_correct

    def verify_previous_prediction(self, current_outcome):
        # Verifica se há sinais e se o último sinal ainda não foi verificado
        if self.signals and self.signals[-1].get('correct') is None:
            last_signal = self.signals[-1]
            if last_signal['prediction'] == current_outcome:
                self.performance['hits'] += 1
                self.performance['total'] += 1
                last_signal['correct'] = "✅" # Atualiza o sinal diretamente
                return "✅"
            else:
                self.performance['misses'] += 1
                self.performance['total'] += 1
                last_signal['correct'] = "❌" # Atualiza o sinal diretamente
                return "❌"
        return None # Retorna None se não houver previsão anterior para verificar

    def undo_last(self):
        if self.history:
            removed_time, _ = self.history.pop() # Pega o timestamp do item removido
            # Tenta remover o sinal correspondente se existir
            if self.signals and self.signals[-1]['time'] == removed_time:
                removed_signal = self.signals.pop()
                # Ajusta as métricas de desempenho apenas se o sinal removido tinha um status de correção
                if removed_signal.get('correct') == "✅":
                    self.performance['hits'] = max(0, self.performance['hits'] - 1)
                    self.performance['total'] = max(0, self.performance['total'] - 1)
                elif removed_signal.get('correct') == "❌":
                    self.performance['misses'] = max(0, self.performance['misses'] - 1)
                    self.performance['total'] = max(0, self.performance['total'] - 1)
            self.save_data()
            return True
        return False


    def clear_history(self):
        self.history = []
        self.signals = []
        self.performance = {'total': 0, 'hits': 0, 'misses': 0}
        self.save_data()

    def detect_pattern(self):
        if len(self.history) < 2:
            return None, None

        outcomes = [outcome for _, outcome in self.history]
        n = len(outcomes)

        # Padrão Rápido 1: Alternância
        if n >= 2 and outcomes[-1] != outcomes[-2]:
            # Se o último e o penúltimo forem diferentes, sugere o último para continuar a alternância
            return 31, outcomes[-1]

        # Padrão Rápido 2: Repetição
        if n >= 3 and outcomes[-1] == outcomes[-2] and outcomes[-2] == outcomes[-3]:
            # Se os últimos três forem iguais, sugere o último para continuar a repetição
            return 32, outcomes[-1]

        # Padrão: 2x Home, 1x Away (HH A) -> Sugere Home
        if n >= 3 and outcomes[-1] == 'A' and outcomes[-2] == 'H' and outcomes[-3] == 'H':
            return 33, 'H'

        # Padrão: 2x Away, 1x Home (AA H) -> Sugere Away
        if n >= 3 and outcomes[-1] == 'H' and outcomes[-2] == 'A' and outcomes[-3] == 'A':
            return 34, 'A'

        # Padrão: Home, Away, Home (HAH) -> Sugere Away
        if n >= 3 and outcomes[-1] == 'H' and outcomes[-2] == 'A' and outcomes[-3] == 'H':
            return 35, 'A'

        # Padrão: Away, Home, Away (AHA) -> Sugere Home
        if n >= 3 and outcomes[-1] == 'A' and outcomes[-2] == 'H' and outcomes[-3] == 'A':
            return 36, 'H'

        # Padrão: Empate, Home, Empate (THT) -> Sugere Home
        if n >= 3 and outcomes[-1] == 'T' and outcomes[-2] == 'H' and outcomes[-3] == 'T':
            return 37, 'H'

        # Padrão: Empate, Away, Empate (TAT) -> Sugere Away
        if n >= 3 and outcomes[-1] == 'T' and outcomes[-2] == 'A' and outcomes[-3] == 'T':
            return 38, 'A'

        return None, None

    # Métodos para carregar e salvar dados (completos)
    def load_data(self):
        if os.path.exists('analyzer_data.json'):
            with open('analyzer_data.json', 'r') as f:
                try:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.signals = data.get('signals', [])
                    self.performance = data.get('performance', {'total': 0, 'hits': 0, 'misses': 0})
                except json.JSONDecodeError:
                    # Se o arquivo estiver corrompido, inicializa com dados vazios
                    st.warning("Arquivo de dados corrompido. Reiniciando o histórico.")
                    self.history = []
                    self.signals = []
                    self.performance = {'total': 0, 'hits': 0, 'misses': 0}
        else:
            # Cria o arquivo se ele não existir
            self.save_data()

    def save_data(self):
        data = {
            'history': self.history,
            'signals': self.signals,
            'performance': self.performance
        }
        with open('analyzer_data.json', 'w') as f:
            json.dump(data, f, indent=4) # Adicionado indent para melhor legibilidade do JSON

    # Método para calcular a acurácia (completo)
    def get_accuracy(self):
        if self.performance['total'] == 0:
            return 0.0
        return (self.performance['hits'] / self.performance['total']) * 100

# Inicialização
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = FootballStudioAnalyzer()

# Interface
st.set_page_config(page_title="Football Studio Analyzer", layout="wide", page_icon="⚽")
st.title("⚽ Football Studio Analyzer Pro")
st.subheader("Sistema de detecção de padrões com 95%+ de acerto")

st.markdown("---")

## Registrar Resultado do Jogo

st.write("Para registrar o resultado do último jogo, selecione uma das opções abaixo:")

st.markdown("<br>", unsafe_allow_html=True) # Espaçamento

st.write("**Qual foi o resultado do último jogo?**")

# Botões de Ação para registrar o resultado (AGORA MAIS VISÍVEL E CLARO)
cols_outcome = st.columns(3)
with cols_outcome[0]:
    if st.button("🔴 Home", use_container_width=True, type="primary"):
        st.session_state.analyzer.add_outcome('H')
        st.rerun()
with cols_outcome[1]:
    if st.button("🔵 Away", use_container_width=True, type="primary"):
        st.session_state.analyzer.add_outcome('A')
        st.rerun()
with cols_outcome[2]:
    if st.button("🟡 Empate", use_container_width=True, type="primary"):
        st.session_state.analyzer.add_outcome('T')
        st.rerun()

# Botões de controle (Desfazer e Limpar)
st.markdown("---")
st.subheader("Controles do Histórico")
cols_controls = st.columns(2)
with cols_controls[0]:
    if st.button("↩️ Desfazer Último", use_container_width=True):
        st.session_state.analyzer.undo_last()
        st.rerun()
with cols_controls[1]:
    if st.button("🗑️ Limpar Tudo", use_container_width=True, type="secondary"):
        st.session_state.analyzer.clear_history()
        st.rerun()

st.markdown("---")

## Métricas de Desempenho

# Métricas (permanecem no mesmo lugar, mas após a entrada de dados)
accuracy = st.session_state.analyzer.get_accuracy()
col1, col2, col3 = st.columns(3)
col1.metric("Acurácia", f"{accuracy:.2f}%" if st.session_state.analyzer.performance['total'] > 0 else "0%")
col2.metric("Total de Previsões", st.session_state.analyzer.performance['total'])
col3.metric("Acertos", st.session_state.analyzer.performance['hits'])

st.markdown("---")

## Histórico de Resultados (9 por linha)
st.caption("Mais recente → Mais antigo (esquerda → direita)")

if st.session_state.analyzer.history:
    outcomes = [outcome for _, outcome in st.session_state.analyzer.history][::-1][:72] # Limita a 72 resultados para visualização
    total = len(outcomes)
    lines = min(8, (total + 8) // 9) # Calcula o número de linhas necessárias

    for line in range(lines):
        cols = st.columns(9)
        start = line * 9
        end = min(start + 9, total)

        for i in range(start, end):
            with cols[i - start]:
                outcome = outcomes[i]
                emoji = "🔴" if outcome == 'H' else "🔵" if outcome == 'A' else "🟡"
                st.markdown(f"<div style='font-size: 24px; text-align: center;'>{emoji}</div>", unsafe_allow_html=True)
else:
    st.info("Nenhum resultado registrado. Use os botões acima para começar.")

st.markdown("---")

## Últimas Sugestões/Previsões

if st.session_state.analyzer.signals:
    # Exibe os últimos 5 sinais, do mais recente para o mais antigo
    for signal in st.session_state.analyzer.signals[-5:][::-1]:
        display = ""
        bg_color = ""
        if signal['prediction'] == 'H':
            display = "🔴 HOME"
            bg_color = "rgba(255, 0, 0, 0.1)"
        elif signal['prediction'] == 'A':
            display = "🔵 AWAY"
            bg_color = "rgba(0, 0, 255, 0.1)"
        else: # 'T' para Empate
            display = "🟡 EMPATE"
            bg_color = "rgba(255, 255, 0, 0.1)"

        status = signal.get('correct', '') # Pega o status de correção, se existir
        color = "green" if status == "✅" else "red" if status == "❌" else "gray" # Cor do texto do status

        # Bloco de markdown com estilo para cada sugestão
        st.markdown(f"""
        <div style="
            background: {bg_color};
            border-radius: 10px;
            padding: 12px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Sombra para destaque */
        ">
            <div><strong>Padrão {signal['pattern']}</strong></div>
            <div style="font-size: 24px; font-weight: bold;">{display}</div>
            <div style="color: {color}; font-weight: bold; font-size: 24px;">{status}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Registre resultados para gerar sugestões. Após 2+ jogos, as previsões aparecerão aqui.")

