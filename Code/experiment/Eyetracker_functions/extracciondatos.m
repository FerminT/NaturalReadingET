function [Datos]=extracciondatos(archivo, S);

%%
% Toma  de todo el .asc solo desde donde comienzan los samples (S) para abajo, hay que setearlo en cada .asc mirandolo 
% con el notepad.

filename=archivo;
fid = fopen(filename);
C = textscan(fid, '%s','HeaderLines',S,'delimiter', '\n');
fclose(fid);
a=C{1};

%%
%Toma la lectura del .asc como strings y lo transforma en una matriz solo
%con samples validos. Esto si solo pedimos gaze y tamaño de pupila.
%Ordenados por columnas esta tiempo gazex, gazey y tamaño de pupila.
data=a;

Datos=nan(length(data),4);
for i=1:length(data);
    temp=sscanf(char(data(i)),'%f'); %Setearlo de acuerdo a la estructura del  .asc
    if length(temp)==4
        Datos(i,:)=temp;
    end    
end
