% funciones que piden data. 

type = Eyelink('GetNextDataType'); %nos dice de que tipo es la data.

item = Eyelink('GetFloatData', type); %pide la data del tipo que le pedimos.

Eyelink( 'NewFloatSampleAvailable'); % nos dice si hay un nuevo sample disponible.

Eyelink( 'NewestFloatSample'); % pide el sample mas nuevo disponible.

% Para ver que numero le corresponde a cada tipo de evento  poner en matlab
% 
%el=EyelinkInitDefaults().


