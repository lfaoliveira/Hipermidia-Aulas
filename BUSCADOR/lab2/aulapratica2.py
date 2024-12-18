import os
import shutil
import xml.etree.ElementTree as ET 
import numpy as np
import sys

# sempre dar append ao path quando quiser importar dos scripts 
sys.path.append('C:\\Users\\Estudante\\Desktop\\mateus e Luis-Casal Unido')

#TAMANHO MINIMO PARA CONSIDERAR PALAVRA
TAM_MINIMO = 4

class Buscador:
    def __init__(self):
      # key= id da pagina, value = dict de ocorrencias da pagina
      pass
      
    def contar_ocorrencias(self, lista: list, busca: str):
        """
        RETORNA NUM de ocorrencias
        
        ----------
        Parameters
        lista: `list` lista contendo palavras do texto\n
        busca: `str` contendo string a ser buscada\n
        """
        ocor, total = 0, 0
        for string in lista:
          if len(string) >= TAM_MINIMO and string.lower() == busca.lower():
            ocor+= 1
          total += 1
          
        return ocor, total


    def in_titulo(self, titulo: list, busca: str):
        '''
        Funcao booleana que diz se palavra buscada esta no titulo ou nao\n
        '''
        return busca in titulo


    def escrever_tuplas(self, dict_tuples, path_out: str):
      with open(path_out, 'w') as f:
        lista_out = list()
        for tuple in dict_tuples:
            string = str(tuple) + "\n"
            lista_out.append(string)
        f.writelines(lista_out)


    def escrever_dados(self, lista_classe, path_out: str):
        with open(path_out, 'w') as f:
          lista_out = list()
          for elem in lista_classe:
            string = str(elem.ocorrencias) + "\n"
            lista_out.append(string)
          f.writelines(lista_out)
          
    #rankeia baseado em titulo e texto
    def rankear_titulo_texto(self, path_data, string_busca):
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
          
          dado = DadosPesquisa(id.text, titulo.text, score)
          '''print(dado.titulo+ " "+ dado.id)'''
          ocorrencias[id.text] = dado
      # lista com classes ordenada com base nas ocorrencias de palavra chave
      ocorrencias = list(sorted(ocorrencias.values(), key=lambda item: item.ocorrencias, reverse=True))
      cache.inserir(string_busca, ocorrencias)
      print(ocorrencias[:20])
      return ocorrencias
    
    
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
        dict_pagina = dict()
        id = page.find('.//id').text
        #lista com todas as strings 
        
        lista_texto = page.find('.//text').text.split(" ")
        palavras_titulo = page.find('.//title').text

        for string in lista_texto:
          if string in keywords:
            dict_pagina[string] += 1
          else:
            keywords.add(string)
            dict_pagina[string] = 1
        
        self.hash_invertida[id] = dict_pagina

class DadosPesquisa:
    def __init__(self, id, titulo, ocorrencias=None):
        self.id = id
        self.titulo = titulo
        self.ocorrencias = ocorrencias

class CacheBuscas:
    def __init__(self):
        # registra dicionario de consultas
        # self.dicionario_buscas = dict()
        self.hash_invertida = dict()

    def inserir(self, string, lista_dados: list):
       self.hash_invertida[string] = lista_dados
    def get(self, str_busca) -> list:
       #retorna lista de DadosPesquisa
       return self.hash_invertida[str_busca]


cache = CacheBuscas()





'''
Código ruim de mateus
user_words_in_text = 0
total_words_in_text = 0
user_word_percentage = 0
user_defined_str = "computer"
dict_title_occur = {}
dict_data_pages = []#list of tuples in which each tuple is filled with (word percentage, title, id)


for child in root.findall('page'):
    text_words = child.find('text').text.split()
    title_words = child.find('title').text.split()
    title = child.find('title').text
    id = child.find('id').text
    for word in text_words:
        total_words_in_text += 1
        if(word.lower() == user_defined_str.lower()):
            user_words_in_text += 1
    user_word_percentage = round(user_words_in_text/total_words_in_text * 100, 3) #visualize the data better
    for word in title_words:
        if(user_defined_str.lower() == word.lower()):
            user_word_percentage = round(user_word_percentage + (0.1 * user_word_percentage), 3)
            break
    dict_data_pages.append((user_word_percentage, title, id))
    total_words_in_text = 0
    user_words_in_text = 0
def percentage_getter(tuple):
    return tuple[0]
dict_data_pages.sort(key=percentage_getter, reverse=True)'''





'''-------------------------MAIN-------------------------'''


path_aula = "lab2"
path_data = "verbetesWikipedia.xml"


'''ocor = rankear_titulo_texto(path_data, "12th")
escrever_dados(ocor, "out.txt")'''
