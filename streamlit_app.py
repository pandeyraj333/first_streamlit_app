import streamlit
import pandas
import requests
import snowflake.connector
from urllib.error import URLError

streamlit.title("My Parent's New Healthy Diner")
streamlit.header('Breakfast Menu')
streamlit.text('🥣Omega 3 & Blueberry Oatmeal')
streamlit.text('🥗Kale, Spinach and Rocket Smoothie')
streamlit.text('🐔Hard Boiled Free Range Egg')
streamlit.text('🥑🍞Avocado Toast')
streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')

my_fruit_list = pandas.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index('Fruit')

# Let's put a pick list here so they can pick the fruit they want to include 
fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index),['Avocado','Strawberries'])

fruits_to_show = my_fruit_list.loc[fruits_selected]

# Display the table on the page.
streamlit.dataframe(fruits_to_show)
# Create function for fruityvice
def get_fv_data(this_fruit_choice):
  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + this_fruit_choice)
  fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
  return fruityvice_normalized
# Fruityvice Response
streamlit.header('Fruityvice Fruit Advice!')
try:
  fruit_choice = streamlit.text_input('What fruit would you like information about?')
  if not fruit_choice:
    streamlit.error('Please Select a fruit to get information.')
  else:
    back_from_function = get_fv_data(fruit_choice)
    streamlit.dataframe(back_from_function)
except URLError as e:
  streamlit.error()


streamlit.header("The fruit load list contains:")

# get fruit load list from Snowflake
def get_fruit_load_list(my_cnx):
    with my_cnx.cursor() as my_cur:
        my_cur.execute("select * from fruit_load_list")
        return my_cur.fetchall()

# Add button to load te df
if streamlit.button('Get Fruit Load List'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data_rows = get_fruit_load_list(my_cnx)
  streamlit.dataframe(my_data_rows)

# Add new fruit to list in Snowflake
def insert_row_sf(my_cnx,new_fruit):
  with my_cnx.cursor as my_cur:
    my_cur.execute("insert into fruit_load_list values('"+new_fruit+"')")
    return new_fruit + " added successfully!"

# Add button to add the new button
streamlit.header('What fruit would you like to add')
fruit_add = streamlit.text_input('What fruit would you like to add?')
if streamlit.button('Add'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  new_row_message = insert_row_sf(my_cnx,fruit_add)
  streamlit.text(new_row_message)
