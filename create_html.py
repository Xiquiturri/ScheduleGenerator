import pandas as pd
from datetime import datetime
from programacionLectores import start_date,end_date

# Leer el archivo CSV
df = pd.read_csv('output.csv')

# Función para convertir el formato de la fecha 
def convertir_fechas(start_date, end_date): 
    # Formatear las fechas a la representación escrita 
    start_date_str = start_date.strftime("%d de %B") 
    end_date_str = end_date.strftime("%d de %B") 
    # Devolver la cadena en el formato 
    return f"{start_date_str} al {end_date_str}"

def convertir_a_12_horas(tiempo_24_horas):
    # Convertir la cadena de entrada en un objeto datetime
    tiempo_obj = datetime.strptime(tiempo_24_horas, "%H:%M:%S")
    # Verificar y agregar AM/PM manualmente si es necesario
    if tiempo_obj.hour < 12:
        periodo = "AM"
    else:
        periodo = "PM"
    # Convertir el objeto datetime en el formato de 12 horas
    tiempo_12_horas = tiempo_obj.strftime("%I:%M")
    return f"{tiempo_12_horas.lstrip('0')} {periodo}"


# --------Ordenar por dias de la semana y horas----------------------
days_order = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

# Obtener los valores únicos de eventos obligados excluyendo valores vacíos 
eventos_obligados = df['Obligado'].dropna().unique() 
days_order.extend(eventos_obligados) #Actualizar la lista

df['Hour_order'] = df['Hora'].apply(lambda x: datetime.strptime(x, '%H:%M:%S').time())
df['Day_Order'] = df['Día'].apply(lambda x: days_order.index(x))

# Crear una columna para el orden de los eventos obligados 
df['Obligado_Order'] = df.apply(lambda row: row['Fecha'] if pd.notna(row['Obligado']) and row['Obligado'] != pd.notnull else '', axis=1)

# Ordenar el DataFrame primero por el orden de los días y luego por la hora 
df = df.sort_values(by=['Day_Order', 'Hour_order', 'Obligado_Order']).reset_index(drop=True)
df.drop(columns=['Hour_order', 'Day_Order', 'Obligado_Order'], inplace=True)



# ------------Generar HTML-------------------------------------
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

# ---------------------Poblar la tabla LECTORES
elements_by_day = {}
lectura =["1ra lectura","Salmo","2a lectura","Monitor"]

# Agrupar los datos por día 
for index, row in df.iterrows(): 
    day_name = row["Día"] 
    if day_name not in elements_by_day: 
        elements_by_day[day_name] = [] # Se añade una nueva entrada con ese día como clave y una lista vacía como valor 
    elements_by_day[day_name].append((row["Hora"], row["Persona"])) 

# Asignación de la lectura por persona 
rows_by_day = {} 

for day, details in elements_by_day.items(): 
    if day.lower() == row["Obligado"]: 
        continue
    if day not in rows_by_day: 
        rows_by_day[day] = [] 
    personas_por_dia = {} 
    for hour, persona in details: 
        if hour not in personas_por_dia: 
            personas_por_dia[hour] = [] 
        personas_por_dia[hour].append(persona) 

    for hour, personas in personas_por_dia.items(): 
        for i, persona in enumerate(personas): 
                rows_by_day[day].append((hour, lectura[i], persona)) 
            


#-----------------------Tabla------------------------------
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
        html += f"<td rowspan='{unique_element}'>{convertir_a_12_horas(tasks[unique_element_aux][0])}</td>"

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
    # Convertir la cadena de fecha a un objeto datetime 
    fecha_obj = datetime.strptime(row['Fecha'], '%Y-%m-%d')
    day_name = fecha_obj.strftime("%A")
    if pd.notna(row["Obligado"]):
        html += f"<tr><td style='background-color: #b3d1fe'>{day_name}</td><td>{row['Persona']}</td></tr>"
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
