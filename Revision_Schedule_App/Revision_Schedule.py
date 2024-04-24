import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

# Function to create SQLite database table if not exists
def create_table():
    conn = sqlite3.connect("revision_schedule.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS topics
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 topic_name TEXT UNIQUE NOT NULL,
                 entry_date DATE NOT NULL,
                 revision_1 DATE NOT NULL,
                 revision_2 DATE NOT NULL,
                 revision_3 DATE NOT NULL,
                 revision_4 DATE NOT NULL,
                 revision_5 DATE NOT NULL)''')
    conn.commit()
    conn.close()

# Function to insert a new topic into the database
def insert_topic(topic_name, entry_date, revision_dates):
    conn = sqlite3.connect("revision_schedule.db")
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO topics (topic_name, entry_date, revision_1, revision_2, revision_3, revision_4, revision_5) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                (topic_name, entry_date, revision_dates[0], revision_dates[1], revision_dates[2], revision_dates[3], revision_dates[4]))
    conn.commit()
    conn.close()

# Function to remove entry from the database by topic name
def remove_entry_by_topic(topic_name):
    conn = sqlite3.connect("revision_schedule.db")
    c = conn.cursor()
    c.execute("DELETE FROM topics WHERE topic_name=?", (topic_name,))
    conn.commit()
    conn.close()

# Function to retrieve all topics from the database
def retrieve_topics():
    conn = sqlite3.connect("revision_schedule.db")
    c = conn.cursor()
    c.execute("SELECT topic_name, revision_1, revision_2, revision_3, revision_4, revision_5 FROM topics")
    topics = c.fetchall()
    conn.close()
    return topics

# Function to generate revision chart for all topics
def generate_revision_chart(topics):
    fig = go.Figure()
    for topic in topics:
        topic_name, revision_dates = topic[0], topic[1:]
        revision_numbers = list(range(1, 6))
        fig.add_trace(go.Scatter(x=revision_dates, y=revision_numbers, mode='lines+markers', name=topic_name))
    fig.update_layout(
        title="Revision Schedule",
        xaxis_title="Revision Date",
        yaxis_title="Revision Number",
        xaxis=dict(tickformat="%Y-%m-%d"),
        yaxis=dict(tickvals=revision_numbers, ticktext=["Revision " + str(i) for i in revision_numbers]),
        showlegend=True
    )
    return fig

# Create database table if not exists
create_table()

def main():
    st.sidebar.title("Input Topic Data")
    topic_name = st.sidebar.text_input("Enter the topic name")
    entry_date = st.sidebar.date_input("Enter the date")
    add_topic = st.sidebar.button("Add Topic")

    revision_pattern = [7,14,30,60,90]

    if add_topic:
        # Calculate revision dates based on the pattern
        revision_dates = []
        current_revision_date = entry_date
        for after_days in revision_pattern:
            current_revision_date = current_revision_date + timedelta(days=after_days)
            revision_dates.append(current_revision_date)

        insert_topic(topic_name.strip(), entry_date, revision_dates)
        st.sidebar.success("Topic added successfully!")

    st.sidebar.markdown("***")
    st.sidebar.title("Filter by Date")
    filter_date = str(st.sidebar.date_input("Select Date"))

    st.sidebar.markdown("***")
    remove_topic_name = st.sidebar.text_input("Topic to Remove")
    remove_topic = st.sidebar.button("Remove Topic")

    if remove_topic:
        remove_entry_by_topic(remove_topic_name.strip())
        st.sidebar.success("Topic removed successfully!")

    # Display revision chart for all topics
    topics = retrieve_topics()
    
    if topics:

        fig = generate_revision_chart(topics)
        st.title("Revision Schedule")
        st.plotly_chart(fig, use_container_width=True)
        
        # Filter topics based on selected date
        df = pd.DataFrame(topics, columns=["Topic Name", "Revision 1", "Revision 2", "Revision 3", "Revision 4", "Revision 5"])
        st.title('Topic Data')
        st.write(df)

        # Initialize lists to store matched topic names and column names
        matched_topic_names = []
        matched_column_names = []

        # Iterate over each row and column
        for index, row in df.iterrows():
            topic_name = row["Topic Name"]
            for col_name, col_value in row.iteritems():
                if col_name != "Topic Name":
                    if col_value == filter_date:
                        matched_topic_names.append(topic_name)
                        matched_column_names.append(col_name)
        
        if len(matched_topic_names)!=0:
            # Create DataFrame from matched topic names and column names
            matched_df = pd.DataFrame({"Topic Name": matched_topic_names, "Matched Column Name": matched_column_names})
            st.title(f'Filtered topics for {filter_date}')
            st.write(matched_df)
        else:
            st.title(f'Filtered topics for {filter_date}')
            st.write("No topics to revise on the selected date.")

    else:
        st.write("No topics found in the database.")

if __name__ == "__main__":
    main()
