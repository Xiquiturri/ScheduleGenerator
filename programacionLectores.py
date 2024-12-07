from datetime import datetime,timedelta
import random
import pandas as pd
import json
import locale
from datetime import date 
from collections import deque
import os
from Modelos.evento import evento

#path 
event_metadata_relative_path=os.path.join("Metadata","event_metadata.csv")
# Set the locale to Spanish 
locale.setlocale(locale.LC_TIME, 'es_ES')

class CustomEncoder(json.JSONEncoder): 
    def default(self, obj): 
        if isinstance(obj, date): 
            return obj.isoformat() 
        return super().default(obj)

class Lector:
    def __init__(self, nombre):
        self.nombre = nombre
        self.preferencias = {}
        self.fechas_no_disponibles = []

    def agregar_preferencia(self, dia, momento):
        if dia not in self.preferencias:
            self.preferencias[dia] = momento

    def agregar_fecha_no_disponible(self, fecha):
        self.fechas_no_disponibles.append(fecha)

    def __repr__(self):
        return f"Lector(nombre={self.nombre}, preferencias={self.preferencias}, fechas_no_disponibles={self.fechas_no_disponibles})"

class GestionLectores:
    def __init__(self):
        self.lectores = []
        self.lectores_to_save={}
        self.df_metadata = pd.read_csv(event_metadata_relative_path)
    
    def save_lectores_to_json(self, file_path):
        # Convert lectores to a serializable format
        lectores_serializable = {nombre: lector.__dict__ for nombre, lector in self.lectores_to_save.items()}
        with open(file_path, 'w') as json_file:
            json.dump(lectores_serializable, json_file, indent=4, cls=CustomEncoder)

    def load_lectores_from_json(self, file_path):
        with open(file_path, 'r') as json_file:
            lectores_data = json.load(json_file)
        self.lectores = []
        for nombre, data in lectores_data.items():
            lector = Lector(nombre)
            lector.preferencias = data['preferencias']
            lector.fechas_no_disponibles = [datetime.strptime(fecha, '%Y-%m-%d').date() for fecha in data['fechas_no_disponibles']]
            #self.lectores[nombre] = lector
            self.lectores.append(lector)

    def ingresar_lectores(self):
        while True:
            nombre = input("Ingresa el nombre del lector (o 'fin' para terminar): ")
            if nombre.lower() == 'fin':
                break
            self.lectores_to_save[nombre] = Lector(nombre)

    def ingresar_preferencias(self):
        momentos_validos = self.df_metadata.iloc[:,:2] #selecciona dia y hora
        for lector in self.lectores_to_save.values():
            print(momentos_validos) #opciones de dias y horarios 
            preferencias = input(lector.nombre + " Selecciona tus preferencias(ej:1,2,3) o 'fin' para terminar: ")
            if preferencias =='fin':
                continue
            preferencias_list = [int(x) for x in preferencias.split(",")]
            for preferencia in preferencias_list:
                dia = momentos_validos['Dia'][preferencia]
                hora = pd.to_datetime(momentos_validos['Hora'][preferencia]).strftime("%H:%M:%S")
                lector.agregar_preferencia(dia,hora)
                print(hora)

    def ingresar_fechas_no_disponibles(self):
        for lector in self.lectores_to_save.values():
            print(f"\nFechas no disponibles para {lector.nombre}:")
            while True:
                fecha = input("  Ingresa la fecha (YYYY-MM-DD) o 'fin' para terminar: ")
                if fecha.lower() == 'fin':
                    break
                lector.agregar_fecha_no_disponible(datetime.strptime(fecha, '%Y-%m-%d').date())
    

    def generar_horarios(self, start_date, end_date):

        horarios = []
        delta = timedelta(days=1)
        current_date = start_date

        while current_date <= end_date:
            dia_semana = current_date.strftime('%A')
            # Filter rows where 'Dia' matches dia_semana
            matching_rows = self.df_metadata[self.df_metadata['Dia'] == dia_semana]
            # Iterate over matching rows and append information to horarios
            for _, row in matching_rows.iterrows():
                if pd.isna(row['Obligado']):
                    horarios.append(evento(
                        current_date,
                        {dia_semana: row['Hora']},
                        row['Cupo'],
                        row['Default'],
                        row['Obligado']
                    ))
                else:
                    horarios.append(evento(
                        current_date,
                        {row['Obligado']: row['Hora']},
                        row['Cupo'],
                        row['Default'],
                        row['Obligado']
                    ))
            current_date+=delta

        # Convert list of lectores to deque
        random.shuffle(self.lectores)

        lectores = deque(self.lectores)
        random.shuffle(horarios)
        # Ensure each lector appears at least once
        eventos_vacios = True
        evento_obligado=set()
        while eventos_vacios:
            estado_de_eventos = []
            for lector in list(lectores):
                lista_preferencias = list(lector.preferencias)
                random.shuffle(lista_preferencias)
                asignado = False
                while not asignado:
                    for _evento in horarios:
                        if _evento.fecha in lector.fechas_no_disponibles:
                            asignado =True
                            break
                        
                        #-----DEFAULT-------- Si es unn evento por defecto hay que rellenarlo con un lector por defecto.
                        if not pd.isna(_evento.default):
                            if _evento.vacio:
                                _evento.participante.add(Lector(_evento.default))
                            continue

                        for pref in lista_preferencias:
                            value = lector.preferencias[pref]
                            momento = {pref:value}
                            #-----PREFERENCIAS--------verificar que los dias y horas correspondan del schedule y la preferencia
                            if (_evento.momento == momento and lector not in _evento.participante and _evento.vacio and pd.isna(_evento.obligado)and pd.isna(_evento.default)) or not lector.preferencias:
                                _evento.participante.add(lector)
                                asignado = True
                                break
                            #-----OBLIGADO--------Si es evento obligado y lector preferencia va de acorde, entonces agregarlo si es que no aparece en el set de evento obligado.
                            elif (not pd.isna(_evento.obligado) and _evento.vacio and _evento.momento == momento and lector not in evento_obligado):
                                _evento.participante.add(lector)
                                evento_obligado.add(lector)
                                continue
                        #-----SIN PREFERENCIAS--------
                        if (lector not in _evento.participante and _evento.vacio and pd.isna(_evento.obligado)and pd.isna(_evento.default)) and( not lector.preferencias or ((len(lista_preferencias)==1) and pref not in ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"])):
                            _evento.participante.add(lector)
                            asignado = True
                        if _evento == horarios[-1] and (asignado ==False):
                            asignado = True
                            break
                        if(asignado):
                            break
                lectores.rotate(-1)  # Move the lector to the end of the queue
                
                for _evento_status in horarios:
                    estado_de_eventos.append(_evento_status.vacio)
                if not (True in estado_de_eventos):
                    eventos_vacios=False

        for _evento in horarios:
            nombres_participantes=[]
            for participante in _evento.participante:
                nombres_participantes.append(participante.nombre)
            print(f"Para {_evento.momento}, los participantes son: {nombres_participantes}")
        return horarios

    def generar_tabla(self, horarios):
        data = {'Fecha': [], 'Mañana': [],'Funeral':[], 'Tarde': [], 'Noche': []}
        for fecha in sorted(horarios.keys()):
            data['Fecha'].append(fecha.strftime('%Y-%m-%d'))
            if 'mañana' in horarios[fecha]:
                data['Mañana'].append(', '.join(horarios[fecha]['mañana'])) 
            else: 
                data['Mañana'].append('NA')
            if 'tarde' in horarios[fecha]:
                data['Tarde'].append(', '.join(horarios[fecha]['tarde']))
            else:
                data['Tarde'].append('NA')
            if 'noche' in horarios[fecha]:
                data['Noche'].append(', '.join(horarios[fecha]['noche']))
            else:
                data['Noche'].append('NA')
            if 'funeral' in horarios[fecha]:
                data['Funeral'].append(', '.join(horarios[fecha]['funeral']))
            else:
                data['Funeral'].append('NA')

        
        df = pd.DataFrame(data)
        df.to_csv('output.csv', index=False)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # Ensure the full table is printed
            print(df.to_string(index=False))

# Ejecución
gestion = GestionLectores()

while True:
    add_lectores=input("Desea agregar lectores? si o no -> ")
    if(add_lectores.lower()=="si"):
        gestion.ingresar_lectores()
        gestion.ingresar_preferencias()
        gestion.ingresar_fechas_no_disponibles()
        gestion.save_lectores_to_json("lectores_db.json")
        break
    elif(add_lectores.lower()=="no"):
        break

gestion.load_lectores_from_json("lectores_db.json")

#start_date = datetime.datetime.strptime(input("Ingresa la fecha de inicio (YYYY-MM-DD): "), '%Y-%m-%d').date()
#end_date = datetime.datetime.strptime(input("Ingresa la fecha de fin (YYYY-MM-DD): "), '%Y-%m-%d').date()

start_date = datetime.strptime("2024-12-16", '%Y-%m-%d').date()
end_date = datetime.strptime("2024-12-22", '%Y-%m-%d').date()

horarios = gestion.generar_horarios(start_date, end_date)
#horarios_asignados = gestion.asignar_lectores(horarios)
#gestion.generar_tabla(horarios)
