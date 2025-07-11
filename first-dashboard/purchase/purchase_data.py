from connect import Connect
from models.purchase_data_model import Purchase_data_model

"""TODO
- Mettre 'db' dans un singleton, ou faire un Design en Factory pour empêcher lles répétition de
db = Connect("dsn")
"""


def getPurchaseData():
    db = Connect("dsn1")

    purchase_data = Purchase_data_model()

    purchase_data.purchase_order = db.read("SELECT * FROM purchase_order")
    purchase_data.suppliers = db.read(
        "SELECT res_partner.name, res_partner.email, res_partner.website, purchase_order.write_date, purchase_order.company_id FROM res_partner JOIN purchase_order ON purchase_order.partner_id = res_partner.id"
    )

    return purchase_data
