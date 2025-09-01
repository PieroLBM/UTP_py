import datetime as time
import random as rd
nombre = "Piero."
fecha = time.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
print("Buenas tardes Ing. se le envia los datos de las muestras de voltajes a continuacion:")
print("Con fecha:", fecha) 
for i in range(10):
    v = rd.randint(0, 1023) #valor aleatorio del 1 y 100
    if v < 100: 
       print("valor bajo: " + str(v))
    elif v < 500:
      print("valor medio: " + str(v))
     
