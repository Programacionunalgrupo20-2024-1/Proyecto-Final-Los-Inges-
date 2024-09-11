#Entradas en metros
b=float(0.2)
h=float(0.4)
recub=0.05
d=float(h-recub)
tipo="no liviano"
#Todo en megaPascales
fc=float(20)
fyt=float(420)
Vu=float(120)/1000
phi=0.75

if tipo=="liviano":
    lambda_=0.75
else:
    lambda_=1

print("Por ejemplo barra No: 3")
print("Solo colocar el numero")
numero=int(input("Designacion de la barra para estribos simples: "))


barras={
    2: 32,
    3: 71,
    4: 129,
    5: 199,
    6: 284,
    7: 387,
    8: 510,
    9: 645,
    10: 819,
    11: 1006,
    14: 1452,
    18: 2581
}


Area=barras[numero]
Area_resistente=Area*2 
