%% Enceuntra las lineas en las que  hay mensajes de la forma trial(iesimo).
indices=strmatch('MSG',a);
for i=2:length(indices)    
    a(indices(i))
    temp=sscanf(char(a(indices(i))),'MSG %s')
end


%% Busca en el .asc las lineas donde hay mensaje y me dice cuales son.
index=zeros(1200,1);
contador=0;
for i=1:length(a)
    dat=char(a(i));
    if strcmp('MSG',dat(1:3))==1
        contador=contador+1;
        index(contador)=i;
%        disp([num2str(i) char(a(i)) ])
    end
end

%% Arma una matriz que tiene tiempo de comienzo y numero de trial.
 M=nan(length(index),2);
for i=1:21731
    temp=sscanf(char(a(i)),'MSG %f Empieza programa')   
end

%% Arma una matriz con los datos de t, posicion x-y y tamaño pupila.
 S=nan(length(a),4);
for i=1:length(a)
    temp=sscanf(char(a(i)),'%f %f %f %f ...');
    if length(temp)>=4
       S(i,:)=temp(1:4);
    end    
end

%% Borra las filas con  datos no validos (nan)

Index=find(isnan(Datosarca2sinc(:,1)));
Datosarca2sinc(Index,:)=[];

%% Toma un intervalo de 100ms anets y 900ms despues del comienzo del y lo escribe en la mtriz P.
P=nan(length(S),2); %arma la matriz P (pupil size)
%M(:,1); % la cloumna de los tiempos de trials.
for i=1:length(M);
    for s=1:length(S);
        if S(s,1)>=(M(i,1)-100) && S(s,1)<=M(i,1);
            P(s,:)=S(s,[1 4]);

        elseif S(s,1)<=(M(i,1)+900) && S(s,1)>=M(i,1);
            P(s,:)=S(s,[1 4]);
        end
    end
end

%% Es mucho mas rapido, usa la funcion find del matlab
P=nan(1200,2002,4); %arma la matriz P (pupil size)
for i=1:length(M);
    index=find(((M(i,1)-100)<=S(:,1) & S(:,1)<=M(i,1))| ((M(i,1)+900)>=S(:,1) & S(:,1)>=M(i,1))) ;
    P(i,1:length(index),:)=S(index,:);
end

xdata=(1:2002)/2-100;

plot(xdata,tamapupila')

isnan(mean(tamapupila'))

find(isnan(mean(tamapupila')))

tamapupila2(find(isnan(mean(tamapupila'))),:)=[];

%%
I=find(Datosarca2(:,1)>91178);
L=length(I)
Datosarca2sinc=nan(L,4);
Datosarca2sinc(I,:)=Datosarca2(I,:);

[I J]=find(isnan(vistos))