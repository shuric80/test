import collections
import re
import string
from typing import List

import click
import requests
from stop_words import get_stop_words


RUSSIAN_ALPHABET = [chr(letter) for letter in range(1072, 1104)]
stop_words = get_stop_words('russian')


def clear_text(html: str) -> str:
    expression = re.compile('<.*?>')
    text = re.sub(expression, '', html)
    return text


def processing(text: str) -> List[str]:
    for letter in string.punctuation:
        text = text.replace(letter, ' ')

    text = text.lower()
    words = [word for word in text.split(' ') if word not in '']

    words = [word for word in words if word[0] in RUSSIAN_ALPHABET]
    words = [word for word in words if word not in stop_words]

    return words


@click.command()
@click.option('--uri', default='http://az.lib.ru/t/tolstoj_lew_nikolaewich/text_0073.shtml', help='URL page')
@click.option('--n', default=10, help='show most commonly words.')
def main(uri: str, n: int):
    response = requests.get(uri, stream=True)
    assert response.status_code == 200

    buffer = collections.Counter()
    prev = ''

    for chunk in response.iter_lines(chunk_size=1024, decode_unicode=True):

        if not chunk.endswith('>'):
            ret = chunk.rsplit('>', 1)
            if len(ret) == 2:
                text, rest = ret
                text = ''.join((prev, text))
                prev = rest
            else:
                text = ret[0]
        else:
            text = ''.join((prev, chunk))
            prev = ''

        text = clear_text(text)
        text = processing(text)

        for word in text:
            buffer[word] += 1

    print(buffer.most_common(n))

          
if __name__ == '__main__':
    main()
