import copy

import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph = nx.Graph()
        self._costruttori = []
        self._idMapCostruttori = {}
        self._year1 = None
        self._year2 = None

        self._optListaCostruttori = None
        self._optScore = None

    def getListaCostruttoriOttima(self, k):
        self._optListaCostruttori = []
        self._optScore = 365 * 100  # 100 years in days

        # Load oldest driver DOB for each constructor
        DAO.getDataNascitaPilotaPiuAnziano(self._year1, self._year2, self._idMapCostruttori)

        components = list(nx.connected_components(self._graph))

        if k > len(components):
            return None, 0

        parziale = []
        self._ricorsione(components, k, parziale, 0)
        return self._optListaCostruttori, self._optScore

    def _ricorsione(self, componenti, k, parziale, index_componente):
        # Base case: found k constructors
        if len(parziale) == k:
            # Check if all constructors have oldest_driver_dob
            dobs = [c.oldest_driver_dob for c in parziale if c.oldest_driver_dob is not None]
            if len(dobs) != k:
                return  # Skip if some constructors don't have data

            diff_attuale = (max(dobs) - min(dobs)).days

            if diff_attuale < self._optScore:
                self._optScore = diff_attuale
                self._optListaCostruttori = copy.deepcopy(parziale)
            return

        # Termination conditions
        if index_componente >= len(componenti):
            return
        if (len(componenti) - index_componente) < (k - len(parziale)):
            return

        # Option 1: Skip this component
        self._ricorsione(componenti, k, parziale, index_componente + 1)

        # Option 2: Choose one constructor from this component
        componente_corrente = componenti[index_componente]
        for costruttore in componente_corrente:
            if costruttore.oldest_driver_dob is not None:
                parziale.append(costruttore)
                self._ricorsione(componenti, k, parziale, index_componente + 1)
                parziale.pop()

    def getYears(self):
        return DAO.getAllYears()

    def buildGraph(self, anno1, anno2):
        self._graph.clear()
        self._year1 = anno1
        self._year2 = anno2
        self._costruttori = DAO.getCostruttori(anno1, anno2)
        for c in self._costruttori:
            self._idMapCostruttori[c.constructorId] = c

        self._graph.add_nodes_from(self._costruttori)

        allEdges = DAO.getCostruttoriEdges(anno1, anno2, self._idMapCostruttori)
        for e in allEdges:
            self._graph.add_edge(e[0], e[1], weight=e[2]) #perche lavoriamo con tuple
            #self._graph.add_edge(edge.c1, edge.c2, weight=edge.weight)#SBAGLIATO


    def getGraphDetails(self):
        return len(self._graph.nodes), len(self._graph.edges)

    def getTop3Archi(self):
        #metro paris archi peso maggiore

        #vettore che posso sortare con lambda function
        return sorted(self._graph.edges(data=True), key=lambda x: x[2]["weight"], reverse=True)[:3]
    def getConnessaInfo(self):
        #1. le componenti connesse
        #lista di serie di nodi connessi tra di loro
        components = list(nx.connected_components(self._graph))
        largest = max(components, key=len) #usa la dimensione della singola componente, per decidere chi è la piu grande
        #per sapere il grado dei nodi devo lavorare sul grafo
        #prendo il sottografo
        subgraph = self._graph.subgraph(largest).copy()
        orderedNodes = sorted(subgraph.nodes(),key = lambda n: self._graph.degree(n), reverse=True)
        #ordino secondo il grado da maggiore a minore
        #faccio lista di tuple primo elm nodo, secondo il grado
        details = [(n, self._graph.degree(n)) for n in orderedNodes]
        return len(components), largest, details

#Inizializzazione (getListaCostruttoriOttima)Trova tutte le componenti connesse del grafo tramite nx.connected_components(self._graph).
# Ciascuna componente contiene un gruppo di costruttori legati tra loro dai piloti.Se il numero $K$ richiesto dall'utente è superiore al numero di componenti connesse totali disponibili,
# l'algoritmo si ferma subito perché è matematicamente impossibile scegliere $K$ costruttori da componenti distinte.
# Inizializza self._optScore a un valore molto alto (100 anni in giorni) per poter trovare il minimo.La Ricorsione (_ricorsione)L'algoritmo analizza le componenti connesse una alla volta
# (usando index_componente). Per ciascuna componente, ha due scelte:
# Opzione 1 (Salto): Non scegliere nessun costruttore da questa componente e passa alla successiva.
# Opzione 2 (Scelta): Scegliere uno dei costruttori presenti nella componente corrente (purché abbia una data di nascita valida), aggiungerlo alla lista parziale e avanzare alla componente successiva.
# Condizioni di Terminazione e Soluzione Ottima:Caso Base (Soluzione Trovata): Quando len(parziale) == k, significa che abbiamo estratto esattamente 1 costruttore da $K$ componenti diverse.
# Calcola lo scarto in giorni: (max(dobs) - min(dobs)).days.Se questo scarto è inferiore a quello memorizzato in self._optScore, aggiorna il record del punteggio ottimo e salva una copia della lista (copy.deepcopy(parziale)).
# Pruning (Taglio dei rami inutili): if (len(componenti) - index_componente) < (k - len(parziale)): return. Se le componenti rimaste da analizzare sono meno dei costruttori che mancano per raggiungere l'obiettivo $K$, è inutile continuare la ricorsione.