
from shiny import ui, render, reactive, module
from purchase.purchase_data import getPurchaseData
from shared import getSharedData
from datetime import datetime

import polars as pl

# TODO
## Rendre l'affichage du temps de retard plus beau


shared_data = getSharedData()

@module.ui
def suppliers_stats_page():
    return ui.page_sidebar(
        ui.sidebar(
            ui.h3("Critères de tri"),
            ui.input_select('company_name', ui.h4('Sélectionnez une entreprise'), shared_data.company_names)
        ),


        ui.card(
                ui.card_header("Commandes en retard"),
                ui.card_body(
                    ui.output_data_frame('displayOverdueOrders')
                )
        ),
        
        ui.h2("Achats"),
        ui.card(
                ui.card_header("Commandes"),
                ui.card_body(
                    ui.h3("pas encore implémenté.")
                )
            )
        ,
        
        ui.card(
            ui.card_header("Fournisseurs"),
            ui.card_body(
                ui.output_data_frame("displaySuppliers")
            )
        )
    )


@module.server
def suppliers_stats_server(input, output, session):

    purchase_data = getPurchaseData()
    
    @render.data_frame
    def displaySuppliers():
        return (
            purchase_data.suppliers
                .filter(
                    #input.dateslider()[0] <= pl.col("write_date"),
                    #input.dateslider()[1] >= pl.col("write_date"),
                    shared_data.company_dict[f'{input.company_name()}'.replace(" ", "").strip()] == pl.col('company_id')
                )
                .select('name', 'email' ,'website')
                .rename({
                    'name' : 'nom du fournisseur',
                    'website' : 'site web'
            })
        )
    
    @render.data_frame
    def displayOverdueOrders():
        return (
            shared_data.res_partner
            .rename({
                "id" : "res_partner_id",
                "name" : "nom du fournisseur",
                "email" : "email de l'entreprise"
            })
            .join_where(
                purchase_data.purchase_order.rename({
                    'id' : 'id de la commande'
                }),
                pl.col('res_partner_id') == pl.col('partner_id')
            )
            .filter(
                pl.col('receipt_status').is_null()
            )
            .with_columns(date = datetime.now())
            .rename({
                "date": "date actuelle"
            })
            .with_columns(
                (pl.col('date_planned') - 
                pl.col('date actuelle'))
                .mul(-1) # to positive result
                .alias('retard de livraison')
            )
            .select('id de la commande', 'nom du fournisseur', 'email de l\'entreprise', 'retard de livraison')
            .sort(by='retard de livraison', descending=True)
        )
 