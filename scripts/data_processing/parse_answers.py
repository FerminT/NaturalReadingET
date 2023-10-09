WORDS_MAPPING = {
    'anio': 'año',
    'anos': 'años',
    '21': 'veintiuno',
    'xxi': 'veintiuno',
    'pequenio': 'pequeño',
    'seniora': 'señora',
    'senior': 'señor',
    'seniorita': 'señorita',
    'maniana': 'mañana'
}


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
