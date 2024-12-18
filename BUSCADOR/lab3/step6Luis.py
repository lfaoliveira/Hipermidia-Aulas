# Import the xml data that will be analised
""""""
# tam minimo pra considerar palavara
TAM_MINIMO = 4
import xml.etree.ElementTree as ET
import numpy as np
import os


class DadosPagina:
    def __init__(self, id, titulo, total, texto: list, dict_pagina: dict):
        self.id = id
        self.titulo = titulo
        self.dict_pagina = dict_pagina
        self.total = total
        self.texto = texto


class DadosBusca:
    def __init__(self, str_busca: str, lista_res: list):
        """
        str_busca: `str`
        dict_paginas: `list`, value=score da pagina
        """
        self.str_busca = str_busca
        self.lista_res = lista_res


class CacheBuscas:
    def __init__(self, path_data):
        # registra hash de indexacao da pagina
        # ou seja, hash que guarda info de cada pagina
        self.hash_indexacao = dict()
        # hash de buscas: hash invertida que guarda ocorrencias de string de busca
        # key = string de busca, value=DadosBusca
        # (pode ser mais de 1 palavra)
        self.hash_buscas = dict()
        self.setup_cache(path_data)

    def in_titulo(self, titulo: list, busca: str):
        """
        Funcao booleana que diz se palavra buscada esta no titulo ou nao\n
        """
        return busca in titulo

    # OK
    def checa_string(self, pagina: DadosPagina, string):
        dict_pagina = pagina.dict_pagina
        for chave in dict_pagina.keys():
            if chave.lower() == string.lower():
                return True
        return False

    # OK
    def setup_cache(self, path_data):
        """
        Itera sobre documento e cria uma hash geral para cada PAGINA
        com as contagens das KEYWORDS por pagina
        """
        tree = ET.parse(path_data)
        root = tree.getroot()
        for page in root:
            # set de keywords POR PAGINA
            keywords = set()
            # key=keyword, value = contagem da keyword
            # dicionario de ocorrencias da pagina
            dict_pagina = dict()
            id = page.find(".//id").text
            titulo = page.find(".//title").text

            lista_texto = page.find(".//text").text.split(" ")
            # minimo 1 ja que um texto pode conter apenas keywords
            total = 1
            for string in lista_texto:
                string = string.lower()
                if len(string) >= TAM_MINIMO:
                    if string in keywords:
                        dict_pagina[string] += 1
                    else:
                        keywords.add(string)
                        dict_pagina[string] = 1
                    total += 1

            self.hash_indexacao[id] = DadosPagina(
                id, titulo, total, lista_texto, dict_pagina
            )


path_data = "verbetesWikipedia.xml"
cache = CacheBuscas(path_data)


def rankear_paginas(string_busca):
    string_busca = string.lower()
    if string_busca in cache.hash_buscas.keys():
        return cache.hash_buscas[string_busca]
    else:
        # dicionario interno: key= id_pagina; value=score da pagina
        cache.hash_buscas[string_busca] = dict()

    lista_paginas_classe = list()
    dict_paginas_com_str = dict()

    for id_pagina in cache.hash_indexacao.keys():
        # se string de busca nao esta nesta pagina, vai pra proxima
        pagina = cache.hash_indexacao[id_pagina]

        if not cache.checa_string(pagina, string_busca):
            # print("PAGINA SEM STRING")
            continue
        else:
            lista_paginas_classe.append(id_pagina)
            # print("ACHOU STRING")

        coef_aumento = 1
        if cache.in_titulo(pagina.titulo, string_busca):
            # coeficiente de aumento para aumentar peso do score
            # quando palavra chave estiver no titulo
            coef_aumento = 1.0 + 0.1

        # TOTAL relativo a texto da pagina
        # pega dicionario e total do cache
        dict_pagina, TOTAL = pagina.dict_pagina, pagina.total
        contagem_string_busca = dict_pagina[string_busca]

        # pega score da palavra
        score = round(contagem_string_busca / TOTAL * 100 * coef_aumento, 3)
        dict_paginas_com_str[id_pagina] = score

    aux = list()
    for id in lista_paginas_classe:
        aux.append(cache.hash_indexacao[id])
    lista_paginas_classe = sorted(aux, key=lambda x: dict_paginas_com_str[x.id])

    lista_res = list()
    for pagina in lista_paginas_classe:
        str_res = f"ID: {pagina.id}, TITULO: {pagina.titulo}, SCORE: {dict_paginas_com_str[pagina.id]}\n"
        lista_res.append(str_res)

    cache.hash_buscas[string_busca] = DadosBusca(string_busca, lista_res)
    with open("out.txt", "a") as f:
        f.write(f"STR DE BUSCA: {string_busca}\n\n")
        f.writelines(lista_res)


def rankear_frase(frase_busca):
    frase = frase_busca.split(" ")
    frase = [elem.lower() for elem in frase]

    if frase_busca in cache.hash_buscas.keys():
        return cache.hash_buscas[frase_busca]
    else:
        # dicionario interno: key= id_pagina; value=score da pagina
        cache.hash_buscas[frase_busca] = dict()

    lista_paginas_classe = list()
    dict_paginas_com_str = dict()

    for id_pagina in cache.hash_indexacao.keys():
        frase_copia = frase.copy()
        palavra1, palavra2 = frase_copia
        pagina = cache.hash_indexacao[id_pagina]
        for palavra in frase_copia:
            # string fora da pagina
            if not cache.checa_string(pagina, palavra):
                frase_copia[frase_copia.index(palavra)] = None

        # se nenhuma string de busca nao esta nesta pagina, vai pra proxima
        if all(palavra is None for palavra in frase_copia):
            continue
        else:
            lista_paginas_classe.append(id_pagina)
        # no maximo 1 none na frase_copia
        if None in frase_copia:
            frase_copia.remove(None)

        # duas strings estao no texto

        coef_aumento = 1
        if any(cache.in_titulo(pagina.titulo, palavra) for palavra in frase_copia):
            # coeficiente de aumento para aumentar peso do score
            # quando palavra chave estiver no titulo
            coef_aumento = 1.0 + 0.1

        # TOTAL relativo a texto da pagina
        # pega dicionario e total do cache
        dict_pagina, TOTAL = pagina.dict_pagina, pagina.total
        print(frase_copia)
        contagem_string_busca = [dict_pagina[palavra] for palavra in frase_copia]
        contagem_string_busca = sum(contagem_string_busca)
        # pega score da palavra
        score = round(contagem_string_busca / TOTAL * 100 * coef_aumento, 3)
        dict_paginas_com_str[id_pagina] = score

    aux = list()
    for id in lista_paginas_classe:
        aux.append(cache.hash_indexacao[id])
    lista_paginas_classe = sorted(
        aux, key=lambda x: dict_paginas_com_str[x.id], reverse=True
    )

    lista_res = list()
    for pagina in lista_paginas_classe:
        str_res = f"ID: {pagina.id}, TITULO: {pagina.titulo}, SCORE: {dict_paginas_com_str[pagina.id]}\n"
        print(str_res)
        lista_res.append(str_res)

    cache.hash_buscas[frase_busca] = DadosBusca(frase_busca, lista_res)
    with open("out.txt", "w") as f:
        f.write(f"STR DE BUSCA: {frase_busca}\n\n")
        f.writelines(lista_res)


"""def escrever_dados(self, lista_classe, path_out="out.txt"):
    with open(path_out, "w") as f:
        lista_out = list()
        for elem in lista_classe:
            string = f"{elem.id} {elem.titulo} {str(elem.ocorrencias)}\n"
            lista_out.append(string)
        f.writelines(lista_out)"""


print("\n                        sixth step".upper())

loop = True
while loop:
    print("\nInsira Palavra de Busca Digite 'exit' para sair: ")
    string = input(" ")
    splitado = string.split(" ")
    if "exit" in string:
        loop = False
        break
    elif len(splitado) == 1:
        rankear_paginas(string)
    elif len(splitado) == 2:
        rankear_frase(string)
    else:
        print("INPUT ERRADO! PRA NAO QUEBRAR A COISA TODA, INSIRA NO MAXIMO 2 PALAVRAS")

# string = "Computer"
# rankear_paginas(path_data, string)
