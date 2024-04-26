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
              (position INTEGER, 
              topic_name TEXT UNIQUE NOT NULL,
              category TEXT NOT NULL, 
              resource TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def get_max_position(category):
    # Connect to the SQLite database
    conn = sqlite3.connect('topic.db')
    cursor = conn.cursor()

    # Execute the SQL query to get the maximum position value for the specified category
    cursor.execute("SELECT Count(*) FROM topics WHERE Category = ?", (category,))
    max_position = cursor.fetchone()[0]

    # Close the database connection
    conn.close()

    return max_position

# Function to insert a new topic into the database
def insert_topic(max_pos,topic_name,category,resource):
    conn = sqlite3.connect("topic.db")
    c = conn.cursor()
    try :
        c.execute('''INSERT INTO topics (position,topic_name, category,resource) 
                        VALUES (? , ?, ?, ?)''', 
                    (max_pos,topic_name,category,resource))
    except:
        pass    
    conn.commit()
    conn.close()

# Function to remove entry from the database by topic name
def remove_entry_by_topic(topic_name):
    conn = sqlite3.connect("topic.db")
    c = conn.cursor()

    # Extract the category of the topic at the specified position
    c.execute("SELECT position,category FROM topics WHERE topic_name = ?", (topic_name,))
    result = c.fetchone()
    
    c.execute("DELETE FROM topics WHERE topic_name=?", (topic_name,))
    c.execute("UPDATE topics SET position = position - 1 WHERE position > ? AND category = ?", 
              (result[0],result[1]))

    # Commit the changes to the database
    conn.commit()
    conn.close()

# Function to retrieve all topics from the database
def retrieve_topics():
    conn = sqlite3.connect("topic.db")
    c = conn.cursor()
    c.execute("SELECT position,topic_name, category ,resource FROM topics")
    topics = c.fetchall()
    conn.close()
    return topics

def reorder_topic(topic_name, new_pos):
    # Connect to the SQLite database
    conn = sqlite3.connect('topic.db')
    cursor = conn.cursor()

    # Retrieve the current position of the topic to be reordered
    cursor.execute("SELECT position FROM topics WHERE topic_Name = ?", (topic_name,))
    current_position = cursor.fetchone()[0]

    # If the new index is greater than the current position,
    # shift topics between the current position and the new index down by 1
    if new_pos > current_position:
        cursor.execute("UPDATE topics SET position = position - 1 WHERE position > ? AND position <= ?", (current_position, new_pos))

    # If the new index is less than the current position,
    # shift topics between the new index and the current position up by 1
    elif new_pos < current_position:
        cursor.execute("UPDATE topics SET position = position + 1 WHERE position >= ? AND position < ?", (new_pos, current_position))

    # Update the position of the topic to be reordered to the new index
    cursor.execute("UPDATE topics SET position = ? WHERE Topic_Name = ?", (new_pos, topic_name))

    conn.commit()
    conn.close()

# Function to insert rows into the database
def insert_rows(rows):
    # Connect to the SQLite database
    conn = sqlite3.connect('topic.db')
    c = conn.cursor()

    for row in rows:
        try :
            c.execute('''INSERT INTO topics (position,topic_name, category,resource) 
                        VALUES (? , ?, ?, ?)''', (row))
        except:
            pass  

    conn.commit()
    conn.close()

def delete_rows():
    conn = sqlite3.connect('topic.db')
    c = conn.cursor()

    c.execute("DELETE FROM topics")

    conn.commit()
    conn.close()

# Function to display the upload button and process the uploaded file
def upload_and_process():
    uploaded_file = st.sidebar.file_uploader("Upload Data", type=['csv'])
    if uploaded_file is not None:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        rows = [tuple(row) for row in df.values]

        delete_rows()
        insert_rows(rows)
        st.sidebar.success("Data added successfully!")


# Create database table if not exists
create_table()

def main():

    upload_and_process()

    st.sidebar.markdown("***")
    st.sidebar.title("Input Topic Data")
    category = st.sidebar.selectbox("Category",('ML','DL','NLP','CV','Stats','Technologies','Documentation'))
    topic_name = st.sidebar.text_input("Topic name")
    resource = st.sidebar.text_input("Resource Name",'List of resouces')
    add_topic = st.sidebar.button("Submit")

    if add_topic:
        max_pos = get_max_position(category)
        insert_topic(max_pos,topic_name.strip(),category,resource)
        st.sidebar.success("Topic added successfully!")

    st.sidebar.markdown("***")
    st.sidebar.title("Filter by Topic Category")
    filter_category = st.sidebar.selectbox("Filter Category",('All','ML','DL','NLP','CV','Stats','Technologies','Documentation'),index=None)

    st.sidebar.title("Filter by Topic Name")
    filter_topic = st.sidebar.text_input("Filter Topic",value="")

    st.sidebar.markdown("***")
    reorder_topic_name = st.sidebar.text_input("Topic to Reorder")
    new_pos = st.sidebar.text_input("New Topic Position")
    reorder = st.sidebar.button('Reorder')

    if reorder:
        reorder_topic(reorder_topic_name,int(new_pos.strip()))

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
        df = pd.DataFrame(topics, columns=["Position","Topic Name", "Category", "Resource"])
        df.sort_values(by=['Category','Position'],inplace=True)

         # Add a button to download the CSV file
        csv = df.to_csv(index=False).encode('utf-8')

        # Offer the CSV file for download
        st.sidebar.markdown("***")
        st.sidebar.download_button(
            label="Download Data",
            data=csv,
            file_name='topic-resource.csv',
            mime='text/csv'
        )  

        # Filter topics based on selected date
        if filter_category is not None:

            if filter_category =='All':
                df_filter1 = df.copy()
            else:
                df_filter1 = df[df['Category']==filter_category]
            
            if len(df_filter1)!=0:
                # Create DataFrame from matched topic names and column names
                st.markdown("***")
                st.title(f'Topics : {filter_category}')
                st.table(df_filter1)
            else:
                st.markdown("***")
                st.title(f'Topics : {filter_category}')
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

        # Display the pie chart using Streamlit
        st.markdown("***")
        counts = df.groupby('Category').size().reset_index(name='Count')
        fig = px.pie(counts, values='Count', names='Category', title='Counts of Categories')
        st.title('Topic Category Distribution')
        st.plotly_chart(fig)  

    else:
        st.markdown("***")
        st.write("No topics found in the database.")



if __name__ == "__main__":
    main()
