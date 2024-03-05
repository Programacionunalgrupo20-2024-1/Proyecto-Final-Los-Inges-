# Proyecto-Final-Los-Inges-
Calculadora de diseño de refuerzo de vigas de concreto. Toma valores de un software de analisis estructural como sap2000 donde, tras apicar cargas y definir los apoyos, se obtiene un diagrama de momento y cortante. Estos diagramas son exportados al programa,
grafica las envolventes de momento y cortante teniendo en cuenta la norma sismo resistente (NSR-10). Una vez cuenta con estas envolventes se empieza a reforzar la viga con los requerimientos de cuantia de refuerzo para las solicitaciones, de aqui tienen que determinar
cuantas varillas de refuerzo colocar, especificando el numero, la longitud de estas y su ubicacion a lo largo de la viga. Adicionalemente tendra en cuenta las longitudes comerciales que existen para realizar los traslapos correspondientes considerando las secciones donde
no se puede colocar traslapo especificado por la norma. Asi mismo, para el diseño a cortante determinara cuales son los estribos requeridos y como estan distribuidos a lo largo de la viga. Al final el programa deberia mostrar datos del refuerzo usado, su cantidad, distribucion  
y longitud, a su vez que la forma de la varilla usada, pues en los extremos se debe usar ganchos. Finalmente se obtendra una lista con la forma de la varilla, la longitud, cantidad si hay varillas tipo, y peso, de manera que se puedan ordenar el proveedor.

Caracteristicas:

Interfaz grafica donde se muestren todas las vigas tipo del proyecto. Haciendo clic a cada una aprazcan sus geometrias con sus diagramas y envolventes. Que aparezca  y de ahi se entre a diseñar por el usuario. Que una vez se esta diseñando se vea la distribucion del refuerzo
dentro de la viga.

Al final cuando se analicen todas las vigas, se termine el diseño y se obtenga una lista (base de datos) con los numeros de varillas, las longitudes, las formas, y los pesos de las varillas tipo, a su vez que un codigo que identifique a que varilla corresponden. Esto es para que
puedan mandarse al fabricante de varilla y las diseñe a medida para la obra.


