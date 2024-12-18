import os
import shutil
import xml.etree.ElementTree as ET 
import importlib.machinery

class CustomFinder(importlib.machinery.PathFinder):
    _path = ['C:\\Users\\Estudante\\Desktop\\mateus e Luis-Casal Unido\\']

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        return super().find_spec(fullname, cls._path, target)

import sys
sys.meta_path.append(CustomFinder)

def print_id_titulo(path_data):
    tree = ET.parse(path_data) 
    # get root element 
    # Nesse XML, root deve ser <collection>
    root = tree.getroot()

    for child in root.iter():
        
        if child.tag == "id":
            print("ID: ", child.text)
        elif child.tag == "title":
            print("TITLE: ", child.text)
    return


def printar_string_busca(path_data, string_busca):
    tree = ET.parse(path_data)
    root = tree.getroot()

    for page in root.iter():
        achou = False
        for child in page.iter():
            if child.tag == "title":
                texto_titulo = child.text
                splitado = texto_titulo.split(" ")
                
                for string in splitado:
                    if string_busca == string:
                        # print(texto_id)
                        print(texto_titulo)
                        achou = True
                        
            if achou:
                if child.tag == "id":
                    print("ID: ", child.text)
    
        
        
        
def rankear_ocorrencias(path_data, string_busca):
    tree = ET.parse(path_data)
    root = tree.getroot()
    ocorrencias = dict()
    for page in root:
        achou = False
        titulo = page.find('.//title')
        print(titulo)

        texto_titulo = titulo.text
        splitado = texto_titulo.split(" ")
        
        for string in splitado:
            if string_busca == string:
                # print(texto_id)
                print(texto_titulo)
                achou = True
                        
        if achou:
            texto_pagina =  page.find('.//text').text
            print(type(texto_pagina))
            splitado = texto_pagina.split(" ")
            cont_ocur = 0
            for string in splitado:
                if string == string_busca:
                    cont_ocur += 1
            ocorrencias[texto_titulo] = cont_ocur 
        
            #print(ocorrencias[page.find(".//title").text])
    ocorrencias = sorted(ocorrencias, key=lambda item: item[1], reverse=True)
    print(ocorrencias[:10])


def parse_xml(path_data):
    tree = ET.parse(path_data)
    # get root element 
    # Nesse XML, root deve ser <collection>
    root = tree.getroot()
    contagem = list()

    for child in root:
        if child.tag == "page":
            contagem.add(child.tag)
    quant_paginas = len(contagem)
    return quant_paginas



#--------------------------MAIN------------------------------#

path_aula1 = "lab1"
path_data = "verbetesWikipedia.xml"
a = rankear_ocorrencias(path_data, "12th")
print(a)
