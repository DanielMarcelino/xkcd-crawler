import os
import hashlib

arquivos = os.listdir('comics/')
lista_md5 = []
lista_md5_id = []
# print(arquivos)
for arquivo in arquivos:
    with open(f'comics/{arquivo}', 'rb') as arq_bin:
        conteudo_arq = arq_bin.read()
        md5_from_file = hashlib.md5()
        md5_from_file.update(conteudo_arq)
        md5_from_file = md5_from_file.hexdigest()
        lista_md5.append(f'{md5_from_file}.{arquivo[-3:]}')
        lista_md5_id.append([f'{md5_from_file}.{arquivo[-3:]}', f'{arquivo[:-4]}' ])

# print(len(lista_md5))
# print(lista_md5_id)

arquivos_2 = [arquivo for arquivo in os.listdir('comics_2/')]
# print(arquivos_2)
lista_repetdos = []
# print(lista_md5.difference(arquivos_2))
for arquivo in arquivos_2:
    if lista_md5.count(arquivo) > 1:
        lista_repetdos.append(arquivo)
        print(arquivo)

for repetido in lista_repetdos:
    for nome in lista_md5_id:
        if nome[0] == repetido:
            print(nome)