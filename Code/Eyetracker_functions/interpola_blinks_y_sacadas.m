function todo=interpola_blinks_y_sacadas(todo)
% pupilsize=todo.samples(:,4);


if strcmp(todo.modo,'RTABLE') | strcmp(todo.modo,'MTABLE') %si es remoto o monocular
    todo=interpola_eventos(todo,todo.lesac,2:4);% saco sacadas left
    todo=interpola_eventos(todo,todo.resac,2:4);% saco sacadas right
%    todo=interpola_eventos(todo,todo.lebli,2:4);% saco blinks left
%    todo=interpola_eventos(todo,todo.rebli,2:4);% saco blinks right
elseif strcmp(todo.modo,'BTABLE') %si es binocular    
    todo=interpola_eventos(todo,todo.lesac,2:4);% saco sacadas left    
    todo=interpola_eventos(todo,todo.resac,5:7);% saco sacadas right
%    todo=interpola_eventos(todo,todo.lebli,2:4);% saco blinks left
%    todo=interpola_eventos(todo,todo.rebli,5:7);% saco blinks right

end


end

function todo=interpola_eventos(todo,eventos,indinterpola)
% saco eventos (puede ser blinks o sacadas) y los indremove pueden ser 2:4
% (ier ojo) o 5:7 (2do ojo) 
    tiempo=todo.samples(:,1);
    if isempty(eventos)
        return
    end

    eventstart=eventos(:,1);
    eventend=eventos(:,2);    
    
%    fprintf(1,'podria eliminar totalmente el ultimo evento\n');
    for i=1:length(eventstart)-1%al ultimo lo dejo como estaba
        %si el ultimo evento termina junto con la toma, da error. por eso
        %saque el ultimo. podria eliminar totalmente el ultimo (de todo.samples y
        %de todo.lesac,lefix,resac,refix)
        
%        indstart=find(tiempo>eventstart(i),1);
%        indend=find(tiempo>eventend(i),1);
       indstart=findsorted(tiempo,eventstart(i));
       indend=findsorted(tiempo,eventend(i));       
       
       
        for j=1:length(indinterpola) 
            ind=indinterpola(j);
            valstart=todo.samples(indstart-1,ind);
            valend=todo.samples(indend+1,ind);            
            todo.samples(indstart:indend,ind)=valstart+((indstart:indend)-indstart)*(valend-valstart)/(indend-indstart);
        end

    end
end

function ind=findsorted(data,value)
%busca un indice de un valor en un vector ordenado
%busqueda por biparticion del intervalo.
%data=sort(data);
%ind=find(data>value,1);

maxind=length(data);
minind=1;
currind=round(length(data)/2);
while (data(currind)~=value && maxind-minind>1)
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
