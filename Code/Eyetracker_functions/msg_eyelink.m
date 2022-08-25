%% Mensaje al EyeLink con sincronia adecuada con el PsychToolbox


function msg_eyelink(str)

Eyelink('Message', str);
 
WaitSecs(0.01);


end