import pydot
from IPython.display import Image, display
import queue
import numpy as np

#------CLASE------
#Objeto Principal--> Representa el estado del juego 
class Node ():
  def __init__(self, state,value,operators,operator=None, parent=None,objective=None): #constructor
    #--------Atributos------
    self.state= state #estado actual del juego 
    self.value = value #identificador del nodo 
    self.children = [] #lista de hijos
    self.parent=parent
    self.operator=operator #movimiento que genero ese nodo
    self.objective=objective
    self.level=0 #profundidad
    self.operators=operators #movimientos posibles 
    self.v=0 #valor minimax

  #-------Metodo-----
  def add_child(self, value, state, operator): #Creamos un nuevo nodo hijo 
    node=type(self)(value=value, state=state, operator=operator,parent=self,operators=self.operators) #Creamos un nuevo objeto del mismo tipo que el actual y PERMITE HERENCIA
    node.level=node.parent.level+1 #calcula la profundidad del arbol
    self.children.append(node)
    return node

  def add_node_child(self, node):
    node.level=node.parent.level+1
    self.children.append(node)
    return node
  
  #-------Metodo-----
  #Devuelve todos los estados según los operadores aplicados
  def getchildrens(self): #Genera todos los posibles estados aplicando los operadores
    return [
        self.getState(i)
          if not self.repeatStatePath(self.getState(i)) #Si el estado no se ha repetido --> lo agrega 
            else None for i, op in enumerate(self.operators)] #si ya aparecio en el camino --> devuelve None

  def getState(self, index):
    pass

  def __eq__(self, other):
    return self.state == other.state

  def __lt__(self, other):
    return self.f() < other.f()

  #-------Metodo-----
  #Con este metodo sabe si ya repitio o no el estado
  def repeatStatePath(self, state):
      n=self #empieza en el nodo actual
      while n is not None and n.state!=state:
          n=n.parent
      return n is not None

  def pathObjective(self):
      n=self
      result=[]
      while n is not None:
          result.append(n)
          n=n.parent
      return result


  ### Crear método para criterio objetivo
  ### Por defecto vamos a poner que sea igual al estado objetivo, para cada caso se puede sobreescribir la función
  def isObjective(self):
    return (self.state==self.objetive.state)


#------CLASE------
#Maneja el arbol de busqueda 
class Tree ():
  def __init__(self, root ,operators):
    self.root=root
    self.operators=operators

  def printPath(self,n):
    stack=n.pathObjective()
    path=stack.copy()
    while len(stack)!=0:
        node=stack.pop()
        if node.operator is not None:
            print(f'operador:  {self.operators[node.operator]} \t estado: {node.state}')
        else:
            print(f' {node.state}')
    return path

  def reinitRoot(self):
    self.root.operator=None
    self.root.parent=None
    self.root.objective=None
    self.root.children = []
    self.root.level=0


  def miniMax(self, depth):
    self.root.v=self.miniMaxR(self.root, depth, True) #Llamamos a miniMaxR
    ## Comparar los hijos de root
    values=[c.v for c in self.root.children]
    maxvalue=max(values)
    index=values.index(maxvalue)
    return self.root.children[index]

  def miniMaxR(self, node, depth, maxPlayer):
    if depth==0 or node.isObjective(): #Si profundidad es igual a cero o estamos en el estado objetivo 
      node.v=node.heuristic()
      return node.heuristic() #Retornamos la heuristica 
    ## Generar los hijos del nodo
    children=node.getchildrens()

    ## Según el jugador que sea en el árbol
    if maxPlayer:
      value=float('-inf') #El MAX comienza en -inf
      for i,child in enumerate(children):
        if child is not None:
          newChild=type(self.root)(value=node.value+'-'+str(i),state=child,operator=i,parent=node,
                                   operators=node.operators,player=False)
          newChild=node.add_node_child(newChild)
          value=max(value,self.miniMaxR(newChild,depth-1,False))
      #node.v=value
      #return value
    else:
      value=float('inf') #Si hablamos de MIN--> Comienza en inf
      for i,child in enumerate(children):
        if child is not None:
          newChild=type(self.root)(value=node.value+'-'+str(i),state=child,operator=i,parent=node,
                                   operators=node.operators,player=True)
          newChild=node.add_node_child(newChild)
          value=min(value,self.miniMaxR(newChild,depth-1,True))
    node.v=value
    return value
  
  def miniMaxAlphaBeta(self, depth, bonus_base, bonus_factor):
    self.root.bonus_base = bonus_base
    self.root.bonus_factor = bonus_factor
    self.root.v=self.miniMaxRAlphaBeta(self.root, depth, True, float('-inf'), float('inf'))
    ## Comparar los hijos de root
    values=[c.v for c in self.root.children]
    maxvalue=max(values)
    index=values.index(maxvalue)
    return self.root.children[index]

  def miniMaxRAlphaBeta(self, node, depth, maxPlayer, alpha, beta):
    if depth==0 or node.isObjective():
      node.v=node.heuristic()
      return node.heuristic()
    ## Generar los hijos del nodo
    children=node.getchildrens()

    ## Según el jugador que sea en el árbol
    if maxPlayer:
      value=float('-inf')
      for i,child in enumerate(children):
        if child is not None:
          if beta <= alpha:
            break
          newChild=type(self.root)(value=node.value+'-'+str(i),state=child,operator=i,parent=node,
                                   operators=node.operators,player=False, bonus_base=node.bonus_base, bonus_factor = node.bonus_factor)
          newChild=node.add_node_child(newChild)
          value=max(value,self.miniMaxRAlphaBeta(newChild,depth-1,False, alpha, beta))
          alpha = max(alpha, value)

      #node.v=value
      #return value
    else:
      value=float('inf')
      for i,child in enumerate(children):
        if child is not None:
          if beta <= alpha:
            break
          newChild=type(self.root)(value=node.value+'-'+str(i),state=child,operator=i,parent=node,
                                   operators=node.operators,player=True, bonus_base=node.bonus_base, bonus_factor = node.bonus_factor)
          newChild=node.add_node_child(newChild)
          value=min(value,self.miniMaxRAlphaBeta(newChild,depth-1,True, alpha, beta))
          beta = min(beta, value)

    node.v=value
    return value


  ## Método para dibujar el árbol
  def draw(self,path):
    graph = pydot.Dot(graph_type='graph')
    nodeGraph=pydot.Node(str(self.root.state)+"-"+str(0),
                          label=str(self.root.state),shape ="circle",
                          style="filled", fillcolor="red")
    graph.add_node(nodeGraph)
    path.pop()
    return self.drawTreeRec(self.root,nodeGraph,graph,0,path.pop(),path)

  ## Método recursivo para dibujar el árbol
  def drawTreeRec(self,r,rootGraph,graph,i,topPath,path):
    if r is not None:
      children=r.children
      for j,child in enumerate(children):
        i=i+1
        color="white"
        if topPath.value==child.value:
          if len(path)>0:topPath=path.pop()
          color='red'
        c=pydot.Node(child.value,label=str(child.state)+r"\n"+r"\n"+"f="+str(child.heuristic())+r"\n"+str(child.v),
                      shape ="circle", style="filled",
                      fillcolor=color)
        graph.add_node(c)
        graph.add_edge(pydot.Edge(rootGraph, c,
                                  label=str(child.operator)+'('+str(child.cost())+')'))
        graph=self.drawTreeRec(child,c,graph,i,topPath,path)  # recursive call
      return graph
    else:
      return graph
    
    
#Clase NODE para NIM (especializa Node)
class NimNode(Node): #HERENCIA--> Hereda todo de Node
  def __init__(self, player=True,**kwargs):
    super(NimNode, self).__init__(**kwargs) #Llamamos al constructor de la clase padre
    self.player=player
    # True para max, False para Min
    if player:
      self.v=float('-inf')
    else:
      self.v=float('inf')

  #En NimNode sobreescribimos el METODO porque no se deben bloquear estados repetidos
  # Porque en Nim: Siempre disminuyen las fichas, Nunca puedes volver a un estado anterior, No hay ciclos
  def repeatStatePath(self, state):
    return False

  def cost(self):
    return self.level

  #Calculamos cuentas fichas quedan despues de quitar (juega alguien)
  def getState(self, index):
    take = self.operators[index]
    remaining = self.state - take
    if remaining >= 0:
      return remaining
    return None

  def isObjective(self):
    # The current player can take all remaining tokens and win
    return self.state <= max(self.operators)

  def heuristic(self):
    tokens = self.state

    # No tokens left
    if tokens == 0:
      return -100 if self.player else 100

    # Few tokens left
    if tokens <= max(self.operators):
      return 100 if self.player else -100

    # Intermediate position: multiples of (max+1) are losing positions
    modulo = max(self.operators) + 1  # in this case 4
    if tokens % modulo == 0:
        return -10 if self.player else 10
    else:
        return 10 if self.player else -10
