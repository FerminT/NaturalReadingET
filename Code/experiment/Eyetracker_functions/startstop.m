function startstop(tiempo,sujeto)

[edfFile]=eyelink_ini(sujeto);

for i=1:3
waitsecs(tiempo);
Eyelink('Stoprecording');
waitsecs(tiempo);
Eyelink('Sartrecording')
end

eyelink_end;
eyelink_receive_file(edfFile);