
function gazeenvideo(video);

 %Este programa agarra un video .avi, y frame por frame le pinta un punto
 %de color en donde le digo (x,y) que pueden ser  o no la posicion del ojo.
 
 
fil=video;
D=aviinfo(fil);
NF=D.NumFrames;
W=D.Width;H=D.Height; % El ancho y alto, debe estar ajustado a la calibracion de x e y.
BS=3; % La mitad del tamaño con el que dibuja el punto de fijacion
T=[1:NF];

X=round(W/2+30*cos(2*pi*T/NF)); % Un circulo de movimiento, como ejemplo
Y=round(H/2+30*sin(2*pi*T/NF));

for i=1:NF
    T=aviread(fil,i);
    temp=T.cdata;
   temp(Y(i)-BS:Y(i)+BS,X(i)-BS:X(i)+BS,1)=256; % Dibjar en rojo
   temp(Y(i)-BS:Y(i)+BS,X(i)-BS:X(i)+BS,2)=0; % Setear a 256 para verde...
   temp(Y(i)-BS:Y(i)+BS,X(i)-BS:X(i)+BS,3)=0;

    te(i) = im2frame(temp);
end

movie2avi(te,'t3.avi');