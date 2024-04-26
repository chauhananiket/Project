import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import warnings
import plotly.express as px

warnings.filterwarnings("ignore")

# Function to create SQLite database table if not exists
def create_table():
    conn = sqlite3.connect("topic.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS topics
              (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              topic_name TEXT UNIQUE NOT NULL,
              category TEXT NOT NULL, 
              resource TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Function to insert a new topic into the database
def insert_topic(topic_name,category,resource):
    conn = sqlite3.connect("topic.db")
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO topics (topic_name, category,resource) 
                    VALUES (?, ?, ?)''', 
                (topic_name,category,resource))
    conn.commit()
    conn.close()

# Function to remove entry from the database by topic name
def remove_entry_by_topic(topic_name):
    conn = sqlite3.connect("topic.db")
    c = conn.cursor()
    c.execute("DELETE FROM topics WHERE topic_name=?", (topic_name,))
    conn.commit()
    conn.close()

# Function to retrieve all topics from the database
def retrieve_topics():
    conn = sqlite3.connect("topic.db")
    c = conn.cursor()
    c.execute("SELECT topic_name, category ,resource FROM topics")
    topics = c.fetchall()
    conn.close()
    return topics

# Create database table if not exists
create_table()

def main():
    st.sidebar.title("Input Topic Data")
    category = st.sidebar.selectbox("Category",('ML','DL','NLP','CV','Stats','Technologies','Documentation'))
    topic_name = st.sidebar.text_input("Topic name")
    resource = st.sidebar.text_input("Resource Name",'List of resouces')
    add_topic = st.sidebar.button("Submit")

    if add_topic:
        insert_topic(topic_name.strip(),category,resource)
        st.sidebar.success("Topic added successfully!")

    st.sidebar.markdown("***")
    st.sidebar.title("Filter by Topic Category")
    filter_category = st.sidebar.selectbox("Filter Category",('ML','DL','NLP','CV','Stats','Technologies','Documentation'),index=None)

    st.sidebar.title("Filter by Topic Name")
    filter_topic = st.sidebar.text_input("Filter Topic",value="")

    st.sidebar.markdown("***")
    remove_topic_name = st.sidebar.text_input("Topic to Remove")
    remove_topic = st.sidebar.button("Remove Topic")

    if remove_topic:
        remove_entry_by_topic(remove_topic_name.strip())
        st.sidebar.success("Topic removed successfully!")

    # Display revision chart for all topics
    topics = retrieve_topics()
    
    if topics:

        st.title('Topic Resource Assistant')
        
        df = pd.DataFrame(topics, columns=["Topic Name", "Category", "Resource"])

        # Filter topics based on selected date
        if filter_category is not None:
            df_filter1 = df[df['Category']==filter_category]
            if len(df_filter1)!=0:
                # Create DataFrame from matched topic names and column names
                st.markdown("***")
                st.title(f'Topics In {filter_category}')
                st.table(df_filter1)
            else:
                st.markdown("***")
                st.title(f'Topics In {filter_category}')
                st.write("No topics added!")
        else :
            st.markdown("***")
            st.write("No topic category to filter.")
            
        if len(filter_topic)!=0:
            df_filter2 = df[df['Topic Name'].str.contains(filter_topic.strip(), case=False)]
            if len(df_filter2)!=0:
                st.markdown("***")
                st.title(f'Topics Filtered')
                st.table(df_filter2)
            else:
                st.markdown("***")
                st.write("No topics added!")
        else :
            st.markdown("***")
            st.write("No topic name filter.")

        # Group by 'Category' and count occurrences
        counts = df.groupby('Category').size().reset_index(name='Count')

        # Create a pie chart using Plotly Express
        fig = px.pie(counts, values='Count', names='Category', title='Counts of Categories')

        # Display the pie chart using Streamlit
        st.markdown("***")
        st.plotly_chart(fig)    

    else:
        st.markdown("***")
        st.write("No topics found in the database.")

if __name__ == "__main__":
    main()
