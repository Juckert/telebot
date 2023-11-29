import g4f

def gpt3(prompt:str):
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        result = ''
        for message in response:
            result += message
        return result
    
    except RuntimeError:
        return 'Сервер не отвечает'


def gpt4(prompt:str):
    try:
        response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4,
        messages=[{"role": "user", "content": prompt}],
        )

        return response

    except RuntimeError:
        return 'Сервер не отвечает'