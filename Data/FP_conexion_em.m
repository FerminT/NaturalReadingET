classdef FP_conexion_em 
% mi funcion packer de conexion_em
    properties
    end
    methods(Static)
        function f=FP_conexion_em
        end
        function [FIX palabras OUT]=FIX2EM(FIX,palabras) 
            try
                %[palabras OUT]=FIX2EM(FIX,palabras) 
                % usa la estructura de fijaciones y la estructura de palabras para calcular 
                %    las medidas de em.
                % agrega esta info a la estructura de palabras. devuelve tambien el OUT como sale.


                fp=FP_conexion_em;

                %agrego WordNumberPantalla a las fijaciones y palabras
                [FIX,palabras]=fp.agrego_WNP_a_FIX_y_palabras(FIX,palabras);

                %agrego suj, porque no lo tenia
                for i=1:length(FIX)
                    FIX(i).subj=1;
                end

                %cambio nombres variables, roi por WNP, trial por pantalla.
                for indfix=1:length(FIX)
                    FIX(indfix).roi=FIX(indfix).WNP;
                    FIX(indfix).trial=FIX(indfix).pantalla;
                end

                % necesito una estructura que tenga los siguientes campos:
                %   subj: sumero de sujeto
                %   trial: numero de trial dentro del sujeto (puede ser pantalla o renglon, la unidad de lo que se presenta simultaneamente)
                %   roi: numero de palabra en la que fijo, dentro del trial 
                %   dur: duracion de la fijacion
                %   tini: tiempo inicial de la fijacion, solo para ordenar las fix por tiempo.
                %%OUT=fp.conexion_em(FIX);  
                OUT=fp.conexion_em_matlab(FIX);                 
                %OUT es un array de estructuras, una por cada palabra de cada
                %pantalla. ojo que asume que todas las pantallas tienen la
                %misma cantidad de, por lo que tiene #pantallas*max(WNP)
                %elementos. 
                %en los ultimos de cada pantalla todos estos campos tienen
                %ceros, podria eliminarlos. o los manejo de otra manera.
                %FFD	FFP	SFD	FPRT	RBRT	TFT	RPD		RRT	RRTP	RRTR	RBRC	TRC	LPRT

     
                

                indout=1;
                maxfixWNP=max([FIX.WNP]);
                for indpal=1:length(palabras)
                    
                    if palabras(indpal).WNP>maxfixWNP %si estoy en las ultimas palabras, y nunca fije en palabras de WNP tan alto
                        %necesito esto para los casos en que en todo un texto,  
                        %    un sujeto nunca fijo en la/s ultima/s palabra/s, 
                        %    entonces OUT es mas cortito. y tengo que rellenar con esto
                        palabras(indpal).em=em_vacio(palabras(indpal));
                    else                        
                        %busco el indout que le corresponde a la indpal, pues hay
                        %mas OUT que palabras, por lo que explique mas arriba
                        while 1
                            if OUT(indout).trial==palabras(indpal).pantalla && ...
                               OUT(indout).roi  ==palabras(indpal).WNP                
                                break
                            else
                                indout=indout+1;
                            end
                        end    

                        %ya se cual es el indout que le corresponde a este indpal, lo guardo
                        palabras(indpal).em=OUT(indout);
                    end
                    %fprintf('Palabra "%10s" indpal=%5d, indout=%5d agregada\n',palabras(indpal).palabra,indpal,indout);                    
                    
                end
            catch ME
                ME
                keyboard
            end
            
            
        end       
        function [FIX,palabras]=agrego_WNP_a_FIX_y_palabras(FIX,palabras)
            %inicializo con nan
            [FIX(:).WNP]=deal(nan);
            
            %para cada pantalla
            for pantalla=min([palabras.pantalla]):max([palabras.pantalla])
                
                %busco todas las palabras y fijaciones que caen en esa pantalla
                indpal=find([palabras.pantalla]==pantalla);                
                indfix=find([FIX.pantalla]==pantalla);
                
                %busco la primera palabra de esa pantalla (no puedo buscar en FIX, pues tal vez no fijaron la primera palabra de una pantalla!!)
                minWNG=min([palabras(indpal).WNG]);
                                
                
                %agrego WNP a las fijaciones
                for i=1:length(indfix)
                    FIX(indfix(i)).WNP=FIX(indfix(i)).WNG-minWNG+1; %#ok<*SAGROW>
                end
                
                %agrego WNP a las palabras
                for i=1:length(indpal)
                    palabras(indpal(i)).WNP=palabras(indpal(i)).WNG-minWNG+1; %#ok<*SAGROW>
                end                
            end
        end                     
        function OUT=conexion_em(FIX)
            % necesito una estructura que tenga los siguientes campos:
            %   subj: sumero de sujeto
            %   trial: numero de trial dentro del sujeto (puede ser pantalla en nuestro caso)
            %   roi: numero de palabra en la que fijo, dentro del trial 
            %   dur: duracion de la fijacion
            %   tini: tiempo inicial de la fijacion, solo para ordenar por tiempo.
            fprintf('Running EM connection...\n')
            delete('Rinput.csv')
            delete('Routput.csv')
            fp=FP_conexion_em;
            fp.exporto_FIX_csv(FIX);
            fp.genero_r_scriptfile;
            fp.ejecuto_rscript;
            OUT=fp.importo_R_output;
        end
        function exporto_FIX_csv(FIX)
            %C es un array de celdas, con todos los campos.
            %C2 es un array de celdas, con una celda por fila.
            
            %creo un array de celdas para exportar como csv
            C=[fieldnames(FIX)' ; squeeze(struct2cell(FIX))'];
            [nrows,ncols]= size(C); %#ok<NASGU>
            C2=[];
            %myfieldnames={'tini' 'dur' 'WNP' 'pantalla' 'subj'};
            myfieldnames={'tini' 'dur' 'roi' 'trial' 'subj'};
            for row=1:nrows
                C2{row}=''; %#ok<*AGROW>
                for indfieldname=1:length(myfieldnames)
                    col=strcmp(myfieldnames{indfieldname},fieldnames(FIX));

                    if isnumeric(C{row,col})
                        C2{row}=sprintf('%s%g,',C2{row}, C{row,col});
                    elseif ischar(C{row,col})
                        C2{row}=sprintf('%s%s,',C2{row}, C{row,col});
                    end
                end
                C2{row}=C2{row}(1:(end-1));
            end

            %exporto celldata como CSV directamente
            csvname = 'Rinput.csv';
            fid = fopen(csvname, 'w');
            for row=1:length(C2)
                fprintf(fid, '%s\n', C2{row});
            end
            fclose(fid);
            fprintf('\tFile %s saved\n',csvname)
        end
        function genero_r_scriptfile()
            C=importdata('conexion_em_template.R');
            C=strrep(C,'routputfile','"Routput.csv"');
            C=strrep(C,'rinputfile','"Rinput.csv"');
            str=['"' pwd '"'];
            str=strrep(str,'\','/');
            C=strrep(C,'datadirectory',str);

            [nrows ncols]= size(C); %#ok<NASGU>
            filename = 'conexion_em.r';
            fid = fopen(filename, 'w');
            for row=1:nrows
                fprintf(fid, '%s\n', C{row});
            end
            fprintf('\tR scriptfile %s generated\n',filename )
        end
        function ejecuto_rscript()
            %eval(['!rscript "' datadir '/probando_em.r"'])
            tic
            eval('!Rscript conexion_em.r')
            fprintf('\trscript executed, file Routput.csv created in %2.2f seg\n',toc)
        end
        function OUT=importo_R_output()
            try
                csvname='Routput.csv';
                temp=importdata(csvname);
                fieldnames=temp.textdata(1,:);
                fieldnames=strrep(fieldnames,'"','');

                OUT=[];
                for i=1:size(temp.data,1)
                    for indfield=1:2       %los primeros campos son subj y trial, factores, por lo que los guarda como texto
                       fieldname=fieldnames{indfield};
                       OUT(i).(fieldname)=str2double(temp.textdata{i+1,indfield});
                    end
                    for indfield=3:length(fieldnames) %el resto de los campos los guarda como numero
                       fieldname=fieldnames{indfield};
                       OUT(i).(fieldname)=temp.data(i,indfield-2);
                    end    
                end
                fprintf('\tFile %s loaded\n',csvname)
            catch ME
                disp(ME)
                keyboard
            end
        end
        
        function OUT=conexion_em_matlab(FIX)
            fp=FP_conexion_em;
            % FIX: a struct array with the following fields:
            %   subj: subject number
            %   trial: trial number within subject (can be our screen number)
            %   roi: word number within trial
            %   dur: fixation duration
            %   tini: initial time of fixation

            if any([FIX.roi]==0) 
                fprintf('Hay Fijaciones a ROI=0. las saco\n')
                FIX([FIX.roi]==0)=[];                
            end

            if any([FIX.roi]==-1) 
                fprintf('Hay Fijaciones a ROI=-1. las saco\n')
                FIX([FIX.roi]==-1)=[];                
            end            
            
            if ~issorted([FIX.tini]) 
                error('Initial times of fixations not sorted... please CHECK!!')
            end

            %initialize the output
            OUT=[];
            max_roi=max([FIX.roi]);%maximum number of rois in any trial

            %In order to process each single trial separately, first split by subject...
            SUBJS=unique([FIX.subj]);

            TRIALS=unique([FIX.trial]);
            TRIALS(isnan(TRIALS))=[];%saco los nan

            TRIALS=min([FIX.trial]):max([FIX.trial]);
            
            for indsuj=1:length(SUBJS)
                iSuj = SUBJS(indsuj);
                index=[FIX.subj]==SUBJS(indsuj);    
                FIXsuj=FIX(index);

%                 if length(TRIALS)~=length(min([FIXsuj.trial]):max([FIXsuj.trial]))
%                     disp('conexion_em_matlab:: Ojo, los trials no son consecutivos')
%                 end                
                
                %then split by trials
                for indtr=1:length(TRIALS)
                    iTrial = TRIALS(indtr);
                    index=[FIXsuj.trial]==TRIALS(indtr);
                    FIXsujtr=FIXsuj(index);

                    if isempty(FIXsujtr)
                        fprintf(2,'NO FIXATIONS: subj %d, trial %d\n',iSuj,iTrial)
                    end
                    
                    %then run a function for a single trial
                    OUTtemp=fp.conexion_em_matlab_one_trial(FIXsujtr,iSuj,iTrial,max_roi);                                           
                    
                    %and finally accumulate the results
                    OUT=[OUT OUTtemp];    
                end
            end
        end

        function OUT=conexion_em_matlab_one_trial(FIX,indsuj,indtr,max_roi)
            try
                %initialize the output structure
                fnames={'roi'    'FFD' ...
                    'FFP'    'SFD'    'FPRT'    'RBRT'    'TFT'    'RPD' ...
                    'CRPD'    'RRT'    'RRTP'    'RRTR'    'RBRC' ...
                    'TRC'    'LPRT' 'TRI' 'NFFP' 'NFT' 'FFLP' 'FFL'};
                OUT=struct();
                OUT.subject=indsuj;
                OUT.trial=indtr;
                OUT.response=1;
                OUT.roi=nan;
                for indfn=1:length(fnames)
                %     OUT=setfield(OUT,fnames{indfn},0);
                    OUT.(fnames{indfn})=0;
                end
                OUT.fixlist=[];
                OUT=repmat(OUT,1,max_roi);
                for indroi=1:max_roi
                    OUT(indroi).roi=indroi;
                    OUT(indroi).FFL=nan;                    
                    OUT(indroi).FFLP=nan;
                    OUT(indroi).MFL=nan;
                end


                prev_roi=0;%roi of previous fixation
                max_roi=0;%roi of furthest fixation on this trial

                %first, remove the fixations to nan.
                FIX=FIX(~isnan([FIX.roi]));

                %run the "magic", calculate the eye movement measures, based on fixations            
                for indfix=1:length(FIX)
                    curr_roi=FIX(indfix).roi;%the roi of the current fixation

                    OUT(curr_roi).fixlist=[OUT(curr_roi).fixlist indfix];

                    %FFD  # (First Fixation Duration) Duration of the first fixation on  a position iff the fixation was progressive. Zero otherwise.
                    if curr_roi>=max_roi ... % if progressive
                            && length(OUT(curr_roi).fixlist)==1 %and this is the first fixation
                        OUT(curr_roi).FFD=FIX(indfix).dur;
                    end
                    
                    %FFLP  # (First Fixation Location Progressive) Location of the first fixation on a position iff the fixation was progressive. Zero otherwise.
                    if curr_roi>=max_roi ... % if progressive
                            && length(OUT(curr_roi).fixlist)==1 %and this is the first fixation
                        OUT(curr_roi).FFLP=FIX(indfix).location;
                    end

                    %FFL  # (First Fixation Location) Location of the first fixation on a position.
                    if length(OUT(curr_roi).fixlist)==1% if this is the first fixation on this position
                        OUT(curr_roi).FFL=FIX(indfix).location;
                    end                    

                    %MFL  # (Mean Fixation Location) Mean location of all fixations on a position.
                    if length(OUT(curr_roi).fixlist)==1% if this is the first fixation on this position
                        OUT(curr_roi).MFL=FIX(indfix).location;
                    else
                        prev_average=OUT(curr_roi).MFL;
                        prev_nfixations=length(OUT(curr_roi).fixlist)-1;
                        prev_total=prev_average*prev_nfixations;
                        OUT(curr_roi).MFL=(prev_total+FIX(indfix).location)/length(OUT(curr_roi).fixlist);
                    end                    

                    
                    %SFD	 # (Single Fixation Duration) Duration of the first *single* fixation on a position, i.e. if no subsequent fixations on this position will follow. (= FFD for single fixations)
                    if curr_roi>=max_roi ... % if progressive
                            && length(OUT(curr_roi).fixlist)==1 %and this is the first fixation    
                        OUT(curr_roi).SFD=FIX(indfix).dur;
                    end        
                    if length(OUT(curr_roi).fixlist)>1% if new fixations occur on this position...
                        OUT(curr_roi).SFD=0;            
                    end

                    %FFP	 # (First Fixation Progressive) 0 if material downstream was viewed before the first fixation on this position, 1 otherwise.
                    if curr_roi>=max_roi ... % if progressive
                            && length(OUT(curr_roi).fixlist)==1 %and this is the first fixation        
                        OUT(curr_roi).FFP=1;  
                    end

                    %FPRT # (First Pass Reading Time, Gaze Duration) Sum of all     % fixations on a position before another one is fixated, i.e. all fixations prior to a left- or rightward movement.
                    if curr_roi>=max_roi ... % if progressive
                            && length(OUT(curr_roi).fixlist)==1 %and this is the first fixation        
                        OUT(curr_roi).FPRT=FIX(indfix).dur;
                    end
                    if curr_roi>=max_roi ... % if progressive
                            && length(OUT(curr_roi).fixlist)>1 %if not the first fix to this point        
                        if max(diff(OUT(curr_roi).fixlist))==1 %and all fix were successive
                            OUT(curr_roi).FPRT=OUT(curr_roi).FPRT+FIX(indfix).dur;
                        end
                    end
                    
                    %NFT	 # (Number of Fixations Total) Count of all fixations on a position.
                    OUT(curr_roi).NFT=OUT(curr_roi).NFT+1;

                    
                    %NFFP # (Number of fixations in First Pass (the ones that compose FPRT) Count of fixations on a position before another one is fixated, i.e. all fixations prior to a left- or rightward movement.
                    if curr_roi>=max_roi ... % if progressive
                            && length(OUT(curr_roi).fixlist)==1 %and this is the first fixation        
                        OUT(curr_roi).NFFP=1;
                    end
                    if curr_roi>=max_roi ... % if progressive
                            && length(OUT(curr_roi).fixlist)>1 %if not the first fix to this point        
                        if max(diff(OUT(curr_roi).fixlist))==1 %and all fix were successive
                            OUT(curr_roi).NFFP=OUT(curr_roi).NFFP+1;
                        end
                    end


                    %RBRT # (Right Bounded Reading Time) Sum of all fixations on a  position before another position to the right is fixated, i.e. all fixations prior to a rightward movement.
                    if curr_roi>=max_roi ... % if nothing to the right was fixated
                        OUT(curr_roi).RBRT=OUT(curr_roi).RBRT+FIX(indfix).dur;
                    end

                    %TFT	 # (Total Fixation Time) Sum of all fixations on a position.
                    OUT(curr_roi).TFT=OUT(curr_roi).TFT+FIX(indfix).dur;

                    %RRT	 # (Rereading Time) Sum of all fixations on a position, which took place after a fixation on that position and a subsequent fixation on another, i.e. TFT - FPRT.    
                    OUT(curr_roi).RRT=OUT(curr_roi).TFT-OUT(curr_roi).FPRT;

                    %RRTR # (ReReading Time Regressive) Sum of all fixations on a  position, which took place after a fixation on that position and a subsequent fixation to the right of it, i.e. TFT - RBRT.
                    OUT(curr_roi).RRTR=OUT(curr_roi).TFT-OUT(curr_roi).RBRT;

                    %RRTP # (ReReading Time Progressive) Sum of all fixations on a position, which took place after a fixation on that position, a subsequent fixation to the left of it, but no fixation to the right, i.e. RBRT - FPRT.    
                    OUT(curr_roi).RRTP=OUT(curr_roi).RBRT-OUT(curr_roi).FPRT;

                    %TRC	 # (Total Regression Count) Number of regressions from this position.            
                    if curr_roi<prev_roi %if it is a regression
                        OUT(prev_roi).TRC=OUT(prev_roi).TRC+1;
                    end

                    %RBRC (Right-Bounded Regression Count) Number of regressions from this position given *before* any region further to the right has been fixated.    
                    if curr_roi<prev_roi  ... %if it is a regression
                            && prev_roi>=max_roi
                        OUT(prev_roi).RBRC=OUT(prev_roi).RBRC+1;
                    end

                    %TRI	 # (Total Regressions IN) Number of regressions TO this position.            
                    if curr_roi<prev_roi %if it is a regression
                        OUT(curr_roi).TRI=OUT(curr_roi).TRI+1;
                    end    

                    %RPD	 # (Regression Path Duration, Go-Past Duration) Sum of fixations on a position n and all preceding positions starting with the first fixation on n and ending with a fixation on anything right of n.
                    if curr_roi>=max_roi ... % if progressive
                            && length(OUT(curr_roi).fixlist)==1 %if this is the first fixation        
                        OUT(curr_roi).RPD=FIX(indfix).dur;
                    end
                    if curr_roi<=max_roi ... %if regressing
                            && OUT(max_roi).RPD>0 %and first fix to max_roi was progressive
                        OUT(max_roi).RPD=OUT(max_roi).RPD+FIX(indfix).dur;
                    end

                    %CRPD # (Cumulative Regression Path Duration) Sum the RPD of the given position and the RPDs of all preceding positions.        
                    if curr_roi>=max_roi ... % if progressive
                            && length(OUT(curr_roi).fixlist)==1 %if this is the first fixation        
                        for indroi=curr_roi:length(OUT)
                            OUT(indroi).CRPD=OUT(indroi).CRPD+FIX(indfix).dur;
                        end
                    end
                    if curr_roi<=max_roi ... %if regressing
                            && OUT(max_roi).RPD>0 %and first fix to max_roi was progressive
                        for indroi=max_roi:length(OUT)
                            OUT(indroi).CRPD=OUT(indroi).CRPD+FIX(indfix).dur;
                        end
                    end    

                    prev_roi=curr_roi;
                    max_roi=max([curr_roi max_roi]);    
                end                    
                
            catch ME
                ME
                keyboard
            end
        end                    
    end
end



function em=em_vacio(palabra)
%necesito esta funcion para los casos en que en todo un texto, un sujeto nunca fijo en la/s ultima/s palabra/s, entonces OUT es mas cortito. y tengo que rellenar con esto
    em.subj=1;
    em.trial=palabra.pantalla;
    em.roi=palabra.WNP;
    em.FFD=0;
    em.FFP=0;
    em.SFD=0;
    em.FPRT=0;
    em.RBRT=0;
    em.TFT=0;
    em.RPD=0;
    em.CRPD=0;
    em.RRT=0;
    em.RRTP=0;
    em.RRTR=0;
    em.RBRC=0;
    em.TRC=0;
    em.LPRT=0;    
end


%% CODIGO DEL probando_em.r
% % % % setwd(datadirectory)
% % % % rm(list=ls()) #borro todas las variables del workspace (rm)
% % % % 
% % % % library(em)
% % % % 
% % % % d.fix <- read.csv(rinputfile) # Tiene todas, aun las palabras que no se repitieron
% % % % #summary(d.fix)
% % % % #d.fix <- d.fix[order(d.fix$suj ,d.fix$pantalla, d.fix$tini),]
% % % % d.fix <- d.fix[order(d.fix$subj ,d.fix$trial, d.fix$tini),]
% % % % 
% % % % d.fix$trial <- as.factor(d.fix$trial)
% % % % d.fix$dur <- as.integer(d.fix$dur)
% % % % d.fix$roi <- as.integer(d.fix$roi)
% % % % d.fix$subj<- as.factor(d.fix$subj)
% % % % 
% % % % #head(d.fix)
% % % % #str(d.fix)
% % % % #summary(d.fix)
% % % % 
% % % % ## remove the na values
% % % % d.fix <- subset(d.fix,subset=!is.na(roi))
% % % % 
% % % % #calculo todas las cosas
% % % % etm <- with(subset(d.fix,dur>=0 ),
% % % %             em(measures="standard", roi, dur,
% % % %                 trialId=list(subj, trial),
% % % %                 trialInfo=list(subj=subj,trial=trial)))
% % % % #summary(etm)
% % % % #head(etm,200)
% % % % 
% % % % write.csv(etm, routputfile, row.names=FALSE)
% % % % 
% % % % # When set to "standard" the following measures are computed for each region of interest (roi), for each trial:
% % % % # FFD  # (First Fixation Duration) Duration of the first fixation on a position iff the fixation was progressive. Zero otherwise.
% % % % # SFD	 # (Single Fixation Duration) Duration of the first *single* fixation on a position, i.e. if no subsequent fixations on this position will follow. (= FFD for single fixations)
% % % % # FPRT # (First Pass Reading Time, Gaze Duration) Sum of all fixations on a position before another one is fixated, i.e. all fixations prior to a left- or rightward movement.
% % % % # RBRT # (Right Bounded Reading Time) Sum of all fixations on a position before another position to the right is fixated, i.e. all fixations prior to a rightward movement.
% % % % # TFT	 # (Total Fixation Time) Sum of all fixations on a position.
% % % % # RPD	 # (Regression Path Duration, Go-Past Duration) Sum of fixations on a position n and all preceding positions starting with the first fixation on n and ending with a fixation on anything right of n.
% % % % # CRPD # (Cumulative Regression Path Duration) Sum the RPD of the given position and the RPDs of all preceding positions.
% % % % # RRT	 # (Rereading Time) Sum of all fixations on a position, which took place after a fixation on that position and a subsequent fixation on another, i.e. TFT - FPRT.
% % % % # RRTR # (ReReading Time Regressive) Sum of all fixations on a position, which took place after a fixation on that position and a subsequent fixation to the right of it, i.e. TFT - RBRT.
% % % % # RRTP # (ReReading Time Progressive) Sum of all fixations on a position, which took place after a fixation on that position, a subsequent fixation to the left of it, but no fixation to the right, i.e. RBRT - FPRT.
% % % % # FFP	 # (First Fixation Progressive) 0 if material downstream was viewed before the first fixation on this position, 1 otherwise.
% % % % # TRC	 # (Total Regression Count) Number of regressions from this position.
% % % % # RBRC # (First Pass Regression Count) Number of regressions from this position given that after the first fixation on it no positions to the right have been fixated.
% % % % # 
% % % % # When set to "CRI" the following measures are computed for each pair of position (roi) and source position (sourceRoi), for each trial:
% % % % # CFC  # (Conditional Fixation Count) Number of fixations on roi after sourceRoi has been fixated, but before any region right of sourceRoi has been fixated. Two subsequent fixations on one region (i.e. when no other region is looked at inbetween) are considered one fixation.
% % % % # CFT	 # (Conditional Fixation Time) Amount of time spent on fixating roi under the conditions described for CFC.
