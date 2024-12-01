import datetime
import random
import pandas as pd
import json
import locale
from datetime import date 

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
            self.preferencias[dia] = []
        self.preferencias[dia].append(momento)

    def agregar_fecha_no_disponible(self, fecha):
        self.fechas_no_disponibles.append(fecha)

    def __repr__(self):
        return f"Lector(nombre={self.nombre}, preferencias={self.preferencias}, fechas_no_disponibles={self.fechas_no_disponibles})"

class GestionLectores:
    def __init__(self):
        self.lectores = {}
        self.lectores_to_save={}
    
    def save_lectores_to_json(self, file_path):
        # Convert lectores to a serializable format
        lectores_serializable = {nombre: lector.__dict__ for nombre, lector in self.lectores_to_save.items()}
        with open(file_path, 'w') as json_file:
            json.dump(lectores_serializable, json_file, indent=4, cls=CustomEncoder)


    def load_lectores_from_json(self, file_path):
        with open(file_path, 'r') as json_file:
            lectores_data = json.load(json_file)
        self.lectores = {}
        for nombre, data in lectores_data.items():
            lector = Lector(nombre)
            lector.preferencias = data['preferencias']
            lector.fechas_no_disponibles = [datetime.fromisoformat(fecha).date() for fecha in data['fechas_no_disponibles']]
            self.lectores[nombre] = lector




    def ingresar_lectores(self):
        while True:
            nombre = input("Ingresa el nombre del lector (o 'fin' para terminar): ")
            if nombre.lower() == 'fin':
                break
            self.lectores_to_save[nombre] = Lector(nombre)

    def ingresar_preferencias(self):
        dias_validos = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
        momentos_validos = ['mañana', 'tarde', 'noche','funeral']

        for lector in self.lectores_to_save.values():
            print(f"\nPreferencias para {lector.nombre}:")
            while True:
                dia = input(f"  Ingresa el día de la semana para {lector.nombre} (o 'fin' para terminar): ").capitalize()
                if dia.lower() == 'fin':
                    break
                if dia in dias_validos:
                    momento = input(f"  Ingresa el momento del día para {dia} (mañana, tarde, noche): ").lower()
                    if momento in momentos_validos:
                        lector.agregar_preferencia(dia, momento)
                    else:
                        print("  Momento del día incorrecto. Usa 'mañana', 'tarde','funeral' o 'noche'.")
                else:
                    print("  Día de la semana incorrecto. Usa un día válido (Lunes, Martes, etc.).")

    def ingresar_fechas_no_disponibles(self):
        for lector in self.lectores_to_save.values():
            print(f"\nFechas no disponibles para {lector.nombre}:")
            while True:
                fecha = input("  Ingresa la fecha (YYYY-MM-DD) o 'fin' para terminar: ")
                if fecha.lower() == 'fin':
                    break
                lector.agregar_fecha_no_disponible(datetime.datetime.strptime(fecha, '%Y-%m-%d').date())

    def generar_horarios(self, start_date, end_date):
        horarios = {}
        delta = datetime.timedelta(days=1)
        current_date = start_date



        while current_date <= end_date:
            dia_semana = current_date.strftime('%A')
            dia_semana_es = current_date.strftime('%A')
            if(dia_semana =="lunes" or dia_semana == "sábado"):
                horarios[current_date] = {'funeral': [], 'noche': []}
            elif(dia_semana =="martes" or dia_semana =="miércoles" or dia_semana == "viernes"):
                horarios[current_date] = {'mañana':[],'funeral': [], 'noche': []}
            elif(dia_semana=="jueves"):
                horarios[current_date] = {'mañana':[],'funeral': []}
            elif(dia_semana=="domingo"):
                horarios[current_date] = {'mañana':[],'tarde':[],'funeral': [],'noche':[]}
            current_date += delta
        # Get a list of lectores and shuffle it 
        lectores = list(self.lectores.values()) 
        random.shuffle(lectores)
            # Ensure each lector appears at least once
        for lector in lectores:
            assigned = False
            while not assigned:
                random_date = random.choice(list(horarios.keys()))
                random_event = random.choice(list(horarios[random_date].keys()))
                dia_semana_random = random_date.strftime('%A')
                if random_event != 'funeral' and len(horarios[random_date][random_event]) < 2 and dia_semana_random != 'domingo' and self.has_preference(lector,random_event,dia_semana_random) and not self.is_in_date(lector,horarios[random_date]):
                    horarios[random_date][random_event].append(lector.nombre)
                    assigned = True
                elif random_event != 'funeral' and len(horarios[random_date][random_event]) < 4 and dia_semana_random == 'domingo' and random_event == 'tarde' and self.has_preference(lector,random_event,dia_semana_random) and not self.is_in_date(lector,horarios[random_date]):
                    horarios[random_date][random_event].append(lector.nombre)
                    assigned = True
                elif random_event != 'funeral' and len(horarios[random_date][random_event]) < 3 and dia_semana_random == 'domingo' and self.has_preference(lector,random_event,dia_semana_random) and not self.is_in_date(lector,horarios[random_date]):
                    horarios[random_date][random_event].append(lector.nombre)
                    assigned = True
                
                elif not lector.preferencias and random_event !='funeral':
                    if len(horarios[random_date][random_event]) < 2 and dia_semana_random != 'domingo' and dia_semana_random != 'sábado':
                        horarios[random_date][random_event].append(lector.nombre)
                        assigned = True
                    elif len(horarios[random_date][random_event]) < 4 and dia_semana_random == 'domingo' and random_event == 'tarde':
                        horarios[random_date][random_event].append(lector.nombre)
                        assigned = True
                    elif len(horarios[random_date][random_event]) < 3 and dia_semana_random == 'domingo':
                        horarios[random_date][random_event].append(lector.nombre)
                        assigned = True

        # Get a list of lectores and shuffle it 
        lectores = list(self.lectores.values()) 
        random.shuffle(lectores)

        current_date = start_date
        eventos_completos=False
        while current_date <= end_date:
            dia_semana = current_date.strftime('%A')

            for lector in lectores:
                if current_date not in lector.fechas_no_disponibles:
                    
                    if dia_semana in lector.preferencias:
                        eventos_completos=False
                        print(dia_semana)
                        preferencia=list(lector.preferencias[dia_semana])
                        random.shuffle(preferencia)
                        
                        if len(horarios[current_date][preferencia[0]]) < 4 and dia_semana =="domingo" and preferencia[0] =='tarde' and not self.is_in_date(lector,horarios[current_date]):
                            horarios[current_date][preferencia[0]].append(lector.nombre)
                            eventos_completos=False
                        elif len(horarios[current_date][preferencia[0]]) < 3 and dia_semana =="domingo" and not self.is_in_date(lector,horarios[current_date]):
                            horarios[current_date][preferencia[0]].append(lector.nombre)
                            eventos_completos=False
                        elif len(horarios[current_date][preferencia[0]]) < 2 and dia_semana !="domingo" and not self.is_in_date(lector,horarios[current_date]):
                            horarios[current_date][preferencia[0]].append(lector.nombre)
                            eventos_completos=False
                    if not lector.preferencias:
                        momentos_validos = ['mañana', 'tarde', 'noche']
                        random.shuffle(momentos_validos)
                        if momentos_validos[0] in horarios[current_date] and dia_semana != 'sábado':
                            if len(horarios[current_date][momentos_validos[0]]) < 4 and dia_semana =="domingo" and momentos_validos[0] =='tarde' and not self.is_in_date(lector,horarios[current_date]):
                                horarios[current_date][momentos_validos[0]].append(lector.nombre)
                                eventos_completos=False
                            elif len(horarios[current_date][momentos_validos[0]]) < 3 and dia_semana =="domingo" and not self.is_in_date(lector,horarios[current_date]):
                                horarios[current_date][momentos_validos[0]].append(lector.nombre)
                                eventos_completos=False
                            elif len(horarios[current_date][momentos_validos[0]]) < 2 and dia_semana !="domingo" and not self.is_in_date(lector,horarios[current_date]):
                                horarios[current_date][momentos_validos[0]].append(lector.nombre)
                                eventos_completos=False
                    elif dia_semana == "domingo":
                        if len(horarios[current_date]["tarde"]) == 4 and dia_semana =="domingo" and len(horarios[current_date]["mañana"]) == 3 and len(horarios[current_date]["noche"]) == 3:
                            eventos_completos=True
                    elif dia_semana != "domingo" and dia_semana !="sábado":
                        eventos_completos_aux=False
                        eventos_completos_aux2=False
                        if "mañana" in horarios[current_date]:
                            if len(horarios[current_date]["mañana"]) ==2:
                                eventos_completos_aux=True
                        else:
                            eventos_completos_aux=True
                        if "noche" in horarios[current_date]:
                            if len(horarios[current_date]["noche"])==2:
                                eventos_completos_aux2=True
                        else: eventos_completos_aux2=True
                        if eventos_completos_aux and eventos_completos_aux2:
                            eventos_completos=True
                        else:
                            eventos_completos=False
                    
                    if "noche" in horarios[current_date] and dia_semana == "sábado":
                        if len(horarios[current_date]["noche"]) < 3:
                            while len(horarios[current_date]["noche"]) < 3:
                                horarios[current_date]["noche"].append('Confirmantes')
                            eventos_completos=True
                if(eventos_completos):
                    current_date += delta
                    break
        # Ensure no lector is repeated in funeral events within a week
        assigned_lectores = set()
        for current_date in horarios:
            if 'funeral' in horarios[current_date]:
 
                for lector in horarios[current_date]['funeral']:
                    assigned_lectores.add(lector)
                for lector in lectores:
                    tarde = False 
                    for preferencias in lector.preferencias.values(): 
                        if "tarde" in preferencias or "noche" in preferencias: 
                            tarde = True 
                            break
                    if lector.nombre not in assigned_lectores and current_date not in lector.fechas_no_disponibles and (tarde or not lector.preferencias) and lector.nombre != "Diocelina":
                        if len(horarios[current_date]['funeral']) < 1:
                            horarios[current_date]['funeral'].append(lector.nombre)
                            assigned_lectores.add(lector.nombre)
                            break
        return horarios

    def has_preference(self, lector, preference_check,dia_check):
        for dia,momentos in lector.preferencias.items():
            if preference_check in momentos and dia.lower() == dia_check.lower():
                return True
        return False
    def is_in_date(self, lector, fecha):
        for momento, personas in fecha.items():
            if lector.nombre in personas:
                return True
        return False

        
    




    def asignar_lectores(self, horarios):
        for fecha in horarios:
            dia_semana = fecha.strftime('%A')
            for momento in horarios[fecha]:
                preferences_to_check = ["mañana", "tarde", "noche"]
                if len(horarios[fecha][momento]) < 3 and dia_semana =="sábado" and momento !='funeral':
                    while len(horarios[fecha][momento]) < 3:
                        horarios[fecha][momento].append('Confirmantes')

                elif len(horarios[fecha][momento]) < 4 and dia_semana =="domingo" and momento =='tarde':
                    # Añadir lectores adicionales para llenar los espacios vacíos
                    #lectores_disponibles = [ lector for lector in self.lectores.values() if all(lector.nombre not in horarios[fecha][m] for m in horarios[fecha]) and fecha not in lector.fechas_no_disponibles and self.has_preference(lector,momento,dia_semana)]
                    #lectores_disponibles = lectores_disponibles + [lector for lector in self.lectores.values() if not lector.preferencias]
                    lectores_disponibles = [ lector for lector in self.lectores.values() if all(lector.nombre not in horarios[fecha][m] for m in horarios[fecha]) and fecha not in lector.fechas_no_disponibles and not lector.preferencias]
                    random.shuffle(lectores_disponibles)
                    while len(horarios[fecha][momento]) < 4 and lectores_disponibles:
                        horarios[fecha][momento].append(lectores_disponibles.pop(0).nombre)

                elif len(horarios[fecha][momento]) < 3 and dia_semana =="domingo" and momento !='funeral':
                    # Añadir lectores adicionales para llenar los espacios vacíos
                    #lectores_disponibles = [ lector for lector in self.lectores.values() if all(lector.nombre not in horarios[fecha][m] for m in horarios[fecha]) and fecha not in lector.fechas_no_disponibles and self.has_preference(lector,momento,dia_semana)]
                    lectores_disponibles = [ lector for lector in self.lectores.values() if all(lector.nombre not in horarios[fecha][m] for m in horarios[fecha]) and fecha not in lector.fechas_no_disponibles and not lector.preferencias]
                    #lectores_disponibles = lectores_disponibles + [lector for lector in self.lectores.values() if not lector.preferencias]
                    random.shuffle(lectores_disponibles)
                    while len(horarios[fecha][momento]) < 3 and lectores_disponibles:
                        horarios[fecha][momento].append(lectores_disponibles.pop(0).nombre)

                elif len(horarios[fecha][momento]) < 2 and dia_semana !="domingo" and momento !='funeral':
                    # Añadir lectores adicionales para llenar los espacios vacíos
                    #lectores_disponibles = [ lector for lector in self.lectores.values() if all(lector.nombre not in horarios[fecha][m] for m in horarios[fecha]) and fecha not in lector.fechas_no_disponibles and self.has_preference(lector,momento,dia_semana)]
                    #lectores_disponibles = lectores_disponibles + [lector for lector in self.lectores.values() if not lector.preferencias]
                    lectores_disponibles = [ lector for lector in self.lectores.values() if all(lector.nombre not in horarios[fecha][m] for m in horarios[fecha]) and fecha not in lector.fechas_no_disponibles and not lector.preferencias]
                    random.shuffle(lectores_disponibles)
                    while len(horarios[fecha][momento]) < 2 and lectores_disponibles:
                        horarios[fecha][momento].append(lectores_disponibles.pop(0).nombre)

                elif len(horarios[fecha][momento]) < 1 and momento=='funeral':
                    # Añadir lectores adicionales para llenar los espacios vacíos
                    lectores_disponibles = [ lector for lector in self.lectores.values() if lector.nombre not in horarios[fecha][momento] and fecha not in lector.fechas_no_disponibles ]
                    while True:
                        random.shuffle(lectores_disponibles)
                        if(lectores_disponibles[0] != "Diocelina"):
                            break
                    while len(horarios[fecha][momento]) < 1 and lectores_disponibles:
                        horarios[fecha][momento].append(lectores_disponibles.pop(0).nombre)
                
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

""" while True:
    add_lectores=input("Desea agregar lectores? si o no -> ")
    if(add_lectores.lower()=="si"):
        gestion.ingresar_lectores()
        gestion.ingresar_preferencias()
        gestion.ingresar_fechas_no_disponibles()
        gestion.save_lectores_to_json("lectores_db.json")
        break
    elif(add_lectores.lower()=="no"):
        break """

gestion.load_lectores_from_json("lectores_db.json")

#start_date = datetime.datetime.strptime(input("Ingresa la fecha de inicio (YYYY-MM-DD): "), '%Y-%m-%d').date()
#end_date = datetime.datetime.strptime(input("Ingresa la fecha de fin (YYYY-MM-DD): "), '%Y-%m-%d').date()

start_date = datetime.datetime.strptime("2024-12-02", '%Y-%m-%d').date()
end_date = datetime.datetime.strptime("2024-12-08", '%Y-%m-%d').date()

horarios = gestion.generar_horarios(start_date, end_date)
#horarios_asignados = gestion.asignar_lectores(horarios)
gestion.generar_tabla(horarios)
