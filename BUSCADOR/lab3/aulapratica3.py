import os
import shutil
import xml.etree.ElementTree as ET 
import importlib.machinery
import numpy as np
import sys
import abc
# sempre dar append ao path quando quiser importar dos scripts 
sys.path.append('C:\\Users\\Estudante\\Desktop\\mateus e Luis-Casal Unido')

#TAMANHO MINIMO PARA CONSIDERAR PALAVRA
TAM_MINIMO = 4

class Buscador:
    def __init__(self):
      pass


    def in_titulo(self, titulo: list, busca: str):
        '''
        Funcao booleana que diz se palavra buscada esta no titulo ou nao\n
        '''
        return busca in titulo

    def escrever_dados(self, lista_classe, path_out="out.txt"):
        with open(path_out, 'w') as f:
            lista_out = list()
            for elem in lista_classe:
              string = f"{elem.id} {elem.titulo} {str(elem.ocorrencias)}\n"
              lista_out.append(string)
            f.writelines(lista_out)

    def mostrar_paginas(self, dict_dados: dict, escrever=False ):
      """
      Funcao que mostra resultados de busca e opcionalmente escreve em .txt
      ----------
       Parameters
       dict_dados: `dict` dicionario contendo objetos `DadosPagina`\n
      """
      if escrever:
        self.escrever_dados(dict_dados)
        return
      
      for dado in dict_dados.values():
        aux = [dado.id, dado.titulo]
        print(aux)
      tam = len(dict_dados.values())
      print("QUANT OCORRENCIAS: ", tam)

    
    #rankeia baseado em titulo e texto
    '''def rankear_titulo_texto(self, path_data, string_busca):
      tree = ET.parse(path_data)
      root = tree.getroot()
      ocorrencias = dict()
      for page in root:
          titulo = page.find('.//title')
          id = page.find('.//id')
          texto_titulo = titulo.text
          splitado = texto_titulo.split(" ")
          
          coef_aumento = 1
          if self.in_titulo(texto_titulo, string_busca):
              # coeficiente de aumento para aumentar peso do score
              # quando palavra chave estiver no titulo
              coef_aumento = 1.1
          
          texto_pagina =  page.find('.//text').text
          splitado = texto_pagina.split(" ")
          #TOTAL relativo a texto da pagina
          cont_texto, TOTAL = self.contar_ocorrencias(splitado, string_busca)

          #pega numero de ocorencias em porcentagem
          score = round(cont_texto/TOTAL * 100 * coef_aumento, 3)
          
          dado = DadosPagina(id.text, titulo.text, score)
          print(dado.titulo+ " "+ dado.id)
          ocorrencias[id.text] = dado
      # lista com classes ordenada com base nas ocorrencias de palavra chave
      #ocorrencias = list(sorted(ocorrencias.values(), key=lambda item: item.ocorrencias, reverse=True))
      cache.inserir(string_busca, ocorrencias)
      print(ocorrencias[:20])
      return ocorrencias'''
    

    def rankear_paginas(self, string_busca, FRASE=False):
      if string_busca in cache.hash_buscas.keys():
        return cache.hash_buscas[string_busca]
      else:
         #dicionario interno: key= id_pagina; value=score da pagina
         cache.hash_buscas[string_busca] = dict()

      for id_pagina in cache.hash_indexacao.keys():
        # se string de busca nao esta nesta pagina, vai pra proxima
        pagina = cache.hash_indexacao[id_pagina]
           
        if not cache.checa_string(id_pagina, string_busca):
          print("PAGINA SEM STRING")
          continue
        
        coef_aumento = 1
        if self.in_titulo(pagina.titulo, string_busca):
            # coeficiente de aumento para aumentar peso do score
            # quando palavra chave estiver no titulo
            coef_aumento = 1.0 + 0.1

        #TOTAL relativo a texto da pagina
        # pega dicionario e total do cache
        dict_pagina, TOTAL = pagina.dict_pagina, pagina.total
        contagem_string_busca = dict_pagina[string_busca]
        
        #pega score da palavra
        score = round(contagem_string_busca/TOTAL * 100 * coef_aumento, 3)
        dict_interno = cache.hash_buscas[string_busca]
        dict_interno[id_pagina] = score

    def calcDist(self, pal1, pal2, texto):
        """
        Calcula peso  usando índices de posicao de ocorrencias das palavras.
        """
        peso = 0.0
        ocorrencias1, ocorrencias2, = [], []
        for i, string in enumerate(texto):
            if string == pal1:
               ocorrencias1.append(i)
            elif string == pal2:
               ocorrencias2.append(i)
        
        array_pal1, array_pal2 = np.array(ocorrencias1), np.array(ocorrencias2)
        #usando distancia de Manhattan 1D
        array_dif = np.abs(array_pal1 - array_pal2)
        #retorna 1/diferenca
        dist = np.sum(1 / array_dif)
        return dist

    def rankear_frase(self, frase_busca):
        frase = frase_busca.split(" ")
        palavra1, palavra2 = frase
        
        #usa metrica de ocorrencias normalmente
        #else: return 1;

        if frase_busca in cache.hash_buscas.keys():
            return cache.hash_buscas[frase_busca]
        else:
            #dicionario interno: key= id_pagina; value=score da pagina
            cache.hash_buscas[frase_busca] = dict()

        for id_pagina in cache.hash_indexacao.keys():
            # se string de busca nao esta nesta pagina, vai pra proxima
            pagina = cache.hash_indexacao[id_pagina]
            if not cache.checa_string(id_pagina, palavra1) and not cache.checa_string(id_pagina, palavra1):
                print("PAGINA SEM FRASE!!!")
                continue
            #duas strings estao no texto
            texto = pagina.texto
            if palavra1 in texto and palavra2 in texto:
                score_dist = self.calcDist(palavra1, palavra2,texto)
            else:
               score_dist = 1
            
            coef_aumento = 1
            if self.in_titulo(pagina.titulo, palavra1) or self.in_titulo(pagina.titulo, palavra2):
                # coeficiente de aumento para aumentar peso do score
                # quando palavra chave estiver no titulo
                coef_aumento = 1.0 + 0.1

            #TOTAL relativo a texto da pagina
            # pega dicionario e total do cache
            dict_pagina, TOTAL = pagina.dict_pagina, pagina.total
            contagem_string_busca = dict_pagina[frase_busca]
            
            #pega score da palavra
            score = round(contagem_string_busca/TOTAL * 100 * coef_aumento * score_dist, 3)
            dict_interno = cache.hash_buscas[frase_busca]
            dict_interno[id_pagina] = score


#classe que deve armazenar dados diversos da pagina
class DadosPagina:
    def __init__(self, id, titulo,total, texto: list, dict_ocorrencias: dict, ):
      self.id = id
      self.titulo = titulo
      self.dict_ocorrencias = dict_ocorrencias
      self.total = total
      self.texto = texto


class CacheBuscas:
    def __init__(self, path_data):
        # registra hash de indexacao da pagina
        #ou seja, hash que guarda info de cada pagina
        self.hash_indexacao = dict()
        #hash de buscas: hash invertida que guarda ocorrencias de string de busca
        #(pode ser mais de 1 palavra)
        self.hash_buscas = dict()
        self.setup_cache(path_data)

    def checa_string(self, pagina: DadosPagina, string):
       dict_pagina = pagina.dict_pagina
       lista_lower = [chave.lower() for chave in dict_pagina.keys()]
       return string.lower() in lista_lower
          

    def setup_cache(self, path_data):
      '''
      Itera sobre documento e cria uma hash geral para cada PAGINA
      com as contagens das KEYWORDS por pagina
      '''
      tree = ET.parse(path_data)
      root = tree.getroot()
      for page in root:
        #set de keywords POR PAGINA
        keywords = set()
        #key=keyword, value = contagem da keyword
        #dicionario de ocorrencias da pagina
        dict_pagina = dict()
        id = page.find('.//id').text
        titulo = page.find('.//title').text
        
        lista_texto = page.find('.//text').text.split(" ")
        # minimo 1 ja que um texto pode conter apenas keywords
        total = 1
        for string in lista_texto:
          if len(string) >= TAM_MINIMO:
            if string in keywords:
              dict_pagina[string] += 1
            else:
              keywords.add(string)
              dict_pagina[string] = 1
            total += 1
        
        self.hash_indexacao[id] = DadosPagina(id, titulo, total, lista_texto, dict_pagina)



#TODO: PRECISA CRIAR LOGICA DE HASH  PRA CONTAR TODAS OCORRENCIAS DE KEYWRODS NO TEXTO
#TODO: PRECISA CRIAR LOGICA PRA LIDAR COM MAIS DE 1 PALAVRA NA STRING

path_aula = "lab3"
path_data = "verbetesWikipedia.xml"
buscador = Buscador()
cache = CacheBuscas(path_data)

'''-------------------------MAIN-------------------------'''

##ocor = buscador.rankear_paginas(path_data, "Computer")

loop = True
while loop:
    print("\nInsira Palavra de Busca Digite 'exit' para sair: ")
    string = input(" ")
    splitado = string.split(" ")
    if "exit" in string:
        loop = False
        break
    elif len(splitado) == 1:
        buscador.rankear_paginas(string)
    elif len(splitado) == 2:
        buscador.rankear_frase(string)
    else:
       print("INPUT ERRADO! PRA NAO QUEBRAR A COISA TODA, INSIRA NO MAXIMO 2 PALAVRAS")

string = "Computer"
buscador.rankear_paginas(path_data, string)

# buscador.escrever_dados(ocor, "out.txt")
