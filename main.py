import streamlit as st
import sqlite3
from datetime import datetime, time, timedelta
import pandas as pd

# Criar uma conexão com o banco de dados (ou abrir se já existir)
conn = sqlite3.connect('agenda.db')
cursor = conn.cursor()

# Criar a tabela se ela ainda não existir
cursor.execute('''
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY,
        title TEXT,
        activity_type TEXT,
        date TEXT,
        time TEXT,
        status TEXT,
        notes TEXT
    )
''')
conn.commit()

def insert_data(title, activity_type, datetime_combined):
    cursor.execute('''
        INSERT INTO activities (title, activity_type, date, time)
        VALUES (?, ?, ?, ?)
    ''', (title, activity_type, datetime_combined.strftime('%Y-%m-%d'), datetime_combined.strftime('%H:%M:%S')))
    conn.commit()

def get_filtered_activities(selected_date):
    cursor.execute('''
        SELECT id, title, activity_type, date, time, status, notes FROM activities
        WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
    ''', (selected_date.strftime('%Y'), selected_date.strftime('%m')))
    result = cursor.fetchall()
    return pd.DataFrame(result,
                        columns=["id", "title", "activity_type", "date", "time", "status", "notes"])

def update_activity(id, status, notes):
    cursor.execute('''
        UPDATE activities
        SET status = ?, notes = ?
        WHERE id = ?
    ''', (status, notes, id))
    conn.commit()

def delete_activity(id):
    cursor.execute('''
        DELETE FROM activities WHERE id = ?
    ''', (id,))
    conn.commit()

def get_monthly_summary(selected_date):
    cursor.execute('''
        SELECT date, title, activity_type, status FROM activities
        WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
    ''', (selected_date.strftime('%Y'), selected_date.strftime('%m')))
    result = cursor.fetchall()
    return pd.DataFrame(result,
                        columns=["Data", "Título", "Tipo de Atividade", "Status"])

def get_day_activities(selected_date):
    cursor.execute('''
        SELECT title, time FROM activities
        WHERE strftime('%Y-%m-%d', date) = ?
    ''', (selected_date.strftime('%Y-%m-%d'),))
    result = cursor.fetchall()
    return result

def main():
    st.title("Agenda Inteligente")

    # Coletando informações da atividade
    title = st.text_input("Título da Atividade")
    activity_type = st.selectbox("Tipo de Atividade", ["Profissional", "Pessoal", "Familiar", "Outros"])
    date = st.date_input("Data da Atividade")
    time_of_day = st.time_input("Hora da Atividade", time(7, 0))

    # Converter a data e hora para um objeto datetime
    datetime_combined = datetime.combine(date, time_of_day)

    # Botão para adicionar a atividade
    if st.button("Adicionar Atividade"):
        insert_data(title, activity_type, datetime_combined)

    # Filtrar atividades por ano e mês
    year = st.selectbox("Selecione o Ano", range(2000, datetime.now().year + 1))
    month = st.selectbox("Selecione o Mês", range(1, 13))

    # Converter o ano e mês selecionados para objeto datetime
    selected_date = datetime(year, month, 1)

    filtered_activities = get_filtered_activities(selected_date)

    # Mostrar resumo mensal
    st.subheader("Resumo Mensal")
    month_summary = get_monthly_summary(selected_date)
    st.dataframe(month_summary)

    # Mostrar atividades filtradas
    if not filtered_activities.empty:
        st.subheader("Atividades Previstas")
        for index, activity in filtered_activities.iterrows():
            st.write(f"**Título:** {activity['title']}")
            st.write(f"**Tipo de Atividade:** {activity['activity_type']}")
            st.write(f"**Data e Hora da Atividade:** {activity['date']} {activity['time']}")

            # Gerar uma chave única para cada caixa de seleção
            checkbox_key = f"checkbox_{activity['id']}"

            if st.checkbox("Ver Detalhes", key=checkbox_key):
                status = st.selectbox("Status da Atividade", ["Pendente", "Realizada", "Em Execução"])
                notes = st.text_area("Descrição da atividade:")

                update_activity(activity['id'], status, notes)
                delete_button = st.button("Excluir Atividade")
                if delete_button:
                    delete_activity(activity['id'])

            st.write("---")

    # Mostrar atividades do dia na barra lateral
    selected_day = datetime.now().day
    day_activities = get_day_activities(selected_date.replace(day=selected_day))
    st.sidebar.subheader("Atividades do Dia")
    for activity in day_activities:
        st.sidebar.write(f"**Título:** {activity[0]}")
        st.sidebar.write(f"**Hora da Atividade:** {activity[1]}")
        st.sidebar.write("---")

if __name__ == "__main__":
    main()
