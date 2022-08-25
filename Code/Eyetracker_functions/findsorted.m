function ind=findsorted(data,value)
%busca el indice de un valor en un vector ordenado
%data=sort(data);
%ind=find(data>value,1);

if value<data(1)%si el valor es menor que el primero
    ind=1;
    return
elseif value>data(end)%si el valor es mayor que el ultimo
    ind=length(data);
    return
end
maxind=length(data);
minind=1;
currind=round(length(data)/2);
while data(currind)~=value
    if data(currind)>value
        maxind=currind;
        currind=round((maxind+minind)/2);
    else
        minind=currind;
        currind=round((maxind+minind)/2);
    end
end
ind=currind;
end

