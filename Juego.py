import pydot
from IPython.display import Image, display
import queue
import numpy as np
class Node ():
  def __init__(self, state,value,operators,operator=None, parent=None,objective=None):
    self.state= state
    self.value = value
    self.children = []
    self.parent=parent
    self.operator=operator
    self.objective=objective
    self.level=0
    self.operators=operators
    self.v=0


  def add_child(self, value, state, operator):
    node=type(self)(value=value, state=state, operator=operator,parent=self,operators=self.operators)
    node.level=node.parent.level+1
    self.children.append(node)
    return node

  def add_node_child(self, node):
    node.level=node.parent.level+1
    self.children.append(node)
    return node

  #Devuelve todos los estados según los operadores aplicados
  def getchildrens(self):
    return [
        self.getState(i)
          if not self.repeatStatePath(self.getState(i))
            else None for i, op in enumerate(self.operators)]

  def getState(self, index):
    pass

  def __eq__(self, other):
    return self.state == other.state

  def __lt__(self, other):
    return self.f() < other.f()


  def repeatStatePath(self, state):
      n=self
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

  def heuristic(self):
    return 0


  ### Crear método para criterio objetivo
  ### Por defecto vamos a poner que sea igual al estado objetivo, para cada caso se puede sobreescribir la función
  def isObjective(self):
    return (self.state==self.objetive.state)
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


  def miniMax(self, depth, bonus_base, bonus_factor):
    self.root.bonus_base = bonus_base
    self.root.bonus_factor = bonus_factor
    self.root.v=self.miniMaxR(self.root, depth, True) #True--> Max
    # Hasta que el no termine de hacer el metodo no continua
    ## Comparar los hijos de root
    values=[c.v for c in self.root.children]
    maxvalue=max(values)
    index=values.index(maxvalue)
    return self.root.children[index]

  def miniMaxR(self, node, depth, maxPlayer):
    #Evalua profundidad
    if depth==0 or node.isObjective(): #condicion de parada
      node.v=node.heuristic() #Lo que calculo de la heuristica (numero) lo guardo en v 
      return node.heuristic()
    
    #Si no es depth=0 se generan los hijos
    ## Generar los hijos del nodo
    children=node.getchildrens()

    ## Según el jugador que sea en el árbol
    if maxPlayer: #Para MAX
      value=float('-inf')
      for i,child in enumerate(children):
        if child is not None:
          newChild=type(self.root)(value=node.value+'-'+str(i),state=child,operator=i,parent=node,
                                   operators=node.operators,player=False, bonus_base=node.bonus_base, bonus_factor = node.bonus_factor)
          newChild=node.add_node_child(newChild)
          value=max(value,self.miniMaxR(newChild,depth-1,False)) #Ya genere un hijo--> Una profundidad menos --> DEBE LLEGAR A CERO, ADEMAS PASAMOS A MIN(False)
      #node.v=value
      #return value

    else: #Para MIN
      value=float('inf')
      for i,child in enumerate(children):
        if child is not None:
          newChild=type(self.root)(value=node.value+'-'+str(i),state=child,operator=i,parent=node,
                                   operators=node.operators,player=True, bonus_base=node.bonus_base, bonus_factor = node.bonus_factor)
          newChild=node.add_node_child(newChild)
          value=min(value,self.miniMaxR(newChild,depth-1,True)) #MAX
    node.v=value #Al nodo que contenia la heuristica inicial asignele el valor que acabo de calcular
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
          if beta <= alpha: #Condicion de parada del metodo Alpha Beta ---> No genero mas hijos para ese nodo 
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
class NimNode(Node):
  def __init__(self, player=True, bonus_base = 50, bonus_factor = 5,**kwargs):
    super(NimNode, self).__init__(**kwargs)
    self.player=player
    # True para max, False para Min
    if player:
      self.v=float('-inf') #MAX
    else:
      self.v=float('inf') #MIN
    self.bonus_base = bonus_base
    self.bonus_factor = bonus_factor

  def repeatStatePath(self, state):
    return False

  def cost(self):
    return self.level

  def getState(self, index):
    take = self.operators[index]
    remaining = self.state - take
    if remaining >= 0:
      return remaining
    return None

  def isObjective(self):
    # The current player can take all remaining tokens and win
    return self.state <= max(self.operators)

  def heuristic(self, bonus_base=None, bonus_factor=None):
    bb = bonus_base if bonus_base is not None else self.bonus_base
    bf = bonus_factor if bonus_factor is not None else self.bonus_factor

    tokens = self.state
    module = max(self.operators) + 1  # in this case 4

    #tokens--> cantidad de fichas que se tienen 
    # No tokens left
    if tokens == 0:
      return -100 if self.player else 100 #Si el jugador es MAX---> TRUE devuelva 100

    # Few tokens left
    if tokens <= max(self.operators):
      # Depth penalty: winning earlier is worth more
      bonus = max(0,bb - self.level*bf) #level--> Profundidad 
      return (100 + bonus) if self.player else -(100 + bonus)

    # Intermediate position
    distance = tokens % module

    if distance == 0: #Si modulo de 4 es cero, significa que estoy en posicion perderdora
        # Losing position: the more chips left, the worse (further from recovering)
        score = -10
    else:
        # Winning position: the closer to the next multiple, the better
        score = 10

    return score if self.player else -score  #Si esta en MAX -True- (maquina) invierto el valor de Score para que termine en posicion perdedora 
initState = 13
operators = [3,2,1]
levels = {
    "Easy": {
        "depth": 1,
        "bonus_base": 10,
        "bonus_factor": 1
    },
    "Medium": {
        "depth": 3,
        "bonus_base": 30,
        "bonus_factor": 3
    },
    "Hard": {
        "depth": 8,
        "bonus_base": 50,
        "bonus_factor": 5
    },
}

class NimNodeMisere(NimNode):
    """
    Variante Misère: quien toma la última ficha PIERDE.
    La estrategia óptima es casi idéntica al Nim clásico,
    excepto al final: evitar ser quien tome el último token.
    """

    def isObjective(self):
        # El juego termina cuando quedan 0 tokens (alguien ya tomó el último)
        # O cuando el estado actual OBLIGA al jugador a tomar el último
        return self.state == 0 or self.state <= max(self.operators)

    def heuristic(self, bonus_base=None, bonus_factor=None):
        bb = bonus_base if bonus_base is not None else self.bonus_base
        bf = bonus_factor if bonus_factor is not None else self.bonus_factor

        tokens = self.state
        module = max(self.operators) + 1

        # Sin tokens: el jugador anterior tomó el último → jugador anterior PIERDE
        # → quien llega aquí GANA
        if tokens == 0:
            return 100 if self.player else -100

        # Pocos tokens: el jugador ACTUAL se ve obligado a tomar el último → PIERDE
        if tokens <= max(self.operators):
            bonus = max(0, bb - self.level * bf)
            # Invertido respecto al Nim clásico
            return -(100 + bonus) if self.player else (100 + bonus)

        # Posición intermedia — la estrategia misère difiere del clásico
        # solo cuando quedan pocos tokens; aquí es prácticamente igual
        distance = tokens % module

        if distance == 0:
            # Posición perdedora en Nim clásico → en misère también (con tokens > max)
            score = -10
        else:
            score = 10

        return score if self.player else -score
