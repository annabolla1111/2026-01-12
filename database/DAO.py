from database.DB_connect import DBConnect
from model.Constructor import Constructor


class DAO():

    @staticmethod
    def getAllYears():
        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = "SELECT distinct year FROM seasons s  ORDER BY year"

        cursor.execute(query)

        for row in cursor:
            results.append(row["year"])

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getCostruttori(anno1, anno2):
        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """select distinct c.constructorId, c.constructorRef, c.name, c.nationality
from constructors c, results r, races ra
where c.constructorId = r.constructorId 
and r.raceId = ra.raceId 
and r.`position` is not null 
and ra.`year` between %s and %s
        """

        cursor.execute(query, (anno1, anno2))

        for row in cursor:
            results.append(Constructor(**row))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getCostruttoriEdges(anno1, anno2, idMap):
            conn = DBConnect.get_connection()

            results = []

            cursor = conn.cursor(dictionary=True)
            query = """select re1.constructorId as c1, re2.constructorId as c2, count(distinct(re1.driverId)) as peso
from results re1, results re2, races ra1, races ra2
where re1.raceId = ra1.raceId
and re2.raceId = ra2.raceId 
and ra1.`year` between %s and %s
and ra2.`year` between %s and %s
and re1.driverId = re2.driverId 
and re1.constructorId < re2.constructorId
and re1.position is not null 
and re2.position is not null
group by re1.constructorId, re2.constructorId
order by peso desc"""

            cursor.execute(query, (anno1, anno2, anno1, anno2))

            for row in cursor:
                results.append((idMap[row["c1"]], idMap[row["c2"]], row["peso"]))

            cursor.close()
            conn.close()
            return results

    @staticmethod
    def getDataNascitaPilotaPiuAnziano(year1, year2, idMap):
        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """select re.constructorId, min(d.dob)as oldest_driver_dob
from drivers d, races ra, results re
where d.driverId = re.driverId 
and ra.raceId = re.raceId 
and ra.`year` between %s and %s
and re.`position` is not null 
group by re.constructorId 
        """

        cursor.execute(query, (year1, year2))

        for row in cursor:
            if row["constructorId"] in idMap:
                idMap[row["constructorId"]].oldest_driver_dob = row["oldest_driver_dob"]
#Usando la idMap (la mappa che associa l'ID del costruttore all'oggetto Constructor reale),
        # vai a scrivere la data direttamente dentro l'oggetto specifico: idMap[row["constructorId"]].oldest_driver_dob = ....
        # In questo modo, l'informazione biologica del "veterano" rimane incollata al rispettivo team.
        cursor.close()
        conn.close()
        return results

