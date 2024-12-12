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
            border: black 2px solid;
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
            border: black 2px solid;
            padding: 8px;
        }}
        th {{
            background-color: #87CEEB;
            color: white;
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
from collections import defaultdict
# Crear un diccionario para agrupar las filas por día
rows_by_day = defaultdict(list)

# Agrupar las filas por día
for index, row in df.iterrows():
    day_name = get_day_name(row["Fecha"])
    if pd.notna(row["Mañana"]):
        personas = row["Mañana"].split(", ")
        if len(personas) >= 2:
            hora = "7 AM" if day_name == "Domingo" else "8 AM"
            rows_by_day[day_name].append((hora, "1ra lectura", personas[0]))
            rows_by_day[day_name].append((hora, "Salmo", personas[1]))
            if len(personas) > 2:
                rows_by_day[day_name].append((hora, "2a lectura", personas[2]))
            if len(personas) > 3:
                rows_by_day[day_name].append((hora, "Monitor", personas[3]))
    if day_name == "Domingo" and pd.notna(row["Tarde"]):
        personas = row["Tarde"].split(", ")
        if len(personas) >= 2:
            hora = "12:30 PM"
            rows_by_day[day_name].append((hora, "1ra lectura", personas[0]))
            rows_by_day[day_name].append((hora, "Salmo", personas[1]))
            if len(personas) > 2:
                rows_by_day[day_name].append((hora, "2a lectura", personas[2]))
            if len(personas) > 3:
                rows_by_day[day_name].append((hora, "Monitor", personas[3]))
    if pd.notna(row["Noche"]):
        personas = row["Noche"].split(", ")
        if len(personas) >= 2:
            hora = "6 PM"
            rows_by_day[day_name].append((hora, "1ra lectura", personas[0]))
            rows_by_day[day_name].append((hora, "Salmo", personas[1]))
            if len(personas) > 2:
                rows_by_day[day_name].append((hora, "2a lectura", personas[2]))
            if len(personas) > 3:
                rows_by_day[day_name].append((hora, "Monitor", personas[3]))

# Generar el HTML con rowspan
for day_name, tasks in rows_by_day.items():
    rowspan = len(tasks)
    first_task = tasks[0]
    unique_element_aux = tasks[0][0]
    unique_elements_counter = []
    counter = 0

    # Contar elementos únicos y sus frecuencias
    for task in tasks:
        if task[0] != unique_element_aux:
            unique_element_aux = task[0]
            unique_elements_counter.append(counter)
            counter = 0
        counter += 1
    unique_elements_counter.append(counter)  # Añadir el último contador

    html += f"<tr><td style='background-color: #b3d1fe'; rowspan='{rowspan}'>{day_name}</td>"

    unique_element_aux = 0
    for unique_element in unique_elements_counter:
        # Añadir la celda con rowspan para la hora
        html += f"<td rowspan='{unique_element}'>{tasks[unique_element_aux][0]}</td>"

        # Añadir las celdas para las personas
        for i in range(unique_element_aux, unique_element_aux + unique_element):
            task = tasks[i]
            if i == unique_element_aux:
                html += f"<td>{task[1]}</td><td>{task[2]}</td></tr>"
            else:
                html += f"<tr><td>{task[1]}</td><td>{task[2]}</td></tr>"
        unique_element_aux += unique_element

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
        html += f"<tr><td style='background-color: #b3d1fe'>{day_name}</td><td>{row['Funeral']}</td></tr>"
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
