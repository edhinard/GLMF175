#!/usr/bin/python3
# -*- coding: utf-8 -*-

#from __future__ import print_function
from sys import exit,argv

def casepos(case,sudoku):
  """Cette fonction renvoie le nombre de solutions et tous les chiffres possibles dans une case s’il y en a
  case est la position de la case testée dans le sudoku [ligne, colonne]
  """
  liste=set(sudoku[case[0]])
  liste|={sudoku[i][case[1]] for i in range(9)}
  cellule=case[0]//3,case[1]//3
  for i in range(3):
    liste|=set(sudoku[cellule[0]*3+i][cellule[1]*3:(cellule[1]+1)*3])
  possibles = list(set(range(1,10))-liste)
  return [len(possibles), possibles]

def estcontradictoire(liste):
  """Cette fonction signale si un sous-ensemble
  de la grille du sudoku contient un chiffre plus d’une fois
  auquel cas la grille contient une contradiction
  """
  chiffres=set(liste)-{0}
  for c in chiffres:
    if liste.count(c)!=1:
      return True
  return False

try:
  fichier=argv[1]
except IndexError:
  print("Usage : "+argv[0]+" fichier.txt")
  exit(0)

# Tentative d’ouverture du fichier
# Remplissage de la grille et tests de format

sudoku=[]
trous=[]

try:
  with open(fichier,"r") as f:
    for nl,ligne in enumerate(f):
      try:
        nouvelle=[int(i) for i in list(ligne.strip())]
      except ValueError:
        print("La ligne "+str(nl+1)+" contient autre chose qu’un chiffre.")
        exit(1)
      if len(nouvelle)!=9:
        print("La ligne "+str(nl+1)+" ne contient pas 9 chiffres.")
        exit(1)
      # un trou est un triplet contenant :
      #    [le nombre de possibilités, les possibilités, la case (coordonnées)]
      trous=trous+[[0,[],(nl,i)] for i in range(9) if nouvelle[i]==0]
      sudoku.append(nouvelle)
except FileNotFoundError:
  print("Fichier "+fichier+" non trouvé.")
  exit(1)
except PermissionError:
  print("Vous n’avez pas le droit de lire le fichier "+fichier+".")
  exit(1)
if nl!=8:
  print("Le jeu contient "+str(nl+1)+" lignes au lieu de 9.")
  exit(1)

# Les tests de validité de la grille avant résolution

for l in range(9):
  if estcontradictoire(sudoku[l]):
    print("La ligne "+str(l+1)+" est contradictoire.")
    exit(1)
for c in range(9):
  colonne=[sudoku[l][c] for l in range(9)]
  if estcontradictoire(colonne):
    print("La colonne "+str(c+1)+" est contradictoire.")
    exit(1)
for l in range(3):
  for c in range(3):
    cellule=[]
    for i in range(3):
      cellule=cellule+sudoku[l*3+i][c*3:(c+1)*3]
    if estcontradictoire(cellule):
      print("La cellule ("+str(l+1)+";"+str(c+1)+") est contradictoire.")
      exit(1)

# L'heuristique intervient sur le choix du trou dans le parcours de recherche.
# Au lieu de prendre le prochain trou dans un ordre prédéterminé (en parcourant lignes et colonnes)
# on propose ici d'intervenir sur le trou ayant le moins de possibilités.
# C'est la généralisation de la méthode de résolution intuitive d'un humain qui
# cherche d'abord à remplir les cases "imposées"
def heuristique(trous, sudoku):
  trous = sorted([casepos(case,sudoku) + [case] for nbsol,possibles,case in trous])
  return trous

# La résolution
trousbouches = []

while len(trous):
  trous = heuristique(trous, sudoku)
  # rappels
  #  -un trou est un triplet contenant :
  #    [le nombre de possibilités, les possibilités, la case (coordonnées)]
  #  -la liste de trous est triée par ordre croissant sur le nombre de possibilités

  # trous[0][0] est le plus petit nombre de solution parmi les trous
  # si ce nombre vaut 0 c'est qu'on est bloqué dans notre progression, il faut revenir en arrière
  # l'heuristique fait que cet état est détecté au plus vite et évite donc une descente inutile
  # plus profonde dans l'arbre
  while trous[0][0] == 0:
    # -on récupère le dernier objet trou de la liste trousbouches
    # -on replace effectivement le trou dans la grille du sudoku
    # -on replace l'objet trou en début de liste trous (cet objet trou contient toujours
    #   ses autres valeurs possibles)
    try:
      trou = trousbouches.pop()
    except IndexError:
      print("Le sudoku n’a pas de solution.")
      exit(1)      
    case = trou[2]; sudoku[case[0]][case[1]]=0
    trous.insert(0, trou)


  # à cet endroit du programme on est certain que
  # trous[0][0] (le plus petit nombre de solution parmi les trous) est non nul

  # on sort le premier objet trou de la liste trous
  trou = trous.pop(0)

  # on en récupère une valeur possible et on met l'objet à jour
  nbsol,possibles,case = trou
  possible = possibles.pop()
  nbsol -= 1
  trou = [nbsol, possibles, case]

  # on bouche le trou avec la valeur possible extraite
  trousbouches.append(trou)
  sudoku[case[0]][case[1]]=possible


# Présentation de la grille résolue

for l in sudoku:
  for c in l:
    print(c, end="")
  print()


