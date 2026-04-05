from typing import Optional
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

DB_STRING_LENGTH = 255
RGB_COLOR_LENGTH = 7


class Base(DeclarativeBase):
    pass


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(DB_STRING_LENGTH))
    raw_text: Mapped[str] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(server_default=func.now())

    sentences: Mapped[list["Sentence"]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan",
        order_by="Sentence.position",
    )

    def __repr__(self) -> str:
        return f"Contract(id={self.id!r}, filename={self.filename!r})"


class Sentence(Base):
    __tablename__ = "sentences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column()
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id"))
    label_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("clauses.id", ondelete="SET NULL"))

    contract: Mapped["Contract"] = relationship(back_populates="sentences")
    label: Mapped[Optional["Clause"]] = relationship(back_populates="sentences")

    @property
    def label_name(self) -> Optional[str]:
        return self.label.name if self.label else None

    @property
    def label_color(self) -> Optional[str]:
        return self.label.color if self.label else None

    def __repr__(self) -> str:
        return f"Sentence(id={self.id!r}, pos={self.position}, contract_id={self.contract_id})"


class Clause(Base):
    __tablename__ = "clauses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(DB_STRING_LENGTH))
    description: Mapped[Optional[str]] = mapped_column(String(DB_STRING_LENGTH))
    color: Mapped[Optional[str]] = mapped_column(String(RGB_COLOR_LENGTH))

    sentences: Mapped[list["Sentence"]] = relationship(back_populates="label")

    def __repr__(self) -> str:
        return f"Clause(id={self.id!r}, name={self.name!r}, color={self.color!r})"
