
function Datos=borranovalidos(Datos, columna)
%% 
%Borra las filas con  datos no validos (nan) en la columna que le pidamos
%de la matriz de datos.

Index=find(isnan(Datos(:,columna)));
Datos(Index,:)=[];