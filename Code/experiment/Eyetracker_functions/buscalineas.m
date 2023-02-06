
function [indices]=buscalineas(celda, ABC);

%Enceuntra las lineas en las que  hay mnensajes que comienzen con ABC y estan seguidas por un numero.
a=celda
indices=strmatch(ABC,a);
% for i=2:length(indices)    
%     a(indices(i))
%     temp=sscanf(char(a(indices(i))),[ABC '%s']) % Setear aca la estructura de lo que se queire buscar.
%     
% end