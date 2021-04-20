class DatabaseHelper:

    def __init__(self, mysql):
        self.mysql = mysql

    def insert(self, query, args = []):
        cur = self.mysql.connection.cursor()
        cur.execute(query,
                    args)
        self.mysql.connection.commit()
        cur.close()

    def select(self, query, args = []):
        cur = self.mysql.connection.cursor()
        cur.execute(query,
                    args)
        data = cur.fetchall()
        self.mysql.connection.commit()
        return data

    def selectOne(self, query, args = []):
        cur = self.mysql.connection.cursor()
        cur.execute(query,
                    args)
        data = cur.fetchall()
        self.mysql.connection.commit()
        return data[0]


    def delete(self, query, args = []):
        cur = self.mysql.connection.cursor()
        cur.execute(query, args)
        self.mysql.connection.commit()
        cur.close()

    def update(self, query, args = []):
        cur = self.mysql.connection.cursor()
        cur.execute(query, args)
        data = cur.fetchall()
        self.mysql.connection.commit()
        return data


