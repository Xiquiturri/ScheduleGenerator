import pandas as pd
from datetime import datetime

# Leer el archivo CSV
df = pd.read_csv('output.csv')

# Función para obtener el nombre del día en español
def get_day_name(date_str):
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return days[date_obj.weekday()]

start_date = datetime.strptime(df['Fecha'].iloc[0], '%Y-%m-%d')
end_date = datetime.strptime(df['Fecha'].iloc[-1], '%Y-%m-%d')

# Generar HTML
html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Predicando la palabra de DIOS Con Alegria</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f9f9f9;
        }}
        h1 {{
            color: #2c3e50;
        }}
        h2, h3 {{
            color: #2980b9;
        }}
        table {{
            margin: 0 auto;
            border-collapse: collapse;
            width: 80%;
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
            text-align: left;
        }}
    </style>
</head>
<body>
    <h1>Predicando la palabra de DIOS Con Alegria</h1>
    <h2>Rol de la semana</h2>
    {start_date} - {end_date}
    <h3>Lecturas y funerales</h3>
    <table>
        <tr>
            <th>Día</th>
            <th>Hora</th>
            <th>Lectura</th>
            <th>Personas</th>
        </tr>
"""



# Poblar la tabla
for index, row in df.iterrows():
    day_name = get_day_name(row["Fecha"])
    if pd.notna(row["Mañana"]):
        personas = row["Mañana"].split(", ")
        if len(personas) == 2:
            if day_name == "Domingo":
                html += f"<tr><td>{day_name}</td><td>7 AM</td><td>1ra lectura, Salmo</td><td>{', '.join(personas)}</td></tr>"
            else:
                html += f"<tr><td>{day_name}</td><td>8 AM</td><td>1ra lectura, Salmo</td><td>{', '.join(personas)}</td></tr>"
        elif len(personas) == 3:
            if day_name == "Domingo":
                html += f"<tr><td>{day_name}</td><td>7 AM</td><td>1ra lectura, Salmo, 2a lectura</td><td>{', '.join(personas)}</td></tr>"
            else:
                html += f"<tr><td>{day_name}</td><td>8 AM</td><td>1ra lectura, Salmo, 2a lectura</td><td>{', '.join(personas)}</td></tr>"
        elif len(personas) == 4:
            if day_name == "Domingo":
                html += f"<tr><td>{day_name}</td><td>7 AM</td><td>1ra lectura, Salmo, 2a lectura, Monitor</td><td>{', '.join(personas)}</td></tr>"
            else:
                html += f"<tr><td>{day_name}</td><td>8 AM</td><td>1ra lectura, Salmo, 2a lectura, Monitor</td><td>{', '.join(personas)}</td></tr>"
    if pd.notna(row["Noche"]):
        personas = row["Noche"].split(", ")
        if len(personas) == 2:
            html += f"<tr><td>{day_name}</td><td>6 PM</td><td>1ra lectura, Salmo</td><td>{', '.join(personas)}</td></tr>"
        elif len(personas) == 3:
            html += f"<tr><td>{day_name}</td><td>6 PM</td><td>1ra lectura, Salmo, 2a lectura</td><td>{', '.join(personas)}</td></tr>"
        elif len(personas) == 4:
            html += f"<tr><td>{day_name}</td><td>6 PM</td><td>1ra lectura, Salmo, 2a lectura, Monitor</td><td>{', '.join(personas)}</td></tr>"
    if day_name == "Domingo" and pd.notna(row["Tarde"]):
        personas = row["Tarde"].split(", ")
        if len(personas) == 2:
            html += f"<tr><td>{day_name}</td><td>12:30 PM</td><td>1ra lectura, Salmo</td><td>{', '.join(personas)}</td></tr>"
        elif len(personas) == 3:
            html += f"<tr><td>{day_name}</td><td>12:30 PM</td><td>1ra lectura, Salmo, 2a lectura</td><td>{', '.join(personas)}</td></tr>"
        elif len(personas) == 4:
            html += f"<tr><td>{day_name}</td><td>12:30 PM</td><td>1ra lectura, Salmo, 2a lectura, Monitor</td><td>{', '.join(personas)}</td></tr>"

html += """
    </table>
    <h3>Rol de funerales</h3>
    <table>
        <tr>
            <th>Día</th>
            <th>Persona</th>
        </tr>
"""

# Poblar la tabla de funerales
for index, row in df.iterrows():
    day_name = get_day_name(row["Fecha"])
    if pd.notna(row["Funeral"]):
        html += f"<tr><td>{day_name}</td><td>{row['Funeral']}</td></tr>"

html += """
    </table>
    <p>Del Salmo 125 🙏</p>
    <p>Grandes cosas has hecho por nosotros, Señor</p>
</body>
</html>
"""

# Guardar en archivo HTML
with open("rol_de_la_semana.html", "w", encoding="utf-8") as file:
    file.write(html)

print("Archivo HTML creado exitosamente.")
