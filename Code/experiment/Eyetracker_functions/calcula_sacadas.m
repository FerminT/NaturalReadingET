function [lesac resac]=calcula_sacadas(filename,sujnum)
% Esta función extrae toda la info relevante de las sacadas de un 
% archivo que tiene la estructura todo, generada por analiza_datos
% y la pone en un par de estructuras lesac y resac con muchos campos.
% filename: nombre del archivo (con path si no esta aca)
% sujnum: un numero de sujeto, para poner un campo en la estructura, para saber de que sujeto es cada sac
% Diego - Mayo/2010

%% cargo datos
tic
load(filename)
lesac=todo.lesac;
lebli=todo.lebli;
resac=todo.resac;
rebli=todo.rebli;
fprintf(1,'Datos cargados - %2.2f sec\n',toc)

%% remuevo las sacadas que contienen un blink
lesacblink=[];
for i=1:size(lebli,1)
    sbli=lebli(i,1);
    ebli=lebli(i,2);    
    ind=find(lesac(:,1)<sbli & lesac(:,2)>ebli  );
    lesacblink=[lesacblink ind];
end
lesac(lesacblink,:)=[];

resacblink=[];
for i=1:size(rebli,1)
    sbli=rebli(i,1);
    ebli=rebli(i,2);    
    ind=find(resac(:,1)<sbli & resac(:,2)>ebli  );
    resacblink=[resacblink ind];
end
resac(resacblink,:)=[];
fprintf(1,'Removidas %d lesac y %d resac por blink\n',length(lesacblink),length(resacblink))

%% remuevo las sacadas que estan antes del primer sample y despues del ultimo
tiempo=todo.samples(:,1);
ti=lesac(:,1);%tiempo inicial
tf=lesac(:,2);%tiempo final
lindremove=find(tf<tiempo(1) | ti>tiempo(end));
lesac(lindremove,:)=[];
ti=resac(:,1);%tiempo inicial
tf=resac(:,2);%tiempo final
rindremove=find(tf<tiempo(1) | ti>tiempo(end));
resac(rindremove,:)=[];
fprintf(1,'Removidas %d lesac y %d resac  porque estan fuera de samples\n',length(lindremove),length(rindremove))
fprintf(1,'Quedaron  %d lesac y %d resac\n',length(lesac),length(resac))

%% armo la estructura, left (solo si el ojo es left o both)

if strcmp(todo.ojo,'LEFT') | strcmp(todo.ojo,'BOTH')
    t=todo.samples(:,1);    
    x=todo.samples(:,2);
    y=todo.samples(:,3);
    v=sqrt(diff(x).^2+diff(y).^2)./diff(t);v=[v(1);v];%para que tenga la misma longitud
    temp=lesac;
    lesac=[];
    for indsac=1:size(temp,1)
        lesac(indsac).sujnum=sujnum;
        lesac(indsac).ti=temp(indsac,1);
        lesac(indsac).tf=temp(indsac,2);
        lesac(indsac).dur=temp(indsac,3);
        lesac(indsac).xi=temp(indsac,4);
        lesac(indsac).yi=temp(indsac,5);
        lesac(indsac).xf=temp(indsac,6);
        lesac(indsac).yf=temp(indsac,7);
        lesac(indsac).ampli=sqrt((lesac(indsac).xf-lesac(indsac).xi).^2+(lesac(indsac).yf-lesac(indsac).yi).^2);%amplitud 

        si=findsorted(t,lesac(indsac).ti);%sample inicial
        sf=findsorted(t,lesac(indsac).tf);%sample final
        lesac(indsac).peakvel=max(v(si:sf));
        lesac(indsac).samples=todo.samples(si:sf,:);
    end
elseif strcmp(todo.ojo,'RIGHT')
    lesac=[];
end

%% armo la estructura, right (solo si both o right)
if strcmp(todo.ojo,'LEFT')% si es izquierdo, no tengo el ojo derecho y chau
    resac=[];
elseif strcmp(todo.ojo,'BOTH') | strcmp(todo.ojo,'RIGHT')
    if strcmp(todo.ojo,'BOTH') %si es both, el dato del derecho esta en las columnas 5 y 6 
        t=todo.samples(:,1);
        x=todo.samples(:,5);
        y=todo.samples(:,6);
    elseif strcmp(todo.ojo,'RIGHT') %si es right solo, el dato del derecho esta en las columnas 2 y 3 
        t=todo.samples(:,1);
        x=todo.samples(:,2);
        y=todo.samples(:,3);
    end
    v=sqrt(diff(x).^2+diff(y).^2)./diff(t);v=[v(1);v];%para que tenga la misma longitud
    temp=resac;
    resac=[];
    for indsac=1:size(temp,1)
        resac(indsac).sujnum=sujnum;
        resac(indsac).ti=temp(indsac,1);
        resac(indsac).tf=temp(indsac,2);
        resac(indsac).dur=temp(indsac,3);
        resac(indsac).xi=temp(indsac,4);
        resac(indsac).yi=temp(indsac,5);
        resac(indsac).xf=temp(indsac,6);
        resac(indsac).yf=temp(indsac,7);
        resac(indsac).ampli=sqrt((resac(indsac).xf-resac(indsac).xi).^2+(resac(indsac).yf-resac(indsac).yi).^2);%amplitud 

        si=findsorted(t,resac(indsac).ti);%sample inicial
        sf=findsorted(t,resac(indsac).tf);%sample final
        resac(indsac).peakvel=max(v(si:sf));
        resac(indsac).samples=todo.samples(si:sf,:);
    end
end
disp('Estructuras armadas')

