%disp('usar uigetfile y que esto sea una funcion con DESDE y HASTA seteables, y trialnum con slider')
format compact
try
    figure(65432);
    if ~exist('boton_trial_sig','var') | ~ishandle(boton_trial_sig)
        tiempo=todo.samples(:,1);
        posx=todo.samples(:,2);
        posy=todo.samples(:,3);
        pupilsize=todo.samples(:,4);
        sacadas=todo.lesac;
        blinks=todo.lebli;
%        sacadas=todo.resac;
%        blinks=todo.rebli;
        msgtime=todo.msgtime;
        msg=todo.msg;
        trial=2;
        DESDE=-2000;
        HASTA=4000;
        cmd='set(uitrial,''string'',trial-1);visualiza_trial_a_trial;';boton_trial_sig=uicontrol('string','<<<','position',[10 10 30 30],'callback',cmd);
        cmd='set(uitrial,''string'',trial+1);visualiza_trial_a_trial;';boton_trial_pre=uicontrol('string','>>>','position',[40 10 30 30],'callback',cmd);
        uicontrol('style','text','string','trial:','position',[10 40 30 30]);
        uitrial=uicontrol('style','edit','string',trial,'position',[40 40 40 30],'callback','visualiza_trial_a_trial;');
        uicontrol('style','text','string','DESDE:','position',[10 70 30 30]);
        uidesde=uicontrol('style','edit','string',DESDE,'position',[40 70 40 30],'callback','visualiza_trial_a_trial;');
        uicontrol('style','text','string','HASTA:','position',[10 100 30 30]);
        uihasta=uicontrol('style','edit','string',HASTA,'position',[40 100 40 30],'callback','visualiza_trial_a_trial;');
        disp('Ventana y botones creados')
    end
    trial=str2num(get(uitrial,'string'));
    DESDE=str2num(get(uidesde,'string'));
    HASTA=str2num(get(uihasta,'string'));
    %actualiza_pantalla
    % ejecuta el script al apretar los botoncitos y actualiza la pantalla de
    % tamañopupila posx y posy
    rango=[find(tiempo>todo.msgtime(trial)+DESDE,1) find(tiempo>todo.msgtime(trial)+HASTA,1)];

    %fprintf(1,'%d-',trial)
    if length(rango)<2
        disp(['Tiempo fuera de rango, muy cerca del ppio o del final del archivo: ' num2str(todo.msgtime(trial))])
        errorrrr
    end
    
    
    
    
    
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subplot(3,1,1)%subplot TAMPULILA
    plot(tiempo(min(rango):max(rango)),pupilsize(min(rango):max(rango)));
    xlim(tiempo(rango))
    ylim([000 4000])
    title(['Tampupila trial: ' num2str(trial)] )
    %xlim(rango+min(tiempo));%ylim([-1.2 1.2])
    desde=min(xlim);
    hasta=max(xlim);
    sacdesde=find(sacadas(:,1)>desde,1);
    sachasta=find(sacadas(:,1)>hasta,1);
    color='g';
    for i=sacdesde:sachasta
        line([sacadas(i,1) sacadas(i,1)],ylim,'color',color)
        line([sacadas(i,2) sacadas(i,2)],ylim,'color',color)    
        line([sacadas(i,1) sacadas(i,2)],ylim,'color',color)        
        line([sacadas(i,2) sacadas(i,1)],ylim,'color',color)            
    end
    blidesde=find(blinks(:,1)>desde,1);
    blihasta=find(blinks(:,1)>hasta,1);
    color='r';
    for i=blidesde:blihasta
        line([blinks(i,1) blinks(i,1)],ylim,'color',color)
        line([blinks(i,2) blinks(i,2)],ylim,'color',color)    
        line([blinks(i,1) blinks(i,2)],ylim,'color',color)        
        line([blinks(i,2) blinks(i,1)],ylim,'color',color)            
    end
    msgdesde=find(msgtime>desde,1);
    msghasta=find(msgtime>hasta,1);
    color='k';
    for i=msgdesde:msghasta
        line([msgtime(i) msgtime(i)],ylim,'color',color)
        text(msgtime(i),max(ylim),msg(i))
    end    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subplot(3,1,2)%subplot POSX
    plot(tiempo(min(rango):max(rango)),posx(min(rango):max(rango)));
    xlim(tiempo(rango))
    ylim([1 1024])
    title(['PosX  trial: ' num2str(trial)] )
    %xlim(rango+min(tiempo));%ylim([-1.2 1.2])
    desde=min(xlim);
    hasta=max(xlim);
    sacdesde=find(sacadas(:,1)>desde,1);
    sachasta=find(sacadas(:,1)>hasta,1);
    color='g';
    for i=sacdesde:sachasta
        line([sacadas(i,1) sacadas(i,1)],ylim,'color',color)
        line([sacadas(i,2) sacadas(i,2)],ylim,'color',color)    
        line([sacadas(i,1) sacadas(i,2)],ylim,'color',color)        
        line([sacadas(i,2) sacadas(i,1)],ylim,'color',color)            
    end
    blidesde=find(blinks(:,1)>desde,1);
    blihasta=find(blinks(:,1)>hasta,1);
    color='r';
    for i=blidesde:blihasta
        line([blinks(i,1) blinks(i,1)],ylim,'color',color)
        line([blinks(i,2) blinks(i,2)],ylim,'color',color)    
        line([blinks(i,1) blinks(i,2)],ylim,'color',color)        
        line([blinks(i,2) blinks(i,1)],ylim,'color',color)            
    end
    msgdesde=find(msgtime>desde,1);
    msghasta=find(msgtime>hasta,1);
    color='k';
    for i=msgdesde:msghasta
        line([msgtime(i) msgtime(i)],ylim,'color',color)
    end        
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subplot(3,1,3)%subplot POSY
    plot(tiempo(min(rango):max(rango)),posy(min(rango):max(rango)));
    xlim(tiempo(rango))
    ylim([1 768])
    title(['PosY trial: ' num2str(trial)])
    %xlim(rango+min(tiempo));%ylim([-1.2 1.2])
    desde=min(xlim);
    hasta=max(xlim);
    sacdesde=find(sacadas(:,1)>desde,1);
    sachasta=find(sacadas(:,1)>hasta,1);
    color='g';
    for i=sacdesde:sachasta
        line([sacadas(i,1) sacadas(i,1)],ylim,'color',color)
        line([sacadas(i,2) sacadas(i,2)],ylim,'color',color)    
        line([sacadas(i,1) sacadas(i,2)],ylim,'color',color)        
        line([sacadas(i,2) sacadas(i,1)],ylim,'color',color)            
    end
    blidesde=find(blinks(:,1)>desde,1);
    blihasta=find(blinks(:,1)>hasta,1);
    color='r';
    for i=blidesde:blihasta
        line([blinks(i,1) blinks(i,1)],ylim,'color',color)
        line([blinks(i,2) blinks(i,2)],ylim,'color',color)    
        line([blinks(i,1) blinks(i,2)],ylim,'color',color)        
        line([blinks(i,2) blinks(i,1)],ylim,'color',color)            
    end
    msgdesde=find(msgtime>desde,1);
    msghasta=find(msgtime>hasta,1);
    color='k';
    for i=msgdesde:msghasta
        line([msgtime(i) msgtime(i)],ylim,'color',color)
    end        
catch 
    a=lasterror
    a.message
    a.stack
    disp('visualiza_trial_a_trial: error')
end
