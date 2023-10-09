DEACC = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}

WORDS_MAPPING = {
    'anio': 'año',
    'anos': 'años',
    '21': 'veintiuno',
    'xxi': 'veintiuno',
    'pequenio': 'pequeño',
    'seniora': 'señora',
    'senior': 'señor',
    'seniorita': 'señorita',
    'maniana': 'mañana',
    'ojo': 'ojos',
}


def parse_cue(cue):
    cue = cue.lower()
    cue = ''.join([DEACC[char] if char in DEACC else char for char in cue])
    return cue


def parse_answer(answer):
    if type(answer) != str:
        answer = None
    else:
        answer = answer.lower()
        answer = answer.replace(';', 'ñ')
        if len(answer.split()) > 1:
            answer = answer.split()[-1]
        if answer in WORDS_MAPPING:
            answer = WORDS_MAPPING[answer]
    return answer
