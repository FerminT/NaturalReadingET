
% para poner mensajes de sincronizacion en el eyelink el comando es
% "Eyelink('Message','mensaje'); Por ejemplo dentro de un loops de trial
% apra decirle que me anote en el .edf cuando empezo un trial hay que poner
% (adentro el loop):


str=['trial(' num2str(i) ')'];
Eyelink('Message', str);