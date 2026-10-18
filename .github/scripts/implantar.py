"""Aciona o Render e aguarda a versao esperada responder com saude."""

import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


def main() -> int:
    hook = os.environ.get("DEPLOY_HOOK", "")
    imagem = os.environ["IMAGEM"]
    versao = os.environ["VERSAO"]
    aplicacao = os.environ["APLICACAO"].rstrip("/")
    if not hook:
        print("Deploy hook nao configurado para este ambiente.", file=sys.stderr)
        return 1

    partes = urlsplit(hook)
    parametros = parse_qsl(partes.query, keep_blank_values=True)
    parametros.append(("imgURL", imagem))
    url = urlunsplit((partes.scheme, partes.netloc, partes.path, urlencode(parametros), partes.fragment))
    try:
        with urlopen(Request(url, method="POST"), timeout=30) as resposta:
            if resposta.status not in (200, 202):
                print("Render nao aceitou a solicitacao de deploy.", file=sys.stderr)
                return 1
            print(f"Render aceitou o deploy (HTTP {resposta.status}).")
    except (HTTPError, URLError, TimeoutError, OSError):
        print("Falha ao acionar o deploy no Render; confira o secret e o servico.", file=sys.stderr)
        return 1

    limite = time.monotonic() + 900
    while time.monotonic() < limite:
        try:
            with urlopen(f"{aplicacao}/health", timeout=30) as resposta:
                saude = json.load(resposta)
            with urlopen(f"{aplicacao}/version", timeout=30) as resposta:
                atual = json.load(resposta)
            if saude.get("status") == "ok" and atual.get("version") == versao:
                print(f"Saude e versao confirmadas: {versao}")
                return 0
        except (HTTPError, URLError, TimeoutError, OSError, ValueError):
            pass
        print("Aguardando a versao esperada ficar disponivel...")
        time.sleep(15)
    print("Tempo esgotado aguardando saude e versao esperada.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
