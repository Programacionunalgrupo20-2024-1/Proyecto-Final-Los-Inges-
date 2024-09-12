#Entradas en metros
b=float(0.2)
h=float(0.5)
recub=0.05
d=float(h-recub)
dprima=float(recub)
#Todo en megaPascales
fc=float(20)
fy=float(500)
Mu=float(1984)/1000
phi=0.9
Es=200000
gamma=0.85

if fc<=28:
    beta=0.85
elif fc>=55:
    beta=0.65
else:
    beta=0.85-(0.05*(fc-28))/7
eps_u=0.003
eps_y=fy/Es

rho_max=gamma*beta*fc/fy*(eps_u/(eps_u+0.005))

As_max=rho_max*b*d
Mmax_phi=phi*As_max*fy*(d-(As_max*fy)/(2*gamma*fc*b))

As_min1=fc**0.5/(4*fy)*b*d
As_min2=1.4*b*d/fy
As_min=max(As_min1,As_min2)

print("ACERO MINIMO =" + str(round(As_min*1000**2,0)) + " mm2")

if Mu>Mmax_phi:
    M2=(Mu-Mmax_phi)/0.9
    As2=M2/(fy*(d-dprima))
    As=As_max+As2
    Asprima=As2
    rho_y=gamma*fc/fy*beta*eps_u/(eps_u+fy/Es)*dprima/d+Asprima/(b*d)
    rho=As/(b*d)
    

    if rho>rho_y:
        print("ACERO A TRACCION = " + str(round(As*1000**2,0)) + " mm2")
        print("ACERO A COMPRESION = "+ str(round(Asprima*1000**2,0)) + " mm2")
    else:
        a=(As-Asprima)*fy/(gamma*fc*b)
        c=a/beta
        fsprima=eps_u*Es*(c-dprima)/c
        Asprima=Asprima*fy/fsprima
        
        print("ACERO A TRACCION = " + str(round(As*1000**2,0)) + " mm2")
        print("ACERO A COMPRESION = "+ str(round(Asprima*1000**2,0)) + " mm2")
else:
    print("NO USA ACERO A COMPREISON")
    As=(0.9*d-(0.81*d**2-1.8*Mu/(gamma*fc*b))**0.5)/(0.9*fy/(gamma*fc*b))
    As=max(As,As_min)
    Asprima=0
    print("ACERO A TRACCION = " + str(round(As*1000**2,0)) + " mm2")
    print("ACERO A COMPRESION = "+ str(round(Asprima*1000**2,0)) + " mm2")





