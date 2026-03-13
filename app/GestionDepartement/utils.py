"""
Utilitaires pour la génération de PDF
"""
from django.http import HttpResponse
from django.utils import timezone


def generer_pdf_finances(transactions, total_entrees, total_sorties, solde):
    """Génère un PDF récapitulatif des finances"""
    from django.db.models import Sum
    
    now = timezone.now()
    
    # Calculer les stats par département
    departements_stats = {}
    for trans in transactions:
        if trans.departement:
            if trans.departement not in departements_stats:
                departements_stats[trans.departement] = {'entrees': 0, 'sorties': 0}
            if trans.type_mouvement == 'ENTREE':
                departements_stats[trans.departement]['entrees'] += float(trans.montant)
            else:
                departements_stats[trans.departement]['sorties'] += float(trans.montant)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Rapport Financier - {now.strftime('%B %Y')}</title>
    <style>
        @media print {{ body {{ margin: 0; }} }}
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #0000FF; text-align: center; }}
        h2 {{ color: #FFD700; border-bottom: 2px solid #FFD700; padding-bottom: 5px; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 12px; }}
        th {{ background-color: #0000FF; color: white; }}
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 30px 0; }}
        .stat-box {{ text-align: center; padding: 20px; background: #f0f0f0; border-radius: 8px; border-left: 4px solid; }}
        .stat-box.entrees {{ border-color: #22c55e; }}
        .stat-box.sorties {{ border-color: #ef4444; }}
        .stat-box.solde {{ border-color: #0000FF; }}
        .stat-box h3 {{ margin: 0; font-size: 14px; color: #666; }}
        .stat-box p {{ margin: 10px 0 0 0; font-size: 28px; font-weight: bold; }}
        .green {{ color: #22c55e; }}
        .red {{ color: #ef4444; }}
    </style>
</head>
<body>
    <h1>💰 RAPPORT FINANCIER GLOBAL</h1>
    <p style="text-align: center;">Généré le {now.strftime('%d/%m/%Y à %H:%M')}</p>
    
    <div class="stats">
        <div class="stat-box entrees">
            <h3>TOTAL ENTRÉES</h3>
            <p class="green">{total_entrees:,.0f} CFA</p>
        </div>
        <div class="stat-box sorties">
            <h3>TOTAL SORTIES</h3>
            <p class="red">{total_sorties:,.0f} CFA</p>
        </div>
        <div class="stat-box solde">
            <h3>SOLDE NET</h3>
            <p style="color: #0000FF;">{solde:,.0f} CFA</p>
        </div>
    </div>
    
    <h2>📊 Statistiques par Département</h2>
    <table>
        <thead>
            <tr>
                <th>Département</th>
                <th>Entrées</th>
                <th>Sorties</th>
                <th>Solde</th>
            </tr>
        </thead>
        <tbody>"""
    
    for dept, stats in departements_stats.items():
        solde_dept = stats['entrees'] - stats['sorties']
        html_content += f"""
            <tr>
                <td><strong>{dept}</strong></td>
                <td class="green">{stats['entrees']:,.0f} CFA</td>
                <td class="red">{stats['sorties']:,.0f} CFA</td>
                <td style="font-weight: bold;">{solde_dept:,.0f} CFA</td>
            </tr>"""
    
    html_content += """
        </tbody>
    </table>
    
    <h2>📝 Historique des Transactions</h2>
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Département</th>
                <th>Type</th>
                <th>Description</th>
                <th>Catégorie</th>
                <th>Montant</th>
            </tr>
        </thead>
        <tbody>"""
    
    for trans in transactions:
        couleur = 'green' if trans.type_mouvement == 'ENTREE' else 'red'
        signe = '+' if trans.type_mouvement == 'ENTREE' else '-'
        html_content += f"""
            <tr>
                <td>{trans.date_transaction.strftime('%d/%m/%Y')}</td>
                <td><strong>{trans.departement or 'Global'}</strong></td>
                <td>{trans.get_type_mouvement_display()}</td>
                <td>{trans.description}</td>
                <td>{trans.get_categorie_display()}</td>
                <td class="{couleur}" style="font-weight: bold;">{signe}{trans.montant:,.0f} CFA</td>
            </tr>"""
    
    html_content += """
        </tbody>
    </table>
    
    <script>window.print();</script>
</body>
</html>"""
    
    response = HttpResponse(html_content, content_type='text/html')
    return response


def generer_pdf_recapitulatif(rapports, transactions, evenements, stagiaires):
    """Génère un PDF récapitulatif de toutes les activités des départements"""
    from django.db.models import Sum
    
    now = timezone.now()
    
    # Calculer les statistiques financières globales
    total_entrees = sum(float(t.montant) for t in transactions if t.type_mouvement == 'ENTREE')
    total_sorties = sum(float(t.montant) for t in transactions if t.type_mouvement == 'SORTIE')
    solde_global = total_entrees - total_sorties
    
    # Stats par département
    dept_stats = {}
    for trans in transactions:
        if trans.departement:
            if trans.departement not in dept_stats:
                dept_stats[trans.departement] = {'entrees': 0, 'sorties': 0}
            if trans.type_mouvement == 'ENTREE':
                dept_stats[trans.departement]['entrees'] += float(trans.montant)
            else:
                dept_stats[trans.departement]['sorties'] += float(trans.montant)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Récapitulatif Départements - {now.strftime('%B %Y')}</title>
    <style>
        @media print {{ body {{ margin: 0; }} }}
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #0000FF; text-align: center; }}
        h2 {{ color: #FFD700; border-bottom: 2px solid #FFD700; padding-bottom: 5px; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 12px; }}
        th {{ background-color: #0000FF; color: white; }}
        .section {{ page-break-inside: avoid; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
        .stat-box {{ text-align: center; padding: 15px; background: #f0f0f0; border-radius: 8px; border-left: 4px solid; }}
        .stat-box.entrees {{ border-color: #22c55e; }}
        .stat-box.sorties {{ border-color: #ef4444; }}
        .stat-box.solde {{ border-color: #0000FF; }}
        .stat-box h3 {{ margin: 0; font-size: 12px; color: #666; }}
        .stat-box p {{ margin: 5px 0 0 0; font-size: 20px; font-weight: bold; }}
        .green {{ color: #22c55e; }}
        .red {{ color: #ef4444; }}
    </style>
</head>
<body>
    <h1>📊 RÉCAPITULATIF GÉNÉRAL DES DÉPARTEMENTS</h1>
    <p style="text-align: center;">Généré le {now.strftime('%d/%m/%Y à %H:%M')}</p>
    
    <div class="section">
        <h2>💰 STATISTIQUES FINANCIÈRES GLOBALES</h2>
        <div class="stats">
            <div class="stat-box entrees">
                <h3>TOTAL ENTRÉES</h3>
                <p class="green">{total_entrees:,.0f} CFA</p>
            </div>
            <div class="stat-box sorties">
                <h3>TOTAL SORTIES</h3>
                <p class="red">{total_sorties:,.0f} CFA</p>
            </div>
            <div class="stat-box solde">
                <h3>SOLDE NET</h3>
                <p style="color: #0000FF;">{solde_global:,.0f} CFA</p>
            </div>
        </div>
        
        <h3 style="margin-top: 20px;">Finances par Département</h3>
        <table>
            <thead>
                <tr>
                    <th>Département</th>
                    <th>Entrées</th>
                    <th>Sorties</th>
                    <th>Solde</th>
                </tr>
            </thead>
            <tbody>"""
    
    for dept, stats in dept_stats.items():
        solde_dept = stats['entrees'] - stats['sorties']
        html_content += f"""
                <tr>
                    <td><strong>{dept}</strong></td>
                    <td class="green">{stats['entrees']:,.0f} CFA</td>
                    <td class="red">{stats['sorties']:,.0f} CFA</td>
                    <td style="font-weight: bold;">{solde_dept:,.0f} CFA</td>
                </tr>"""
    
    html_content += """
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>1. RAPPORTS DE CULTE PAR DÉPARTEMENT</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Département</th>
                    <th>Responsable</th>
                    <th>1er Culte</th>
                    <th>2ème Culte</th>
                    <th>Boss</th>
                    <th>Statut</th>
                </tr>
            </thead>
            <tbody>"""
    
    for rapport in rapports:
        html_content += f"""
                <tr>
                    <td>{rapport.date_culte.strftime('%d/%m/%Y')}</td>
                    <td><strong>{rapport.nom_departement or '-'}</strong></td>
                    <td>{rapport.responsable.nom_complet if rapport.responsable else '-'}</td>
                    <td>{rapport.culte_1_nbre} / {rapport.culte_1_programme}</td>
                    <td>{rapport.culte_2_nbre} / {rapport.culte_2_programme}</td>
                    <td>{rapport.culte_boss_nbre} / {rapport.culte_boss_programme}</td>
                    <td>{rapport.get_statut_display()}</td>
                </tr>"""
    
    html_content += """
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>2. TRANSACTIONS FINANCIÈRES PAR DÉPARTEMENT</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Département</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Montant</th>
                    <th>Catégorie</th>
                </tr>
            </thead>
            <tbody>"""
    
    for trans in transactions:
        couleur = 'green' if trans.type_mouvement == 'ENTREE' else 'red'
        signe = '+' if trans.type_mouvement == 'ENTREE' else '-'
        html_content += f"""
                <tr>
                    <td>{trans.date_transaction.strftime('%d/%m/%Y')}</td>
                    <td><strong>{trans.departement or '-'}</strong></td>
                    <td>{trans.get_type_mouvement_display()}</td>
                    <td>{trans.description}</td>
                    <td style="color: {couleur}; font-weight: bold;">{signe}{trans.montant} CFA</td>
                    <td>{trans.get_categorie_display()}</td>
                </tr>"""
    
    html_content += """
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>3. ÉVÉNEMENTS PAR DÉPARTEMENT</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Département</th>
                    <th>Type</th>
                    <th>Titre</th>
                    <th>Lieu</th>
                    <th>Statut</th>
                </tr>
            </thead>
            <tbody>"""
    
    for evt in evenements:
        dept = evt.responsable.departement if evt.responsable else '-'
        html_content += f"""
                <tr>
                    <td>{evt.date_evenement.strftime('%d/%m/%Y')}</td>
                    <td><strong>{dept}</strong></td>
                    <td>{evt.get_type_evenement_display()}</td>
                    <td>{evt.titre}</td>
                    <td>{evt.lieu or '-'}</td>
                    <td>{evt.get_statut_display()}</td>
                </tr>"""
    
    html_content += """
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>4. STAGIAIRES PAR DÉPARTEMENT</h2>
        <table>
            <thead>
                <tr>
                    <th>Nom</th>
                    <th>Prénom</th>
                    <th>Département</th>
                    <th>Date début</th>
                    <th>Tuteur</th>
                    <th>Statut</th>
                </tr>
            </thead>
            <tbody>"""
    
    for stag in stagiaires:
        html_content += f"""
                <tr>
                    <td>{stag.nom}</td>
                    <td>{stag.prenom}</td>
                    <td><strong>{stag.departement_accueil or '-'}</strong></td>
                    <td>{stag.date_debut.strftime('%d/%m/%Y')}</td>
                    <td>{stag.tuteur.nom_complet if stag.tuteur else '-'}</td>
                    <td>{stag.get_statut_display()}</td>
                </tr>"""
    
    html_content += """
            </tbody>
        </table>
    </div>
    
    <script>window.print();</script>
</body>
</html>"""
    
    response = HttpResponse(html_content, content_type='text/html')
    return response
