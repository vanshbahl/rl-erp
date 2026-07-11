"""
Factory helpers for creating domain objects directly in the test database.

Rules:
- Every factory accepts a `db` session and returns the persisted ORM instance.
- Factories call db.flush() (not db.commit()) so they work inside the
  rolled-back transaction managed by the `db` fixture.
- All fields have sensible defaults so callers only specify what matters
  for the test.
"""

from datetime import datetime, timedelta
from app.core.security import hash_password
from app.models.user import User
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.bom import BOM
from app.models.bom_item import BOMItem
from app.models.production_order import ProductionOrder
from app.models.production_order_item import ProductionOrderItem


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def make_user(db, *, username="user", email=None, role="staff", password="pass"):
    email = email or f"{username}@test.com"
    obj = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(obj)
    db.flush()
    return obj


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

def make_customer(db, *, company_name="Test Customer", email="customer@test.com",
                  phone="9999999999", is_active=True):
    obj = Customer(
        company_name=company_name,
        email=email,
        phone=phone,
        is_active=is_active,
    )
    db.add(obj)
    db.flush()
    return obj


# ---------------------------------------------------------------------------
# Suppliers
# ---------------------------------------------------------------------------

def make_supplier(db, *, company_name="Test Supplier", contact_person="Contact",
                  phone="8888888888", email="supplier@test.com",
                  is_active=True):
    obj = Supplier(
        company_name=company_name,
        contact_person=contact_person,
        phone=phone,
        email=email,
        is_active=is_active,
    )
    db.add(obj)
    db.flush()
    return obj


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

def make_product(db, *, sku=None, name="Test Product",
                 product_type="FINISHED_GOOD", is_active=True, _counter=[0]):
    _counter[0] += 1
    sku = sku or f"SKU-{_counter[0]:04d}"
    obj = Product(
        sku=sku,
        name=name,
        product_type=product_type,
        is_active=is_active,
    )
    db.add(obj)
    db.flush()
    return obj


def make_raw_material(db, **kwargs):
    return make_product(db, product_type="RAW_MATERIAL", **kwargs)


def make_finished_good(db, **kwargs):
    return make_product(db, product_type="FINISHED_GOOD", **kwargs)


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

def make_inventory(db, *, product_id, quantity=100.0, minimum_stock=10.0):
    obj = Inventory(
        product_id=product_id,
        quantity=quantity,
        minimum_stock=minimum_stock,
    )
    db.add(obj)
    db.flush()
    return obj


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def make_order(db, *, customer_id, contact_person="Test", status="PENDING",
               total_amount=0.0, po_number=None):
    obj = Order(
        customer_id=customer_id,
        contact_person=contact_person,
        po_number=po_number,
        status=status,
        total_amount=total_amount,
    )
    db.add(obj)
    db.flush()
    return obj


def make_order_item(db, *, order_id, product_id, quantity=10.0, rate=100.0):
    amount = quantity * rate
    obj = OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        rate=rate,
        amount=amount,
    )
    db.add(obj)
    db.flush()
    return obj


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

def make_invoice(db, *, order_id, customer_id, total_amount=1000.0,
                 status="DRAFT", due_days=30, invoice_number=None,
                 _counter=[0]):
    _counter[0] += 1
    invoice_number = invoice_number or f"INV-{_counter[0]:06d}"
    obj = Invoice(
        invoice_number=invoice_number,
        order_id=order_id,
        customer_id=customer_id,
        subtotal=total_amount,
        tax_amount=0.0,
        total_amount=total_amount,
        status=status,
        due_date=datetime.utcnow() + timedelta(days=due_days),
    )
    db.add(obj)
    db.flush()
    return obj


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

def make_payment(db, *, invoice_id, amount=500.0, payment_method="BANK_TRANSFER",
                 reference_number=None):
    obj = Payment(
        invoice_id=invoice_id,
        amount=amount,
        payment_method=payment_method,
        reference_number=reference_number,
    )
    db.add(obj)
    db.flush()
    return obj


# ---------------------------------------------------------------------------
# Purchase Orders
# ---------------------------------------------------------------------------

def make_purchase_order(db, *, supplier_id, status="DRAFT",
                        total_amount=0.0, po_number=None, _counter=[0]):
    _counter[0] += 1
    po_number = po_number or f"PO-{_counter[0]:06d}"
    obj = PurchaseOrder(
        supplier_id=supplier_id,
        po_number=po_number,
        status=status,
        total_amount=total_amount,
    )
    db.add(obj)
    db.flush()
    return obj


def make_purchase_order_item(db, *, purchase_order_id, product_id,
                              quantity=50.0, rate=20.0, received_quantity=0.0):
    amount = quantity * rate
    obj = PurchaseOrderItem(
        purchase_order_id=purchase_order_id,
        product_id=product_id,
        quantity=quantity,
        rate=rate,
        amount=amount,
        received_quantity=received_quantity,
    )
    db.add(obj)
    db.flush()
    return obj


# ---------------------------------------------------------------------------
# BOMs
# ---------------------------------------------------------------------------

def make_bom(db, *, product_id, version=1, is_active=True, notes=None):
    obj = BOM(
        product_id=product_id,
        version=version,
        is_active=is_active,
        notes=notes,
    )
    db.add(obj)
    db.flush()
    return obj


def make_bom_item(db, *, bom_id, component_product_id, quantity=2.0,
                  unit_of_measure="KG"):
    obj = BOMItem(
        bom_id=bom_id,
        component_product_id=component_product_id,
        quantity=quantity,
        unit_of_measure=unit_of_measure,
    )
    db.add(obj)
    db.flush()
    return obj


# ---------------------------------------------------------------------------
# Production Orders
# ---------------------------------------------------------------------------

def make_production_order(db, *, product_id, bom_id, bom_version=1,
                           quantity_planned=10.0, status="DRAFT", notes=None):
    obj = ProductionOrder(
        product_id=product_id,
        bom_id=bom_id,
        bom_version=bom_version,
        quantity_planned=quantity_planned,
        status=status,
        notes=notes,
    )
    db.add(obj)
    db.flush()
    return obj


def make_production_order_item(db, *, production_order_id,
                                component_product_id, quantity_required=20.0,
                                unit_of_measure="KG"):
    obj = ProductionOrderItem(
        production_order_id=production_order_id,
        component_product_id=component_product_id,
        quantity_required=quantity_required,
        unit_of_measure=unit_of_measure,
    )
    db.add(obj)
    db.flush()
    return obj
