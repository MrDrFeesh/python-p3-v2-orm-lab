from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.year = year
        self.summary = summary
        self.employee_id = employee_id
        self.id = id

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, {self.employee_id}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            summary TEXT,
            employee_id INTEGER
        )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute("""
            INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)
            """, (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
            print(f"Saved new review: {self}")
        else:
            self.update()
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        id, year, summary, employee_id = row
        if id in cls.all:
            review = cls.all[id]
            review.year = year
            review.summary = summary
            review.employee_id = employee_id
        else:
            review = cls(year, summary, employee_id, id)
            cls.all[id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        CURSOR.execute("""
        UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?
        """, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()
        print(f"Updated review: {self}")

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()
        del Review.all[self.id]
        self.id = None
        print(f"Deleted review: {self}")

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("Year must be an integer greater than or equal to 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Employee ID must be a positive integer.")
        # Assuming Employee class and its find_by_id method are defined elsewhere
        from lib.employee import Employee
        if not Employee.find_by_id(value):
            raise ValueError("Employee ID must correspond to a persisted Employee instance.")
        self._employee_id = value