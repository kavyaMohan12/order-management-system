from decimal import Decimal

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models import Product

SAMPLE_PRODUCTS: list[tuple[str, str | None, Decimal, int]] = [
    ("Desk Lamp", "LED adjustable", Decimal("29.99"), 40),
    ("Notebook Set", "3-pack lined", Decimal("12.50"), 120),
    ("Wireless Mouse", "Ergonomic", Decimal("24.99"), 75),
    ("USB-C Cable", "2m braided", Decimal("14.00"), 200),
    ("Mechanical Keyboard", "Tenkeyless", Decimal("89.99"), 30),
    ("Monitor Stand", "Aluminum", Decimal("45.00"), 50),
    ("Webcam HD", "1080p", Decimal("59.99"), 35),
    ("Laptop Sleeve", "13-14 inch", Decimal("22.00"), 80),
    ("Desk Mat", "Large", Decimal("18.75"), 60),
    ("Phone Stand", "Adjustable", Decimal("9.99"), 150),
    ("HDMI Cable", "1.8m", Decimal("11.49"), 90),
    ("Bluetooth Speaker", "Portable", Decimal("49.99"), 45),
    ("Power Strip", "6 outlets", Decimal("19.99"), 70),
    ("SSD Enclosure", "NVMe USB-C", Decimal("34.50"), 25),
    ("Cable Organizer", "Silicone", Decimal("7.99"), 110),
]


def seed_if_empty() -> int:
    db = SessionLocal()
    try:
        count = db.scalar(select(func.count()).select_from(Product)) or 0
        if count > 0:
            return 0
        for name, description, price, stock in SAMPLE_PRODUCTS:
            db.add(
                Product(name=name, description=description, price=price, stock=stock)
            )
        db.commit()
        return len(SAMPLE_PRODUCTS)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    inserted = seed_if_empty()
    if inserted:
        print(f"Seeded {inserted} products.")
    else:
        print("Products already present; skipped seed.")
