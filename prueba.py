import datetime as time
import random as rd
nombre = "Piero."
fecha = time.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
v = rd.randint(0, 1023)
print("Buenas tardes Ing. se le envia los datos de las muestras de voltajes a continuacion:")
print("voltaje medido:"+ str(v)) #cuando se utiliza el signo "+" no puede sumarse letras con numeros, es por ello que se agregar el comando str("variable")
print("Voltaje medido:", v)  # en este caso solo se usa la coma "," y no es necesario agregar el comando str("variable")
print("Con fecha:", fecha) 
print("Saludos,", nombre)
