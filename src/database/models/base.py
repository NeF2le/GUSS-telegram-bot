from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    repr_cols_num = 10
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for i, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or i < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {','.join(cols)}>"
