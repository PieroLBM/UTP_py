valor_txt = input("Ingrese un valor de tempertura: ")
#print(f"El valor ingresado es: {valor_txt} °C")
t=float(valor_txt)
if t >= 30:
    print("Alerta de temperatura alta")
elif t < 0:
    print("Alerta de temperatura baja")
else:
    print("Temperatura normal")