import random as rd

Vingreso = []
for i in range(10):
    Vingreso.append(rd.randint(1, 100))

print("Lista original:")
print(Vingreso)

# Orden descendente (mayor a menor) usando bubble sort
Wdesc = Vingreso.copy()
for i in range(len(Wdesc)):
    for j in range(len(Wdesc)-1):
        if Wdesc[j] < Wdesc[j+1]:
            Wdesc[j], Wdesc[j+1] = Wdesc[j+1], Wdesc[j]

print("\nLista ordenada de mayor a menor:")
print(Wdesc)

# Orden ascendente (menor a mayor) usando bubble sort
Wasc = Vingreso.copy()
for i in range(len(Wasc)):
    for j in range(len(Wasc)-1):
        if Wasc[j] > Wasc[j+1]:
            Wasc[j], Wasc[j+1] = Wasc[j+1], Wasc[j]

print("\nLista ordenada en forma ascendente:")
print(Wasc)

print("\nLista ordenada en forma descendente:")
print(Wdesc)