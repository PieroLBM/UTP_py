import datetime as time

NOMBRE = "Piero"
edad = 20
voltaje = 3.7
activo = True
fecha = time.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
# f-strings (Formato para cadenas de caracteres, letras)
print(f"Hola, {NOMBRE}. edad: {edad}")
print(f"Voltaje: {voltaje:.2f} V | Activo: {activo}")
print(f"Buenas tardes Ing, {NOMBRE}, su edad es: {edad} años, le adjunto los datos:")
print(f"voltaje de la bateria: {voltaje:.2f} V")
print(f"Estado es: {activo}")
print(f"fecha del correo: {fecha}")