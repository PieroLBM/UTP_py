import datetime as dt
import random as rd

nombre = "Piero"
fecha = dt.datetime.now().strftime("%d/%m/%y, %H:%M:%S")


print("Buenas tardes jefe, le saluda " + nombre, "le adjunto las muestras medidas")
print("valor del voltaje medido: " + str(v))
print(fecha)
#10 salidas de  bajo alto, de temperatura, 
#correo electrónico con 10 salidas con cada salida con un valor alto, medio y bajo, estoy en lo correcto?
for i in range(10):
    v = rd.randint(0 , 50)

