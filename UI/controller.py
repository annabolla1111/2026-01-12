import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    def fillDDyear(self):
        anni = self._model.getYears()
        anni.sort()
        for year in anni:
            self._view._ddAnno1.options.append(ft.dropdown.Option(year))
            self._view._ddAnno2.options.append(ft.dropdown.Option(year))
        self._view.update_page()




    def handleCreaGrafo(self,e):
        year1 = self._view._ddAnno1.value
        year2 = self._view._ddAnno2.value
        self._model.buildGraph(year1,year2,)
        nNodi, nArchi = self._model.getGraphDetails()
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Grafo creato correttamente", color="green"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di nodi: {nNodi}"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di archi: {nArchi}"))
        self._view.update_page()

    def handleDettagli(self, e):
        top3 = self._model.getTop3Archi()
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Archi di peso maggiore: "))
        for arco in top3:
            self._view.txt_result.controls.append(ft.Text(f"{arco[0]} -> {arco[1]} (peso: {arco[2]["weight"]})"))
        #2
        numero, largest, details = self._model.getConnessaInfo()
        self._view.txt_result.controls.append(ft.Text(f"Il grafo contiene {numero} componenti connesse "))
        self._view.txt_result.controls.append(ft.Text(f"La componente connessa maggiore ha dimensione pari a {len(largest)} "))
        for l in largest:
            self._view.txt_result.controls.append(ft.Text(l))
        self._view.txt_result.controls.append(ft.Text(f"Componente connessa in ordine decrescente di grado dei nodi"))
        for d in details:
            self._view.txt_result.controls.append(ft.Text(f"{d[0]} - grado: {d[1]}"))

        self._view.update_page()

    def handleCerca(self, e):
        K = self._view._txtInK.value
        if K == "":
            self._view.txt_result.controls.append(
                ft.Text(f"Inserire un valore intero per K", color="red"))
            self._view.update_page()
            return

        try:
            K = int(K)
        except ValueError:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text(f"Inserire un valore intero per K", color="red"))
            self._view.update_page()
            return

        best_path, bestscore = self._model.getListaCostruttoriOttima(K)
        if best_path is None:
            self._view.txt_result.controls.append(ft.Text(f"Non ci sono abbastanza componenti connesse distinte", color="red"))
            self._view.update_page()
            return

        self._view.txt_result.controls.append(ft.Text(f"Lista di costruttori con minor scarto di età dei veterani:", color="red"))
        for c in best_path:
            self._view.txt_result.controls.append(ft.Text(f"{c.constructorRef} ({c.name}) - Pilota più vecchio nato il: {c.oldest_driver_dob}"))

        self._view.txt_result.controls.append(ft.Text(f"Scarto di età dei veterani (in giorni): {bestscore}"))
        youngest_veteran = min(best_path, key=lambda x: x.oldest_driver_dob)
        oldest_veteran = max(best_path, key=lambda x: x.oldest_driver_dob)
        self._view.txt_result.controls.append(ft.Text(f"Costruttore con il veterano più giovane: {youngest_veteran.constructorRef} ({youngest_veteran.oldest_driver_dob})"))
        self._view.txt_result.controls.append(ft.Text(f"Costruttore con il veterano più vecchio: {oldest_veteran.constructorRef} ({oldest_veteran.oldest_driver_dob})"))
        self._view.update_page()


