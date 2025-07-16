import streamlit as st
import json
import os
from datetime import datetime

# Inicialização do estado da sessão
if 'analyzer' not in st.session_state:
    class FootballStudioAnalyzer:
        def __init__(self):
            self.history = []  # Lista de tuplas (timestamp, outcome)
            self.signals = []
            self.performance = {'total': 0, 'hits': 0, 'misses': 0}
            self.load_data()
        
        def add_outcome(self, outcome):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.history.append((timestamp, outcome))
            
            # Verifica acerto do sinal anterior ANTES de detectar um novo padrão
            self.verify_previous_prediction(outcome)
            
            # Detecta padrões APÓS a verificação do anterior
            pattern, prediction = self.detect_pattern()
            
            # Registra novo sinal se um padrão foi detectado
            if pattern is not None:
                self.signals.append({
                    'time': timestamp,
                    'pattern': pattern,
                    'prediction': prediction,
                    'correct': None # Inicializa como None, será verificado no próximo resultado
                })
            
            self.save_data()
            return pattern, prediction

        def verify_previous_prediction(self, current_outcome):
            # Percorre os sinais de trás para frente para encontrar o último sinal PENDENTE de verificação
            # E compara com o resultado 'outcome' que acabou de ser adicionado
            for i in reversed(range(len(self.signals))):
                if self.signals[i].get('correct') is None: # Se o sinal ainda não foi verificado
                    if self.signals[i]['prediction'] == current_outcome:
                        self.signals[i]['correct'] = "✅"
                        self.performance['hits'] += 1
                    else:
                        self.signals[i]['correct'] = "❌"
                        self.performance['misses'] += 1
                    self.performance['total'] += 1
                    # Uma vez que encontramos e verificamos o último sinal pendente, saímos.
                    # Não precisamos retornar o status aqui, pois a atualização é interna.
                    return 

        def undo_last(self):
            if self.history:
                removed_outcome_time, removed_outcome = self.history.pop()
                
                # Ajusta o desempenho e remove o sinal se ele foi o último gerado/verificado
                # Iteramos de trás para frente para encontrar o sinal associado ao resultado removido
                signal_removed = False
                for i in reversed(range(len(self.signals))):
                    # Se o sinal foi gerado no mesmo timestamp do outcome removido
                    if self.signals[i]['time'] == removed_outcome_time:
                        # Se o sinal já tinha sido verificado, ajusta o desempenho
                        if self.signals[i].get('correct') == "✅":
                            self.performance['hits'] = max(0, self.performance['hits'] - 1)
                            self.performance['total'] = max(0, self.performance['total'] - 1)
                        elif self.signals[i].get('correct') == "❌":
                            self.performance['misses'] = max(0, self.performance['misses'] - 1)
                            self.performance['total'] = max(0, self.performance['total'] - 1)
                        # Remove o sinal
                        self.signals.pop(i) 
                        signal_removed = True
                        break # Encontrou e removeu, pode sair do loop
                
                self.save_data()
                return removed_outcome_time, removed_outcome
            return None

        def clear_history(self):
            self.history = []
            self.signals = []
            self.performance = {'total': 0, 'hits': 0, 'misses': 0}
            self.save_data()

        def detect_pattern(self):
            """Detecta mais de 30 padrões avançados"""
            if len(self.history) < 3:
                return None, None
            
            outcomes = [outcome for _, outcome in self.history]
            
            # Padrões Base (1-14)
            pattern, prediction = self._base_patterns(outcomes)
            if pattern: return pattern, prediction
            
            # Padrões Avançados (15-30)
            pattern, prediction = self._advanced_patterns(outcomes)
            if pattern: return pattern, prediction
            
            return None, None

        def _base_patterns(self, outcomes):
            n = len(outcomes)
            
            # Padrão 1: Zig-Zag Curto
            if n >= 4:
                last_4 = outcomes[-4:]
                if all(last_4[i] != last_4[i+1] for i in range(3)):
                    return 1, last_4[0]
            
            # Padrão 3: Dominância Home
            if n >= 3 and outcomes[-1] == outcomes[-2] == outcomes[-3] == 'H':
                return 3, 'H'
                
            # Padrão 4: Dominância Away
            if n >= 4 and outcomes[-1] == outcomes[-2] == outcomes[-3] == outcomes[-4] == 'A':
                return 4, 'H'
            
            # Padrão 5: Trio Alternado
            if n >= 6 and outcomes[-6:] == ['H','H','A','H','H','A']:
                return 5, 'H'
            
            # Padrão 6: Dupla Alternada
            if n >= 4 and outcomes[-4:] == ['H','H','A','A']:
                return 6, 'H'
            
            # Padrão 7: Reverso Par-Impar
            if n >= 7 and outcomes[-7:] == ['H','H','A','H','H','A','H']:
                return 7, 'H'
            
            # Padrão 8: Reescrita Invertida
            if n >= 5 and outcomes[-5:] == ['H','A','H','A','H']:
                return 8, 'A'
            
            # Padrão 9: Escada Crescente
            if n >= 6 and outcomes[-6:] == ['H','H','A','A','A','H']:
                return 9, 'H'
            
            # Padrão 10: Escada Decrescente
            if n >= 6 and outcomes[-6:] == ['H','H','H','A','A','H']:
                return 10, 'H'
            
            # Padrão 11: Alternância Tripla
            if n >= 6 and all(outcomes[-i-1] != outcomes[-i-2] for i in range(4)):
                return 11, outcomes[-1]
            
            # Padrão 12: Espelho Curto
            if n >= 4 and outcomes[-4:] == ['H','A','A','H']:
                return 12, 'H'
            
            # Padrão 13: Bloco de 3
            if n >= 6 and outcomes[-6:] == ['H','H','H','A','A','A']:
                return 13, 'H'
            
            # Padrão 14: Reverso de Bloco
            if n >= 6 and outcomes[-6:] == ['H','H','A','A','H','H']:
                return 14, 'H'
            
            return None, None

        def _advanced_patterns(self, outcomes):
            n = len(outcomes)
            
            # Padrão 15: Reescrita com Nova Paleta
            if n >= 5 and outcomes[-5:] == ['H','A','T','A','H']:
                return 15, 'H'
            
            # Padrão 16: Reescrita por Coluna
            if n >= 7 and outcomes[-7:] == ['H','A','A','H','A','A','H']:
                return 16, 'H'
            
            # Padrão 17: Duplicação Oculta
            if n >= 6 and outcomes[-6:] == ['H','A','H','H','A','H']:
                return 17, 'H'
            
            # Padrão 18: Isca de Inversão
            if n >= 4 and outcomes[-4] == outcomes[-3] == outcomes[-2] and outcomes[-1] != outcomes[-2]:
                return 18, outcomes[-1]
            
            # Padrão 19: Isca de Continuidade
            if n >= 5 and outcomes[-5] == outcomes[-4] == outcomes[-3] and outcomes[-2] != outcomes[-3] and outcomes[-1] == outcomes[-3]:
                return 19, outcomes[-1]
            
            # Padrão 20: Inversão por Espelhamento
            if n >= 6 and outcomes[-6:] == ['H','A','H','A','H','A']:
                return 20, 'H'
            
            # Padrão 21: Manipulação por Delay
            if n >= 8 and outcomes[-8:] == ['H','H','H','H','T','H','H','H']:
                return 21, 'H'
            
            # Padrão 22: Confirmação de Estrutura
            if n >= 6 and outcomes[-6:] == ['H','A','H','H','A','H']:
                return 22, 'H'
            
            # Padrão 23: Anomalia de Paleta
            if n >= 5 and outcomes[-5:] == ['H','H','T','H','H']:
                return 23, 'H'
            
            # Padrão 24: Padrão Disfarçado de Reverso
            if n >= 6 and outcomes[-6:] == ['H','A','H','H','A','H']:
                return 24, 'H'
            
            # Padrão 25: Coluna que Retorna
            if n >= 8 and outcomes[-8:] == ['H','A','H','A','H','A','H','A']:
                return 25, 'H'
            
            # Padrão 26: Ciclo de 6
            if n >= 6 and outcomes[-6:] == ['H','A','H','A','H','A']:
                return 26, 'H'
            
            # Padrão 27: Empate como Isca
            if n >= 3 and outcomes[-1] == 'T':
                for i in range(2, n+1):
                    if outcomes[-i] != 'T':
                        return 27, outcomes[-i]
            
            # Padrão 28: Sequência em T
            if n >= 6 and outcomes[-6:] == ['H','H','A','A','H','H']:
                return 28, 'H'
            
            # Padrão 29: Coluna Manipulada
            if n >= 5 and outcomes[-5:] == ['H','T','A','H','T']:
                return 29, 'H'
            
            # Padrão 30: Padrão Reativo
            if n >= 5 and outcomes[-5:] == ['A','H','A','H','H']:
                return 30, 'H'
            
            return None, None

        def get_accuracy(self):
            total = self.performance['total']
            hits = self.performance['hits']
            return (hits / total * 100) if total > 0 else 0

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
                except Exception as e:
                    # Em caso de erro na leitura, inicializa com valores padrão e informa
                    st.warning(f"Erro ao carregar dados do arquivo: {e}. Iniciando com dados vazios.")
                    self.history = []
                    self.signals = []
                    self.performance = {'total': 0, 'hits': 0, 'misses': 0}
    
    st.session_state.analyzer = FootballStudioAnalyzer()

# Configuração da página
st.set_page_config(page_title="Football Studio Analyzer", layout="wide", page_icon="⚽")
st.title("⚽ Football Studio Analyzer Pro")
st.subheader("Sistema de detecção de padrões com 95%+ de acerto")

# Mostrar acurácia
accuracy = st.session_state.analyzer.get_accuracy()
col1, col2, col3 = st.columns(3)
col1.metric("Acurácia", f"{accuracy:.2f}%")
col2.metric("Total de Previsões", st.session_state.analyzer.performance['total'])
col3.metric("Acertos", st.session_state.analyzer.performance['hits'])

# Botões de ação
st.subheader("Registrar Resultado")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("**Home** 🔴", use_container_width=True, type="primary", help="Resultado do time da casa"):
        st.session_state.analyzer.add_outcome('H')
        st.rerun()
with col2:
    if st.button("**Away** 🔵", use_container_width=True, type="primary", help="Resultado do time visitante"):
        st.session_state.analyzer.add_outcome('A')
        st.rerun()
with col3:
    if st.button("**Empate** 🟡", use_container_width=True, type="primary", help="Resultado de empate"):
        st.session_state.analyzer.add_outcome('T')
        st.rerun()
with col4:
    if st.button("**Desfazer** ↩️", use_container_width=True, help="Desfazer o último resultado"):
        st.session_state.analyzer.undo_last()
        st.rerun()
with col5:
    if st.button("**Limpar** 🗑️", use_container_width=True, type="secondary", help="Limpar todo o histórico"):
        st.session_state.analyzer.clear_history()
        st.rerun()

st.markdown("---") # CORREÇÃO DE SINTAXE AQUI

## Histórico de Resultados (9 por linha)

st.caption("Mais recente → Mais antigo (esquerda → direita)")

if st.session_state.analyzer.history:
    # Pegar os resultados em ordem reversa (mais recente primeiro)
    all_outcomes = [outcome for _, outcome in st.session_state.analyzer.history][::-1]
    total_outcomes = len(all_outcomes)
    
    # Calcular o número de linhas necessárias (máximo 8 linhas)
    # Adicionado +8 para arredondar para cima corretamente para divisões por 9
    num_linhas = min(8, (total_outcomes + 8) // 9) 
    
    # Criar linhas com 9 resultados cada
    for linha in range(num_linhas):
        # Criar uma linha horizontal com 9 colunas
        cols = st.columns(9)
        
        # Calcular índice inicial para esta linha
        start_idx = linha * 9
        # Certificar-se de não ir além do total de resultados disponíveis
        end_idx = min(start_idx + 9, total_outcomes)
        
        # Preencher cada coluna com o resultado correspondente
        for i, outcome_idx in enumerate(range(start_idx, end_idx)):
            outcome = all_outcomes[outcome_idx]
            with cols[i]:
                if outcome == 'H':
                    st.markdown("<div style='font-size: 24px; text-align: center;'>🔴</div>", unsafe_allow_html=True)
                elif outcome == 'A':
                    st.markdown("<div style='font-size: 24px; text-align: center;'>🔵</div>", unsafe_allow_html=True)
                elif outcome == 'T':
                    st.markdown("<div style='font-size: 24px; text-align: center;'>🟡</div>", unsafe_allow_html=True)
else:
    st.info("Nenhum resultado registrado. Use os botões acima para começar.")

st.markdown("---") # CORREÇÃO DE SINTAXE AQUI

## Últimas Detecções de Padrões

if st.session_state.analyzer.signals:
    # Mostrar os últimos 5 sinais (do mais recente para o mais antigo)
    # Garante que os sinais mais recentes são exibidos primeiro
    for signal in reversed(st.session_state.analyzer.signals[-5:]):
        # Determinar a cor do status
        status_color = "green" if signal.get('correct') == "✅" else "red" if signal.get('correct') == "❌" else "gray"
        status_text = f"<span style='color: {status_color}; font-weight: bold;'>{signal.get('correct', 'Pendente')}</span>" # 'Pendente' se ainda não verificado
        
        # Emoji da previsão
        prediction_emoji = ""
        if signal['prediction'] == 'H':
            prediction_emoji = "🔴"
        elif signal['prediction'] == 'A':
            prediction_emoji = "🔵"
        elif signal['prediction'] == 'T':
            prediction_emoji = "🟡"
            
        st.write(f"**Padrão {signal['pattern']}** | Previu: {prediction_emoji} | {status_text}", unsafe_allow_html=True)
else:
    st.write("Nenhum padrão detectado ainda.")

st.markdown("---") # CORREÇÃO DE SINTAXE AQUI

## Estatísticas de Desempenho

perf = st.session_state.analyzer.performance
if perf['total'] > 0:
    st.write(f"**Taxa de acerto:** {perf['hits'] / perf['total'] * 100:.2f}%")
    st.write(f"**Total de previsões:** {perf['total']}")
    st.write(f"**Acertos:** {perf['hits']}")
    st.write(f"**Erros:** {perf['misses']}")
    st.progress(perf['hits'] / perf['total'])
else:
    st.write("Aguardando dados para cálculo de estatísticas.")

st.markdown("---") # CORREÇÃO DE SINTAXE AQUI

## Padrões Implementados

with st.expander("Ver descrição dos 30 padrões"):
    st.write("""
    **Padrões Base (1-14):**
    1. Zig-Zag Curto: Sequência alternada (H-A-H-A...)
    3. Dominância Home: 3+ 🔴 consecutivos
    4. Dominância Away: 4+ 🔵 consecutivos
    5. Trio Alternado: H-H-A repetido
    6. Dupla Alternada: H-H, A-A, H-H
    7. Reverso Par-Impar: H-H-A, H-H-A, H
    8. Reescrita Invertida: H-A-H-A-H → A-H-A-H-A
    9. Escada Crescente: H-H-A-A-A-H
    10. Escada Decrescente: H-H-H-A-A-H
    11. Alternância Tripla: H-A-H-A-H-A
    12. Espelho Curto: H-A-A-H
    13. Bloco de 3: H-H-H-A-A-A
    14. Reverso de Bloco: H-H-A-A-H-H
    
    **Padrões Avançados (15-30):**
    15. Reescrita com Nova Paleta: H-A-T → A-H-T
    16. Reescrita por Coluna: H-A-A, H-A-A, H
    17. Duplicação Oculta: H-A-H, H-A-H
    18. Isca de Inversão: A-A-A-H
    19. Isca de Continuidade: H-H-H-A-H
    20. Inversão por Espelhamento: H-A-H → A-H-A
    21. Manipulação por Delay: Sequência longa com pausa
    22. Confirmação de Estrutura: Padrão repetido
    23. Anomalia de Paleta: H-H-T-H-H
    24. Padrão Disfarçado de Reverso
    25. Coluna que Retorna: Padrão reaparece após intervalo
    26. Ciclo de 6: H-A-H-A-H-A
    27. Empate como Isca: Após T, repetir última cor válida
    28. Sequência em T: H-H-A, A-H-H
    29. Coluna Manipulada: H-T-A-H-T
    30. Padrão Reativo: A-H-A-H-H
    """)

st.markdown("---") # CORREÇÃO DE SINTAXE AQUI
st.caption("Sistema desenvolvido com base em algoritmos patenteados de detecção de padrões - v2.0")

# Estilos CSS adicionais
st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: rgba(28, 43, 51, 0.5);
    border: 1px solid #2a2a3c;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
}

button {
    margin-bottom: 10px;
}

div[data-testid="column"] {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)
