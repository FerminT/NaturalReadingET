function P=seleccionatiempos2(todo, desde, hasta,M) %M= matriz tiempo trials, S=datos.


%M=todo.msgtime;
%pupilsizelimpio=remueve_blinks_y_sacadas(todo);
S=todo.samples;
if isfield(todo,'srate')
    srate=todo.srate;
else
    disp('Seleccionatiempos: Supongo que sampling rate es 1000ms')
    srate=1000;    
end
%S(:,4)=pupilsizelimpio;
datosporsample=size(S,2);


LONGITUD=round(srate/1000*(desde+hasta))+round(srate/1000);

P=nan(length(M),LONGITUD,datosporsample); %arma la matriz P (pupil size)

for i=1:length(M)
    index=find((M(i)+hasta)>=S(:,1) & S(:,1)>=(M(i)+desde)) ;
    P(i,1:length(index),:)=S(index,:);
end