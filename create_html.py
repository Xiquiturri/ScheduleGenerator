import pandas as pd
from datetime import datetime
from programacionLectores import start_date,end_date

# Leer el archivo CSV
df = pd.read_csv('output.csv')

# Función para obtener el nombre del día en español
def get_day_name(date_str):
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return days[date_obj.weekday()]

# Función para convertir el formato de la fecha 
def convertir_fechas(start_date, end_date): 
    # Formatear las fechas a la representación escrita 
    start_date_str = start_date.strftime("%d de %B") 
    end_date_str = end_date.strftime("%d de %B") 
    # Devolver la cadena en el formato 
    return f"{start_date_str} al {end_date_str}"

#Ordenar el DF 
df['Day_Name'] = df['Fecha'].apply(get_day_name)
days_order = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
df['Day_Order'] = df['Day_Name'].apply(lambda x: days_order.index(x))
df = df.sort_values(by=['Day_Order', 'Fecha']).reset_index(drop=True)

# Generar HTML
html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Generador de horarios</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f9f9f9;
        }}
        h1 {{
            color: #2c3e50;
        }}
        h2 {{
            color: #2980b9;
        }}
        table {{
            margin: 0 auto;
            border-collapse: collapse;
        }}
        #tablaLecturas{{
            border-collapse: collapse;
            width: 50%;
        }}
        #tablaFunerales{{
            border-collapse: collapse;
            width: 20%;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
        }}
        th {{
            background-color: #87CEEB;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #ddd;
        }}
        td {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <h1>PREDICANDO LA PALABRA DE DIOS CON ALEGRÍA</h1>
    <h3>Rol de la semana</h3>
    <h2>{convertir_fechas(start_date, end_date)}</h2>
    <h3>Lecturas y funerales</h3>
    <table id="tablaLecturas">
"""

# Poblar la tabla
for index, row in df.iterrows():
    day_name = get_day_name(row["Fecha"])
    if pd.notna(row["Mañana"]):
        personas = row["Mañana"].split(", ")
        if len(personas) >= 2:
            if day_name == "Domingo":
                hora = "7 AM"
            else:
                hora = "8 AM"
            html += f"<tr><td rowspan='{len(personas)}'>{day_name}</td><td rowspan='{len(personas)}'>{hora}</td><td>1ra lectura</td><td>{personas[0]}</td></tr>"
            html += f"<tr><td>Salmo</td><td>{personas[1]}</td></tr>"
            if len(personas) > 2:
                html += f"<tr><td>2a lectura</td><td>{personas[2]}</td></tr>"
            if len(personas) > 3:
                html += f"<tr><td>Monitor</td><td>{personas[3]}</td></tr>"
    
    if day_name == "Domingo" and pd.notna(row["Tarde"]):
        personas = row["Tarde"].split(", ")
        if len(personas) >= 2:
            hora = "12:30 PM"
            html += f"<tr><td rowspan='{len(personas)}'>{day_name}</td><td rowspan='{len(personas)}'>{hora}</td><td>1ra lectura</td><td>{personas[0]}</td></tr>"
            html += f"<tr><td>Salmo</td><td>{personas[1]}</td></tr>"
            if len(personas) > 2:
                html += f"<tr><td>2a lectura</td><td>{personas[2]}</td></tr>"
            if len(personas) > 3:
                html += f"<tr><td>Monitor</td><td>{personas[3]}</td></tr>"
    if pd.notna(row["Noche"]):
        personas = row["Noche"].split(", ")
        if len(personas) >= 2:
            hora = "6 PM"
            html += f"<tr><td rowspan='{len(personas)}'>{day_name}</td><td rowspan='{len(personas)}'>{hora}</td><td>1ra lectura</td><td>{personas[0]}</td></tr>"
            html += f"<tr><td>Salmo</td><td>{personas[1]}</td></tr>"
            if len(personas) > 2:
                html += f"<tr><td>2a lectura</td><td>{personas[2]}</td></tr>"
            if len(personas) > 3:
                html += f"<tr><td>Monitor</td><td>{personas[3]}</td></tr>"

html += "</table>"

#------------------Tabla de los funerales---------------
html += """
    <br></br>
    <h2>ROL DE FUNERALES</h2>
    <h3> 3 DE LA TARDE </h3>
    <table id="tablaFunerales">
"""
# Poblar la tabla de funerales
for index, row in df.iterrows():
    day_name = row["Day_Name"]
    if pd.notna(row["Funeral"]):
        html += f"<tr><td style='background-color: #87CEEB'>{day_name}</td><td>{row['Funeral']}</td></tr>"
html +="</table>"


#---------------------Salmo-----------------------------
html += """
    <p>Del Salmo 125 🙏</p>
    <p>Grandes cosas has hecho por nosotros, Señor</p>
</body>
</html>
"""

# Guardar en archivo HTML
with open("rol_de_la_semana.html", "w", encoding="utf-8") as file:
    file.write(html)

print("Archivo HTML creado exitosamente.")
