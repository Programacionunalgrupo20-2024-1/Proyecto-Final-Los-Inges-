#Entradas en metros
b=float(0.20)
h=float(0.5)
recub=0.05
d=float(h-recub)
tipo="no liviano"
#Todo en megaPascales
fc=float(20)
fyt=float(420)
Vu=float(250)/1000
phi=0.75

if tipo=="liviano":
    lambda_=0.75
else:
    lambda_=1

s_max=d/2 # en metros
print("Espaciamiento maximo: " + str(round(s_max,2)))
Av_min1=1/16*fc**0.5*b*s_max/fyt
Av_min2=0.35*b*s_max/fyt
Av_min=max(Av_min1,Av_min2)
print("Area minima: " + str(Av_min*1000**2))


print("Solo colocar el numero")
print("Por ejemplo barra No: 3")

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
Area_resistente=Area*2/1000**2
print("Solicitacion a cortante: " + str(Vu))




Vc=fc**0.5/6*b*d*lambda_
Vc_phi=phi*Vc

if Vc_phi*0.5>=Vu:
    print("El concreto resiste sin refuerzo")
elif Vu<Vc_phi:
    print("Se requieren estribo minimos")
    while Av_min>Area_resistente:
        print("Escoger un numero mas grande")
        numero=int(input("Introduzca nuevo numero: "))
        Area=barras[numero]
        Area_resistente=Area*2
    print("Acero numero " + str(numero) + ". Separacion [m]: " + str(round(s_max,2)))
else:
    if Vu<=0.33*fc**0.5*b*d:
        
        s=phi*Area_resistente*fyt*d/(Vu-Vc_phi)
        
        if s>d/2:
            if numero==2:
                print(print("Acero numero " + str(numero) + ". Separacion [m]: " + str(round(s_max,2))))
            else:
                print("Se puede y debe disminuir la designacion del acero para no sobrereforzar")
                print("Acero numero " + str(numero) + ". Separacion [m]: " + str(round(s,2)))
        else:
            print("Acero numero " + str(numero) + ". Separacion [m]: " + str(round(s,2)))

    else:
        s=phi*Area_resistente*fyt*d/(Vu-Vc_phi)
        
        if s>d/4:
            print("Se puede y debe disminuir la designacion del acero para no sobrereforzar")
            print("Acero numero " + str(numero) + ". Separacion [m]: " + str(round(s,2)))
        elif s<=0.03:
            print("Aumentar la designacion de la barra")
        else:
            print("Acero numero " + str(numero) + ". Separacion [m]: " + str(round(s,2)))

    