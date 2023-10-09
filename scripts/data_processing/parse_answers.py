

def parse_answer(answer):
    if type(answer) != str:
        answer = None
    else:
        answer = answer.lower()
        answer = answer.replace(';', 'ñ')
    return answer