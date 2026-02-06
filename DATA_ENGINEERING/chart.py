import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns
from sqlalchemy import create_engine, text 
import os
from dotenv import load_dotenv
import urllib.parse 

# 1. Conexión base de datos 
load_dotenv()
usuario = os.getenv('DB_USER')
password = urllib.parse.quote_plus(os.getenv('DB_PASSWORD'))
engine = create_engine(f"postgresql://{usuario}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

# 2. Query porcentajes 
query = text('''
    SELECT 
        count(*) FILTER (WHERE descripcion ILIKE '%python%') as Python,
        count(*) FILTER (WHERE descripcion ILIKE '%sql%') as SQL,
        count(*) FILTER (WHERE descripcion ILIKE '%power bi%') as Power_BI,
        count(*) FILTER (WHERE descripcion ILIKE '%excel%') as Excel
    FROM vacantes
    WHERE descripcion != 'No encontrada';
''')

# 3. Procesamiento de datos con Pandas 
with engine.connect () as conn: 
    df = pd.read_sql(query, conn)

total_vacantes = 300 
df_melted = df.melt(var_name='Habilidad', value_name='Cantidad')
df_melted['Porcentaje'] = (df_melted['Cantidad']/total_vacantes)*100

# 4. Gráfico 
plt.figure (figsize=(10,6))
sns.set_style('whitegrid')
ax = sns.barplot(x='Habilidad', y='Porcentaje', data=df_melted, palette='viridis')

for p in ax.patches: 
    ax.annotate(f'{p.get_height():.1f}%', (p.get_x()+p.get_width() / 2., p.get_height()),
    ha='center', va='center', xytext=(0,9), textcoords='offset points', fontsize=12, fontweight='bold')

plt.title ('Habilidades más demandadas para Analistas de Datos en Bogotá (N=300)', fontsize=15, pad=20, fontweight='bold')
plt.ylabel ('Porcentaje de Vacantes (%)', fontsize=12)
plt.xlabel ('Herramientas', fontsize=12)
plt.ylim (0, 70)

plt.savefig ('demand_skills_bogota.png', dpi=300, bbox_inches='tight')
print ("✅ Gráfico Generado exitosamente como 'demand_skills_bogota.png")
plt.show ()