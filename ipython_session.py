# coding: utf-8
def ciao(nome):
    print("Il mio nome e' ", nome)
      
ciao('Alessio')
ciao('Mario')
ciao
ciao = 3
ciao('Alessio')
def ciao(nome, cognome):
    print("Il mio nome intero  e' ", nome, ' ',  cognome)
    
      
ciao('Alessio', 'Giuliani')
ciao('Alessio')
def ciao(nome, cognome='cognome ignoto'):
    print("Il mio nome intero  e' ", nome, ' ',  cognome)
    
      
ciao('Alessio')
ciao('Alessio', 'Giuliani')
range(10)
mialista = []
mialista = list()
mialista
list(range(10))
list(range(10.0))
list(range(0.0, 10.0, 1.0))
import numpy as np
miastringa = 'hello world'
list(miastringa)
a = list(miastringa)
a[0] = 'm' 
a
str(a)
''.join(a)
help
help(list)
help(str)
ciao = (3, 5, 6)
ciao
list(ciao)
d tuple()
tuple('ciao')
for i in range(10):
    print(i)
    
for i in range(5, 10):
    print(i)
    
    
for i in range(1, 10):
    print(i)
    
    
    
a = range(1, 10)
a
a = list(range(1, 10))
a
a = list(range(5))
b = a[5:]
b
a
b = a[1:3]
b
b = a[1:4]
b
b = a[2:]
b
b = "ciao mondo"[5:]
b
b = "ciao mondo"[2:5]
b
a
a.index(2)
a = ['a', 'wwww' 4]
a = ['a', 'wwww', 4]
a.index('www')
a.index('wwww')
a.index(4)
a.index('a')
a[2]
def ciao(mialista):
    mialista[3] = 'woooow'
    
unalista = [3, 4,6, 'asldhf', 7, 1]
def unafunzione():
    unalista = list(range(23))
    print(unalista)
    
unalista
unafunzione()
unalista
def unafunzione():
    print(unalista)
    
unafunzione()
def unafunzione(ciaooo):
    print(unalista)
    print(ciaooo)
    
    
unafunzione('dsalfjs')
sum(list(range(10)))
sum([56, 11111])
def funzione(ciao):
    return ciao + 1
    
funzione(3)
d = funzione(6)
d = unafunzione('sdss')
d
d
d
d
d
d
def super_somma(lista_figa):
    somma = 0.0
    for a in lista_figa:
        somma = somma + a
    return somma
    
super_somma(list(range(60)))
super_somma([4, 5, 61])
l = [3, 1111]
super_somma(l)
def super_somma(lista_figa):
    somma = 0.0
    for a in lista_figa:
        somma += a
    return somma
    
    
def super_somma(lista_figa):
    somma = 0.0
    for a in lista_figa:
        somma += a
    return somma
    
    
    
super_somma
print(__name__)
def applica_ad_una_lista(funzione, unalista):
    return funzione(unalista)
    
def applica_ad_una_lista(una_funzione, una_lista):
    return una_funzione(una_lista)
    
    
applica_ad_una_lista(super_somma, [3, 55])
applica_ad_una_lista(print, [3, 55])
applica_ad_una_lista(str, [3, 55])
applica_ad_una_lista(sum, [3, 55])
