import pickle
import sqlite3
import pandas as pd
import altair as alt

df = pd.read_csv('../data/mock_users.csv')
conn = sqlite3.connect('../data/user_data.db')
df.to_sql('people', conn, if_exists='replace', index=False)

conn.close()

loaded_qol_model = pickle.load(open("./models/qol_model.pickle", 'rb'))
loaded_retirement_model = pickle.load(open("./models/retirement_model.pickle", 'rb'))
loaded_disaster_model = pickle.load(open("./models/disaster_model.pickle", 'rb'))
loaded_scaler = pickle.load(open("./models/scaler.pickle",'rb'))


def getInfo(age,housing,income,cpf,exp,saving):
    scaled = loaded_scaler.transform([[age,housing,income,cpf,exp,saving]])
    print(scaled)
    qol = loaded_qol_model.predict(scaled)
    dis = loaded_disaster_model.predict(scaled)
    ret = loaded_retirement_model.predict(scaled)
    return [qol,dis,ret]

def getLobang(qol,dis,ret):
    return round(((qol+dis+ret)/3)*10)

def get_user_data(name):
    # Step 1: Create a connection to the SQLite database
    conn = sqlite3.connect('../data/user_data.db')
    cursor = conn.cursor()
    query = "SELECT * FROM people WHERE name = ?"
    cursor.execute(query, (name,))
    result = cursor.fetchone()
    conn.close()
    
    return result

def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Arial", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response}'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          domain=[input_text, ''],
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text