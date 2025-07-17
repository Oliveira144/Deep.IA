# Últimos sinais detectados
st.subheader("Últimas Detecções de Padrões")
if st.session_state.analyzer.signals:
    # Mostrar os últimos 5 sinais (do mais recente para o mais antigo)
    for signal in st.session_state.analyzer.signals[-5:]:
        # Determinar a cor do status
        status_color = "green" if signal.get('correct') == "✅" else "red" if signal.get('correct') == "❌" else "gray"
        status_text = f"<span style='color: {status_color}; font-weight: bold;'>{signal.get('correct', '')}</span>"
        
        # Emoji e texto da previsão
        prediction_text = ""
        bg_color = ""
        if signal['prediction'] == 'H':
            prediction_text = "🔴 HOME"
            bg_color = "rgba(255, 0, 0, 0.2)"
        elif signal['prediction'] == 'A':
            prediction_text = "🔵 AWAY"
            bg_color = "rgba(0, 0, 255, 0.2)"
        elif signal['prediction'] == 'T':
            prediction_text = "🟡 EMPATE"
            bg_color = "rgba(255, 255, 0, 0.2)"
        
        # Container destacado
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div style="font-weight: bold;">Padrão {signal['pattern']}</div>
            <div style="font-size: 24px; font-weight: bold;">{prediction_text}</div>
            <div>{status_text}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.write("Nenhum padrão detectado ainda.")
