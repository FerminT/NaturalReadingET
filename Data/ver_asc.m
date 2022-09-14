clear;
fp = FP_ETanalysis_new();

ET = fp.loadASC('ACCH/ASCII/ACCH_14');

times = ET.msgtime;
messages = ET.msg;

indicesMsgIni = cellfun(@(x) any(regexp(x,'ini')), messages);
IniTimes  = times(indicesMsgIni );

indicesMsgFin = cellfun(@(x) any(regexp(x,'fin')), messages);
FinTimes = times(indicesMsgFin );

iniMsgs   = messages(indicesMsgIni);
pantallas = cellfun(@(y) str2num(y{3}) ,cellfun(@(x) split(x,' '),iniMsgs,'UniformOutput',0));

pd = table(pantallas, IniTimes, FinTimes);
pd.longPantalla = pd.FinTimes - pd.IniTimes;

be = lower(ET.bestCal(1));
ET.befix = ET.([be,'efix']);
TodasFixIni = ET.befix(:,1);

fixPorPantalla = struct();
for i = 1:length(pantallas)
    IndFixPantalla = TodasFixIni > pd.IniTimes(i) & TodasFixIni<pd.FinTimes(i); 
    fixPantalla    = ET.befix(IndFixPantalla ,:);
    fixPorPantalla(i).numPantalla = pantallas(i);
    fixPorPantalla(i).numFixes = length(fixPantalla);
end

