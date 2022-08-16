function [VALEN] = calcula_distribucion(palpath,ind)

load([palpath,ind '_palabras.mat']);

cat = zeros(size(palabras));
    for indpal=1:length(cat)
        temp = ismember(palabras(indpal).catgramsimple,'anv'); % Coloca un cero donde la categoría NO es adjetivo, nombre o verbo.
        if ~isempty(temp); cat(indpal) = temp; end
    end
    
VALEN=struct([]);
palabra = {palabras(find(cat)).palabra};
catgramsimple = {palabras(find(cat)).catgramsimple};
freqglobal = [palabras(find(cat)).freq];
listapal = unique(palabra);

for indpal=1:length(listapal)                               %Recorre todas las palabras de listapal
    ind    = find(strcmpi(palabra,listapal(indpal)));        %Indices donde aparece esta palabra
    
    VALEN(indpal).palabra=palabra{ind(1)};                     
    VALEN(indpal).catgramsimple=catgramsimple{ind};
    VALEN(indpal).freqglobal=freqglobal(ind(1));
    VALEN(indpal).nAPAR = length(ind);
end

end
