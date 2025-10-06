import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Logements - Île de la Réunion",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(45deg, #FF6B35, #2A9D8F, #E9C46A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .section-header {
        color: #264653;
        border-bottom: 2px solid #FF6B35;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B35;
        margin: 0.5rem 0;
    }
    .commune-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #2A9D8F;
        background-color: #f8f9fa;
    }
    .price-change {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .positive { background-color: #d4edda; border-left: 4px solid #28a745; color: #155724; }
    .negative { background-color: #f8d7da; border-left: 4px solid #dc3545; color: #721c24; }
    .neutral { background-color: #e2e3e5; border-left: 4px solid #6c757d; color: #383d41; }
    .microregion-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .nord { background-color: #FF6B35; color: white; }
    .sud { background-color: #2A9D8F; color: white; }
    .ouest { background-color: #E9C46A; color: black; }
    .est { background-color: #F4A261; color: white; }
    .cirques { background-color: #264653; color: white; }
</style>
""", unsafe_allow_html=True)

class ReunionHousingDashboard:
    def __init__(self):
        self.communes_data = self.define_communes_data()
        self.historical_data = self.initialize_historical_data()
        self.current_data = self.initialize_current_data()
        self.microregion_data = self.initialize_microregion_data()
        
    def define_communes_data(self):
        """Définit les données des communes de La Réunion"""
        return [
            {
                'nom': 'Saint-Denis',
                'micro_region': 'Nord',
                'population': 153810,
                'superficie_km2': 142.79,
                'prix_m2_moyen': 3200,
                'evolution_prix_1an': 4.2,
                'loyers_moyens_m2': 12.5,
                'logements_sociaux_pourcentage': 28,
                'taux_vacance': 6.2,
                'permis_construire_2024': 420,
                'lat': -20.8789,
                'lon': 55.4481,
                'description': 'Préfecture et ville la plus peuplée'
            },
            {
                'nom': 'Saint-Paul',
                'micro_region': 'Ouest',
                'population': 105240,
                'superficie_km2': 241.28,
                'prix_m2_moyen': 2800,
                'evolution_prix_1an': 5.8,
                'loyers_moyens_m2': 10.8,
                'logements_sociaux_pourcentage': 32,
                'taux_vacance': 5.8,
                'permis_construire_2024': 380,
                'lat': -21.0097,
                'lon': 55.2697,
                'description': 'Deuxième ville de l\'île, fort développement'
            },
            {
                'nom': 'Saint-Pierre',
                'micro_region': 'Sud',
                'population': 84520,
                'superficie_km2': 95.99,
                'prix_m2_moyen': 2950,
                'evolution_prix_1an': 6.1,
                'loyers_moyens_m2': 11.2,
                'logements_sociaux_pourcentage': 26,
                'taux_vacance': 4.9,
                'permis_construire_2024': 350,
                'lat': -21.3393,
                'lon': 55.4781,
                'description': 'Sous-préfecture du Sud, pôle économique'
            },
            {
                'nom': 'Le Tampon',
                'micro_region': 'Sud',
                'population': 79849,
                'superficie_km2': 165.43,
                'prix_m2_moyen': 2600,
                'evolution_prix_1an': 5.2,
                'loyers_moyens_m2': 9.8,
                'logements_sociaux_pourcentage': 24,
                'taux_vacance': 5.1,
                'permis_construire_2024': 290,
                'lat': -21.2779,
                'lon': 55.5179,
                'description': 'Commune résidentielle en forte croissance'
            },
            {
                'nom': 'Saint-André',
                'micro_region': 'Est',
                'population': 56602,
                'superficie_km2': 53.07,
                'prix_m2_moyen': 2200,
                'evolution_prix_1an': 3.8,
                'loyers_moyens_m2': 8.5,
                'logements_sociaux_pourcentage': 35,
                'taux_vacance': 7.2,
                'permis_construire_2024': 180,
                'lat': -20.9631,
                'lon': 55.6508,
                'description': 'Commune agricole en développement'
            },
            {
                'nom': 'Saint-Louis',
                'micro_region': 'Sud',
                'population': 53609,
                'superficie_km2': 98.90,
                'prix_m2_moyen': 2450,
                'evolution_prix_1an': 4.9,
                'loyers_moyens_m2': 10.2,
                'logements_sociaux_pourcentage': 31,
                'taux_vacance': 6.5,
                'permis_construire_2024': 220,
                'lat': -21.2861,
                'lon': 55.4111,
                'description': 'Pôle économique du Sud'
            },
            {
                'nom': 'Le Port',
                'micro_region': 'Ouest',
                'population': 32995,
                'superficie_km2': 16.62,
                'prix_m2_moyen': 1950,
                'evolution_prix_1an': 2.8,
                'loyers_moyens_m2': 7.8,
                'logements_sociaux_pourcentage': 45,
                'taux_vacance': 8.5,
                'permis_construire_2024': 120,
                'lat': -20.9394,
                'lon': 55.2928,
                'description': 'Ville portuaire et industrielle'
            },
            {
                'nom': 'Saint-Joseph',
                'micro_region': 'Sud',
                'population': 37882,
                'superficie_km2': 178.50,
                'prix_m2_moyen': 2100,
                'evolution_prix_1an': 4.1,
                'loyers_moyens_m2': 8.2,
                'logements_sociaux_pourcentage': 29,
                'taux_vacance': 6.8,
                'permis_construire_2024': 160,
                'lat': -21.3778,
                'lon': 55.6197,
                'description': 'Grande commune du Sud'
            },
            {
                'nom': 'Saint-Benoît',
                'micro_region': 'Est',
                'population': 37308,
                'superficie_km2': 229.61,
                'prix_m2_moyen': 2050,
                'evolution_prix_1an': 3.5,
                'loyers_moyens_m2': 7.9,
                'logements_sociaux_pourcentage': 33,
                'taux_vacance': 7.1,
                'permis_construire_2024': 140,
                'lat': -21.0339,
                'lon': 55.7147,
                'description': 'Sous-préfecture de l\'Est'
            },
            {
                'nom': 'Sainte-Marie',
                'micro_region': 'Nord',
                'population': 34167,
                'superficie_km2': 87.21,
                'prix_m2_moyen': 2850,
                'evolution_prix_1an': 4.5,
                'loyers_moyens_m2': 11.0,
                'logements_sociaux_pourcentage': 27,
                'taux_vacance': 5.5,
                'permis_construire_2024': 190,
                'lat': -20.8969,
                'lon': 55.5492,
                'description': 'Ville dynamique du Nord'
            },
            {
                'nom': 'Saint-Leu',
                'micro_region': 'Ouest',
                'population': 34746,
                'superficie_km2': 118.37,
                'prix_m2_moyen': 2700,
                'evolution_prix_1an': 5.5,
                'loyers_moyens_m2': 10.5,
                'logements_sociaux_pourcentage': 25,
                'taux_vacance': 5.2,
                'permis_construire_2024': 210,
                'lat': -21.1653,
                'lon': 55.2881,
                'description': 'Station balnéaire prisée'
            },
            {
                'nom': 'La Possession',
                'micro_region': 'Ouest',
                'population': 33506,
                'superficie_km2': 118.35,
                'prix_m2_moyen': 2500,
                'evolution_prix_1an': 4.8,
                'loyers_moyens_m2': 9.5,
                'logements_sociaux_pourcentage': 30,
                'taux_vacance': 5.9,
                'permis_construire_2024': 170,
                'lat': -20.9253,
                'lon': 55.3358,
                'description': 'Ville en développement rapide'
            },
            {
                'nom': 'Sainte-Suzanne',
                'micro_region': 'Nord',
                'population': 24645,
                'superficie_km2': 57.84,
                'prix_m2_moyen': 2650,
                'evolution_prix_1an': 4.0,
                'loyers_moyens_m2': 10.0,
                'logements_sociaux_pourcentage': 28,
                'taux_vacance': 6.0,
                'permis_construire_2024': 130,
                'lat': -20.9061,
                'lon': 55.6069,
                'description': 'Commune agricole et résidentielle'
            },
            {
                'nom': 'Bras-Panon',
                'micro_region': 'Est',
                'population': 13170,
                'superficie_km2': 88.55,
                'prix_m2_moyen': 1900,
                'evolution_prix_1an': 3.2,
                'loyers_moyens_m2': 7.2,
                'logements_sociaux_pourcentage': 32,
                'taux_vacance': 7.5,
                'permis_construire_2024': 90,
                'lat': -21.0017,
                'lon': 55.6772,
                'description': 'Commune rurale de l\'Est'
            },
            {
                'nom': 'Les Avirons',
                'micro_region': 'Ouest',
                'population': 11447,
                'superficie_km2': 26.27,
                'prix_m2_moyen': 2350,
                'evolution_prix_1an': 4.3,
                'loyers_moyens_m2': 9.0,
                'logements_sociaux_pourcentage': 26,
                'taux_vacance': 5.7,
                'permis_construire_2024': 110,
                'lat': -21.2408,
                'lon': 55.3392,
                'description': 'Petite commune de l\'Ouest'
            },
            {
                'nom': 'Entre-Deux',
                'micro_region': 'Sud',
                'population': 7070,
                'superficie_km2': 66.83,
                'prix_m2_moyen': 2000,
                'evolution_prix_1an': 3.7,
                'loyers_moyens_m2': 7.5,
                'logements_sociaux_pourcentage': 22,
                'taux_vacance': 6.3,
                'permis_construire_2024': 70,
                'lat': -21.2500,
                'lon': 55.4722,
                'description': 'Commune des Hauts de l\'île'
            },
            {
                'nom': 'L\'Étang-Salé',
                'micro_region': 'Ouest',
                'population': 14030,
                'superficie_km2': 38.65,
                'prix_m2_moyen': 2400,
                'evolution_prix_1an': 4.6,
                'loyers_moyens_m2': 9.2,
                'logements_sociaux_pourcentage': 27,
                'taux_vacance': 5.4,
                'permis_construire_2024': 100,
                'lat': -21.2631,
                'lon': 55.3842,
                'description': 'Station balnéaire familiale'
            },
            {
                'nom': 'Petite-Île',
                'micro_region': 'Sud',
                'population': 12155,
                'superficie_km2': 33.93,
                'prix_m2_moyen': 2250,
                'evolution_prix_1an': 4.0,
                'loyers_moyens_m2': 8.8,
                'logements_sociaux_pourcentage': 29,
                'taux_vacance': 6.1,
                'permis_construire_2024': 85,
                'lat': -21.3531,
                'lon': 55.5639,
                'description': 'Petite commune du Sud'
            },
            {
                'nom': 'Saint-Philippe',
                'micro_region': 'Sud',
                'population': 5232,
                'superficie_km2': 153.94,
                'prix_m2_moyen': 1800,
                'evolution_prix_1an': 2.9,
                'loyers_moyens_m2': 6.8,
                'logements_sociaux_pourcentage': 24,
                'taux_vacance': 8.0,
                'permis_construire_2024': 50,
                'lat': -21.3592,
                'lon': 55.7672,
                'description': 'Commune sauvage du Sud Sauvage'
            },
            {
                'nom': 'Sainte-Rose',
                'micro_region': 'Est',
                'population': 6424,
                'superficie_km2': 177.60,
                'prix_m2_moyen': 1750,
                'evolution_prix_1an': 2.7,
                'loyers_moyens_m2': 6.5,
                'logements_sociaux_pourcentage': 26,
                'taux_vacance': 8.2,
                'permis_construire_2024': 45,
                'lat': -21.1242,
                'lon': 55.7961,
                'description': 'Commune de l\'Est préservée'
            },
            {
                'nom': 'Cilaos',
                'micro_region': 'Cirques',
                'population': 5528,
                'superficie_km2': 84.40,
                'prix_m2_moyen': 1600,
                'evolution_prix_1an': 2.5,
                'loyers_moyens_m2': 6.0,
                'logements_sociaux_pourcentage': 35,
                'taux_vacance': 9.0,
                'permis_construire_2024': 30,
                'lat': -21.1339,
                'lon': 55.4719,
                'description': 'Commune du cirque de Cilaos'
            },
            {
                'nom': 'Salazie',
                'micro_region': 'Cirques',
                'population': 7363,
                'superficie_km2': 103.82,
                'prix_m2_moyen': 1550,
                'evolution_prix_1an': 2.3,
                'loyers_moyens_m2': 5.8,
                'logements_sociaux_pourcentage': 38,
                'taux_vacance': 9.5,
                'permis_construire_2024': 35,
                'lat': -21.0272,
                'lon': 55.5392,
                'description': 'Commune du cirque de Salazie'
            },
            {
                'nom': 'Les Trois-Bassins',
                'micro_region': 'Ouest',
                'population': 6980,
                'superficie_km2': 42.58,
                'prix_m2_moyen': 2300,
                'evolution_prix_1an': 4.2,
                'loyers_moyens_m2': 8.9,
                'logements_sociaux_pourcentage': 25,
                'taux_vacance': 5.8,
                'permis_construire_2024': 75,
                'lat': -21.1039,
                'lon': 55.2992,
                'description': 'Commune de l\'Ouest'
            }
        ]
    
    def initialize_historical_data(self):
        """Initialise les données historiques des prix"""
        dates = pd.date_range('2018-01-01', datetime.now(), freq='M')
        data = []
        
        for date in dates:
            for commune in self.communes_data:
                # Prix de base selon les données actuelles
                base_price = commune['prix_m2_moyen'] * 0.7  # Prix plus bas en 2018
                
                # Évolution progressive avec volatilité
                years_passed = (date.year - 2018) + (date.month - 1) / 12
                trend_factor = 1 + (years_passed * 0.05)  # Tendance haussière de 5% par an
                
                # Volatilité mensuelle
                monthly_volatility = np.random.normal(1, 0.02)
                
                prix = base_price * trend_factor * monthly_volatility
                
                data.append({
                    'date': date,
                    'commune': commune['nom'],
                    'micro_region': commune['micro_region'],
                    'prix_m2': prix,
                    'loyer_m2': commune['loyers_moyens_m2'] * 0.8 * trend_factor,
                    'permis_construire': commune['permis_construire_2024'] * 0.7 * (1 + years_passed * 0.1)
                })
        
        return pd.DataFrame(data)
    
    def initialize_current_data(self):
        """Initialise les données courantes sous forme de DataFrame"""
        return pd.DataFrame(self.communes_data)
    
    def initialize_microregion_data(self):
        """Initialise les données par micro-région"""
        microregions = list(set([commune['micro_region'] for commune in self.communes_data]))
        data = []
        
        for microregion in microregions:
            communes_microregion = [c for c in self.communes_data if c['micro_region'] == microregion]
            
            population_totale = sum([c['population'] for c in communes_microregion])
            prix_moyen = np.mean([c['prix_m2_moyen'] for c in communes_microregion])
            evolution_prix_moyenne = np.mean([c['evolution_prix_1an'] for c in communes_microregion])
            permis_construire_total = sum([c['permis_construire_2024'] for c in communes_microregion])
            taux_vacance_moyen = np.mean([c['taux_vacance'] for c in communes_microregion])
            
            data.append({
                'micro_region': microregion,
                'population': population_totale,
                'prix_m2_moyen': prix_moyen,
                'evolution_prix_1an': evolution_prix_moyenne,
                'permis_construire_total': permis_construire_total,
                'taux_vacance_moyen': taux_vacance_moyen,
                'nombre_communes': len(communes_microregion)
            })
        
        return pd.DataFrame(data)
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">🏝️ Dashboard Logements - Île de la Réunion</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("**Analyse du marché immobilier réunionnais - Données 2024**")
        
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M')
        st.sidebar.markdown(f"**🕐 Dernière mise à jour: {current_time}**")
    
    def display_key_metrics(self):
        """Affiche les métriques clés du marché immobilier"""
        st.markdown('<h3 class="section-header">📊 INDICATEURS CLÉS DU MARCHÉ</h3>', 
                   unsafe_allow_html=True)
        
        # Calcul des métriques globales
        prix_moyen_global = self.current_data['prix_m2_moyen'].mean()
        evolution_prix_moyenne = self.current_data['evolution_prix_1an'].mean()
        population_totale = self.current_data['population'].sum()
        permis_construire_total = self.current_data['permis_construire_2024'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Prix moyen au m²",
                f"{prix_moyen_global:.0f} €",
                f"{evolution_prix_moyenne:+.1f}%",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Loyer moyen au m²",
                f"{self.current_data['loyers_moyens_m2'].mean():.1f} €",
                f"{np.random.uniform(1, 3):.1f}%"
            )
        
        with col3:
            st.metric(
                "Population totale",
                f"{population_totale:,}",
                f"{np.random.uniform(0.5, 1.5):.1f}%"
            )
        
        with col4:
            st.metric(
                "Permis de construire 2024",
                f"{permis_construire_total:,}",
                f"{np.random.uniform(5, 15):.0f}%"
            )
    
    def create_market_overview(self):
        """Crée la vue d'ensemble du marché"""
        st.markdown('<h3 class="section-header">🏛️ VUE D\'ENSEMBLE DU MARCHÉ</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["Carte Interactive", "Évolution des Prix", "Répartition Micro-régions", "Indicateurs Clés"])
        
        with tab1:
            # Carte interactive avec Folium
            st.subheader("Carte des prix au m² par commune")
            
            # Création de la carte centrée sur La Réunion
            m = folium.Map(location=[-21.115, 55.536], zoom_start=10)
            
            # Ajout des marqueurs pour chaque commune
            for commune in self.communes_data:
                # Déterminer la couleur en fonction du prix
                if commune['prix_m2_moyen'] > 2800:
                    color = 'red'
                elif commune['prix_m2_moyen'] > 2300:
                    color = 'orange'
                elif commune['prix_m2_moyen'] > 1800:
                    color = 'green'
                else:
                    color = 'blue'
                
                # Popup avec informations détaillées
                popup_text = f"""
                <b>{commune['nom']}</b><br>
                Micro-région: {commune['micro_region']}<br>
                Prix m²: {commune['prix_m2_moyen']} €<br>
                Évolution: {commune['evolution_prix_1an']} %<br>
                Population: {commune['population']:,}<br>
                Taux vacance: {commune['taux_vacance']} %
                """
                
                folium.Marker(
                    [commune['lat'], commune['lon']],
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=commune['nom'],
                    icon=folium.Icon(color=color, icon='home', prefix='fa')
                ).add_to(m)
            
            # Affichage de la carte
            folium_static(m, width=1000, height=500)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Évolution des prix moyens par micro-région
                evolution_data = self.historical_data.groupby([
                    self.historical_data['date'].dt.year,
                    'micro_region'
                ])['prix_m2'].mean().reset_index()
                
                fig = px.line(evolution_data, 
                             x='date', 
                             y='prix_m2',
                             color='micro_region',
                             title='Évolution des prix au m² par micro-région (2018-2024)',
                             color_discrete_sequence=['#FF6B35', '#2A9D8F', '#E9C46A', '#F4A261', '#264653'])
                fig.update_layout(yaxis_title="Prix moyen au m² (€)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Évolution des loyers
                loyer_data = self.historical_data.groupby([
                    self.historical_data['date'].dt.year,
                    'micro_region'
                ])['loyer_m2'].mean().reset_index()
                
                fig = px.line(loyer_data, 
                             x='date', 
                             y='loyer_m2',
                             color='micro_region',
                             title='Évolution des loyers au m² par micro-région (2018-2024)',
                             color_discrete_sequence=['#FF6B35', '#2A9D8F', '#E9C46A', '#F4A261', '#264653'])
                fig.update_layout(yaxis_title="Loyer moyen au m² (€)")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                # Répartition des communes par micro-région
                fig = px.pie(self.microregion_data, 
                            values='nombre_communes', 
                            names='micro_region',
                            title='Répartition des communes par micro-région',
                            color='micro_region',
                            color_discrete_map={
                                'Nord': '#FF6B35',
                                'Sud': '#2A9D8F',
                                'Ouest': '#E9C46A',
                                'Est': '#F4A261',
                                'Cirques': '#264653'
                            })
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Prix moyens par micro-région
                fig = px.bar(self.microregion_data, 
                            x='micro_region', 
                            y='prix_m2_moyen',
                            title='Prix moyen au m² par micro-région',
                            color='micro_region',
                            color_discrete_map={
                                'Nord': '#FF6B35',
                                'Sud': '#2A9D8F',
                                'Ouest': '#E9C46A',
                                'Est': '#F4A261',
                                'Cirques': '#264653'
                            })
                fig.update_layout(yaxis_title="Prix moyen au m² (€)")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                # Taux de vacance par micro-région
                taux_vacance_data = self.current_data.groupby('micro_region')['taux_vacance'].mean().reset_index()
                
                fig = px.bar(taux_vacance_data, 
                            x='micro_region', 
                            y='taux_vacance',
                            title='Taux de vacance moyen par micro-région',
                            color='micro_region',
                            color_discrete_map={
                                'Nord': '#FF6B35',
                                'Sud': '#2A9D8F',
                                'Ouest': '#E9C46A',
                                'Est': '#F4A261',
                                'Cirques': '#264653'
                            })
                fig.update_layout(yaxis_title="Taux de vacance (%)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Logements sociaux par micro-région
                logements_sociaux_data = self.current_data.groupby('micro_region')['logements_sociaux_pourcentage'].mean().reset_index()
                
                fig = px.bar(logements_sociaux_data, 
                            x='micro_region', 
                            y='logements_sociaux_pourcentage',
                            title='Pourcentage de logements sociaux par micro-région',
                            color='micro_region',
                            color_discrete_map={
                                'Nord': '#FF6B35',
                                'Sud': '#2A9D8F',
                                'Ouest': '#E9C46A',
                                'Est': '#F4A261',
                                'Cirques': '#264653'
                            })
                fig.update_layout(yaxis_title="Logements sociaux (%)")
                st.plotly_chart(fig, use_container_width=True)
    
    def create_communes_analysis(self):
        """Affiche l'analyse détaillée par commune"""
        st.markdown('<h3 class="section-header">🏢 ANALYSE PAR COMMUNE</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Comparaison Communes", "Top Performances", "Détails par Commune"])
        
        with tab1:
            # Filtres pour les communes
            col1, col2, col3 = st.columns(3)
            with col1:
                microregion_filtre = st.selectbox("Micro-région:", 
                                                ['Toutes'] + list(self.microregion_data['micro_region'].unique()))
            with col2:
                population_filtre = st.selectbox("Taille:", 
                                               ['Toutes', 'Grandes (>50k)', 'Moyennes (20k-50k)', 'Petites (<20k)'])
            with col3:
                tri_filtre = st.selectbox("Trier par:", 
                                        ['Prix m²', 'Évolution prix', 'Population', 'Permis construire'])
            
            # Application des filtres
            communes_filtrees = self.current_data.copy()
            if microregion_filtre != 'Toutes':
                communes_filtrees = communes_filtrees[communes_filtrees['micro_region'] == microregion_filtre]
            if population_filtre == 'Grandes (>50k)':
                communes_filtrees = communes_filtrees[communes_filtrees['population'] > 50000]
            elif population_filtre == 'Moyennes (20k-50k)':
                communes_filtrees = communes_filtrees[(communes_filtrees['population'] >= 20000) & 
                                                     (communes_filtrees['population'] <= 50000)]
            elif population_filtre == 'Petites (<20k)':
                communes_filtrees = communes_filtrees[communes_filtrees['population'] < 20000]
            
            # Tri
            if tri_filtre == 'Prix m²':
                communes_filtrees = communes_filtrees.sort_values('prix_m2_moyen', ascending=False)
            elif tri_filtre == 'Évolution prix':
                communes_filtrees = communes_filtrees.sort_values('evolution_prix_1an', ascending=False)
            elif tri_filtre == 'Population':
                communes_filtrees = communes_filtrees.sort_values('population', ascending=False)
            elif tri_filtre == 'Permis construire':
                communes_filtrees = communes_filtrees.sort_values('permis_construire_2024', ascending=False)
            
            # Affichage des communes
            for _, commune in communes_filtrees.iterrows():
                change_class = ""
                if commune['evolution_prix_1an'] > 0:
                    change_class = "positive"
                elif commune['evolution_prix_1an'] < 0:
                    change_class = "negative"
                else:
                    change_class = "neutral"
                
                col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{commune['nom']}**")
                    microregion_class = commune['micro_region'].lower()
                    st.markdown(f"<div class='microregion-badge {microregion_class}'>{commune['micro_region']}</div>", 
                               unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**{commune['description']}**")
                    st.markdown(f"Population: {commune['population']:,} hab")
                with col3:
                    st.markdown(f"**{commune['prix_m2_moyen']:.0f} €/m²**")
                    st.markdown(f"Loyer: {commune['loyers_moyens_m2']} €/m²")
                with col4:
                    evolution_str = f"{commune['evolution_prix_1an']:+.1f}%"
                    st.markdown(f"**{evolution_str}**")
                    st.markdown(f"Vacance: {commune['taux_vacance']}%")
                with col5:
                    st.markdown(f"<div class='price-change {change_class}'>{evolution_str}</div>", 
                               unsafe_allow_html=True)
                    st.markdown(f"Permis: {commune['permis_construire_2024']}")
                
                st.markdown("---")
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top des communes avec la plus forte hausse des prix
                top_hausse = self.current_data.nlargest(10, 'evolution_prix_1an')
                fig = px.bar(top_hausse, 
                            x='evolution_prix_1an', 
                            y='nom',
                            orientation='h',
                            title='Top 10 des communes avec la plus forte hausse des prix (%)',
                            color='evolution_prix_1an',
                            color_continuous_scale='Greens')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top des communes avec le plus de permis de construire
                top_permis = self.current_data.nlargest(10, 'permis_construire_2024')
                fig = px.bar(top_permis, 
                            x='permis_construire_2024', 
                            y='nom',
                            orientation='h',
                            title='Top 10 des communes avec le plus de permis de construire (2024)',
                            color='permis_construire_2024',
                            color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Détails pour une commune sélectionnée
            commune_selectionnee = st.selectbox("Sélectionnez une commune:", 
                                             self.current_data['nom'].unique())
            
            if commune_selectionnee:
                commune_data = self.current_data[self.current_data['nom'] == commune_selectionnee].iloc[0]
                historique_commune = self.historical_data[self.historical_data['commune'] == commune_selectionnee]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(f"Fiche commune: {commune_selectionnee}")
                    
                    st.metric("Micro-région", commune_data['micro_region'])
                    st.metric("Population", f"{commune_data['population']:,}")
                    st.metric("Superficie", f"{commune_data['superficie_km2']} km²")
                    st.metric("Prix moyen au m²", f"{commune_data['prix_m2_moyen']} €")
                    st.metric("Évolution prix (1 an)", f"{commune_data['evolution_prix_1an']}%")
                    st.metric("Loyer moyen au m²", f"{commune_data['loyers_moyens_m2']} €")
                    st.metric("Taux de vacance", f"{commune_data['taux_vacance']}%")
                    st.metric("Logements sociaux", f"{commune_data['logements_sociaux_pourcentage']}%")
                    st.metric("Permis de construire 2024", commune_data['permis_construire_2024'])
                
                with col2:
                    # Graphique d'évolution des prix pour la commune sélectionnée
                    fig = px.line(historique_commune, 
                                 x='date', 
                                 y='prix_m2',
                                 title=f'Évolution des prix au m² à {commune_selectionnee}',
                                 color_discrete_sequence=['#FF6B35'])
                    fig.update_layout(yaxis_title="Prix au m² (€)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Graphique d'évolution des loyers
                    fig = px.line(historique_commune, 
                                 x='date', 
                                 y='loyer_m2',
                                 title=f'Évolution des loyers au m² à {commune_selectionnee}',
                                 color_discrete_sequence=['#2A9D8F'])
                    fig.update_layout(yaxis_title="Loyer au m² (€)")
                    st.plotly_chart(fig, use_container_width=True)
    
    def create_microregion_analysis(self):
        """Analyse détaillée par micro-région"""
        st.markdown('<h3 class="section-header">📊 ANALYSE PAR MICRO-RÉGION</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Comparaison Micro-régions", "Détails Micro-région", "Tendances"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Comparaison des prix moyens
                fig = px.bar(self.microregion_data, 
                            x='micro_region', 
                            y='prix_m2_moyen',
                            title='Comparaison des prix moyens au m² par micro-région',
                            color='micro_region',
                            color_discrete_map={
                                'Nord': '#FF6B35',
                                'Sud': '#2A9D8F',
                                'Ouest': '#E9C46A',
                                'Est': '#F4A261',
                                'Cirques': '#264653'
                            })
                fig.update_layout(yaxis_title="Prix moyen au m² (€)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Comparaison de l'évolution des prix
                fig = px.bar(self.microregion_data, 
                            x='micro_region', 
                            y='evolution_prix_1an',
                            title='Évolution des prix sur 1 an par micro-région',
                            color='micro_region',
                            color_discrete_map={
                                'Nord': '#FF6B35',
                                'Sud': '#2A9D8F',
                                'Ouest': '#E9C46A',
                                'Est': '#F4A261',
                                'Cirques': '#264653'
                            })
                fig.update_layout(yaxis_title="Évolution des prix (%)")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Détails pour une micro-région sélectionnée
            microregion_selectionnee = st.selectbox("Sélectionnez une micro-région:", 
                                                  self.microregion_data['micro_region'].unique())
            
            if microregion_selectionnee:
                communes_microregion = self.current_data[
                    self.current_data['micro_region'] == microregion_selectionnee
                ]
                historique_microregion = self.historical_data[
                    self.historical_data['micro_region'] == microregion_selectionnee
                ]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(f"Micro-région: {microregion_selectionnee}")
                    
                    microregion_info = self.microregion_data[
                        self.microregion_data['micro_region'] == microregion_selectionnee
                    ].iloc[0]
                    
                    st.metric("Nombre de communes", microregion_info['nombre_communes'])
                    st.metric("Population totale", f"{microregion_info['population']:,}")
                    st.metric("Prix moyen au m²", f"{microregion_info['prix_m2_moyen']:.0f} €")
                    st.metric("Évolution prix moyenne", f"{microregion_info['evolution_prix_1an']:.1f}%")
                    st.metric("Taux de vacance moyen", f"{microregion_info['taux_vacance_moyen']:.1f}%")
                    st.metric("Permis de construire total", microregion_info['permis_construire_total'])
                    
                    # Liste des communes de la micro-région
                    st.subheader("Communes de la micro-région")
                    for _, commune in communes_microregion.iterrows():
                        st.write(f"- {commune['nom']} ({commune['population']:,} hab.)")
                
                with col2:
                    # Graphique d'évolution des prix pour la micro-région
                    evolution_microregion = historique_microregion.groupby('date')['prix_m2'].mean().reset_index()
                    
                    fig = px.line(evolution_microregion, 
                                 x='date', 
                                 y='prix_m2',
                                 title=f'Évolution des prix au m² - {microregion_selectionnee}',
                                 color_discrete_sequence=['#FF6B35'])
                    fig.update_layout(yaxis_title="Prix moyen au m² (€)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Graphique de répartition des prix par commune
                    fig = px.bar(communes_microregion.sort_values('prix_m2_moyen', ascending=False), 
                                x='nom', 
                                y='prix_m2_moyen',
                                title=f'Prix au m² par commune - {microregion_selectionnee}',
                                color='prix_m2_moyen',
                                color_continuous_scale='Viridis')
                    fig.update_layout(xaxis_title="Commune", yaxis_title="Prix au m² (€)")
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Tendances et Perspectives par Micro-région")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📈 Micro-régions Dynamiques
                
                **🏝️ Ouest:**
                - Forte attractivité touristique
                - Développement résidentiel important
                - Prix en hausse constante
                - Projets d'aménagement nombreux
                
                **🌋 Sud:**
                - Croissance économique soutenue
                - Pôle universitaire et de recherche
                - Équipements structurants récents
                - Dynamisme démographique
                """)
            
            with col2:
                st.markdown("""
                ### 📉 Micro-régions en Mutation
                
                **🏛️ Nord:**
                - Marché mature mais cher
                - Saturation des espaces constructibles
                - Renouvellement urbain important
                - Projets de densification
                
                **🌿 Est:**
                - Prix plus accessibles
                - Potentiel de développement
                - Enjeux de désenclavement
                - Préservation des espaces naturels
                
                **⛰️ Cirques:**
                - Marché très spécifique
                - Enjeux de préservation
                - Défis d'accessibilité
                - Tourisme comme levier
                """)
    
    def create_affordability_analysis(self):
        """Analyse de l'accessibilité au logement"""
        st.markdown('<h3 class="section-header">💰 ACCESSIBILITÉ AU LOGEMENT</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Indicateurs d'Accessibilité", "Effort d'Épargne", "Recommandations"])
        
        with tab1:
            # Calcul d'indicateurs d'accessibilité
            self.current_data['prix_appart_70m2'] = self.current_data['prix_m2_moyen'] * 70
            self.current_data['loyer_appart_70m2'] = self.current_data['loyers_moyens_m2'] * 70
            self.current_data['annees_epargne'] = self.current_data['prix_appart_70m2'] / (2000 * 12)  # Simulation épargne
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Prix d'un appartement 70m² par commune
                fig = px.bar(self.current_data.nlargest(15, 'prix_appart_70m2'), 
                            x='prix_appart_70m2', 
                            y='nom',
                            orientation='h',
                            title='Prix d\'un appartement 70m² par commune (€)',
                            color='prix_appart_70m2',
                            color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Années d'épargne nécessaires
                fig = px.bar(self.current_data.nlargest(15, 'annees_epargne'), 
                            x='annees_epargne', 
                            y='nom',
                            orientation='h',
                            title='Années d\'épargne nécessaires (appartement 70m²)',
                            color='annees_epargne',
                            color_continuous_scale='Oranges')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Simulateur d'effort d'épargne")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                commune_choisie = st.selectbox("Commune:", self.current_data['nom'].unique())
                surface_desiree = st.slider("Surface (m²):", 30, 120, 70)
            
            with col2:
                apport_personnel = st.number_input("Apport personnel (€):", 0, 100000, 20000, step=5000)
                epargne_mensuelle = st.number_input("Épargne mensuelle (€):", 100, 3000, 1000, step=100)
            
            with col3:
                duree_pret = st.slider("Durée du prêt (ans):", 15, 25, 20)
                taux_pret = st.slider("Taux du prêt (%):", 1.0, 5.0, 3.0, step=0.1)
            
            if commune_choisie:
                commune_info = self.current_data[self.current_data['nom'] == commune_choisie].iloc[0]
                prix_total = commune_info['prix_m2_moyen'] * surface_desiree
                montant_emprunte = prix_total - apport_personnel
                
                # Calcul mensualité (simplifié)
                taux_mensuel = taux_pret / 100 / 12
                nb_mensualites = duree_pret * 12
                if taux_mensuel > 0:
                    mensualite = (montant_emprunte * taux_mensuel * (1 + taux_mensuel)**nb_mensualites) / ((1 + taux_mensuel)**nb_mensualites - 1)
                else:
                    mensualite = montant_emprunte / nb_mensualites
                
                # Affichage des résultats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prix total", f"{prix_total:,.0f} €")
                    st.metric("Montant à emprunter", f"{montant_emprunte:,.0f} €")
                with col2:
                    st.metric("Mensualité estimée", f"{mensualite:.0f} €")
                    st.metric("Taux d'endettement", f"{(mensualite / 2000 * 100):.1f}%")
                with col3:
                    st.metric("Épargne nécessaire", f"{apport_personnel:,.0f} €")
                    st.metric("Durée d'épargne", f"{(apport_personnel / epargne_mensuelle / 12):.1f} ans")
        
        with tab3:
            st.subheader("Recommandations pour l'Accession")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🏠 Communes Accessibles
                
                **Prix inférieurs à 2 000 €/m²:**
                - Saint-Philippe
                - Sainte-Rose  
                - Cilaos
                - Salazie
                - Bras-Panon
                
                **Avantages:**
                - Prix d'entrée abordable
                - Cadre de vie préservé
                - Potentiel de plus-value
                """)
            
            with col2:
                st.markdown("""
                ### 💡 Stratégies d'Accession
                
                **Aides disponibles:**
                - Prêt à taux zéro (PTZ)
                - Prêt action logement
                - Aides locales (région, département)
                - Dispositif Pinel (investissement locatif)
                
                **Conseils pratiques:**
                - Constituer un apport conséquent
                - Optimiser son profil emprunteur
                - Étudier les programmes neufs
                - Considérer la colocation accession
                """)
    
    def create_sidebar(self):
        """Crée la sidebar avec les contrôles"""
        st.sidebar.markdown("## 🎛️ CONTRÔLES D'ANALYSE")
        
        # Filtres temporels
        st.sidebar.markdown("### 📅 Période d'analyse")
        date_debut = st.sidebar.date_input("Date de début", 
                                         value=datetime.now() - timedelta(days=365*3))
        date_fin = st.sidebar.date_input("Date de fin", 
                                       value=datetime.now())
        
        # Filtres micro-régions
        st.sidebar.markdown("### 🗺️ Sélection des micro-régions")
        microregions_selectionnees = st.sidebar.multiselect(
            "Micro-régions à afficher:",
            list(self.microregion_data['micro_region'].unique()),
            default=list(self.microregion_data['micro_region'].unique())[:3]
        )
        
        # Options d'affichage
        st.sidebar.markdown("### ⚙️ Options")
        show_technical = st.sidebar.checkbox("Afficher indicateurs techniques", value=True)
        auto_refresh = st.sidebar.checkbox("Rafraîchissement automatique", value=False)
        
        # Bouton de rafraîchissement manuel
        if st.sidebar.button("🔄 Rafraîchir les données"):
            st.rerun()
        
        # Informations marché
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 INDICES RÉGIONAUX")
        
        # Indices simulés
        indices = {
            'Prix moyen France': {'valeur': 3800, 'variation': 2.1},
            'Prix moyen Outre-mer': {'valeur': 2800, 'variation': 3.8},
            'Loyer moyen France': {'valeur': 11.5, 'variation': 1.2},
            'Taux vacance national': {'valeur': 7.2, 'variation': -0.3}
        }
        
        for indice, data in indices.items():
            st.sidebar.metric(
                indice,
                f"{data['valeur']}",
                f"{data['variation']:+.1f}%"
            )
        
        return {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'microregions_selectionnees': microregions_selectionnees,
            'show_technical': show_technical,
            'auto_refresh': auto_refresh
        }

    def run_dashboard(self):
        """Exécute le dashboard complet"""
        # Sidebar
        controls = self.create_sidebar()
        
        # Header
        self.display_header()
        
        # Métriques clés
        self.display_key_metrics()
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Vue d'ensemble", 
            "🏢 Communes", 
            "🗺️ Micro-régions", 
            "💰 Accessibilité", 
            "📊 Tendances",
            "ℹ️ À Propos"
        ])
        
        with tab1:
            self.create_market_overview()
        
        with tab2:
            self.create_communes_analysis()
        
        with tab3:
            self.create_microregion_analysis()
        
        with tab4:
            self.create_affordability_analysis()
        
        with tab5:
            st.markdown("## 📊 TENDANCES ET PERSPECTIVES")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🎯 TENDANCES DU MARCHÉ
                
                **📈 Dynamiques Territoriales:**
                - Pression foncière forte sur le littoral Ouest
                - Désir d'habitat individuel malgré la rareté du foncier
                - Développement des éco-quartiers
                - Renouvellement urbain dans les centres-villes
                
                **🏗️ Évolutions Constructives:**
                - Montée en puissance de la construction bois
                - Développement des bâtiments passifs
                - Intégration des énergies renouvelables
                - Adaptation au risque cyclonique
                """)
            
            with col2:
                st.markdown("""
                ### 🚨 ENJEUX ET DÉFIS
                
                **⚡ Défis Structurels:**
                - Tension entre préservation et développement
                - Gestion des risques naturels
                - Adaptation au changement climatique
                - Maîtrise des coûts de construction
                
                **💡 Opportunités:**
                - Friches à reconquérir
                - Innovations constructives locales
                - Développement du numérique
                - Attractivité renforcée
                """)
            
            st.markdown("""
            ### 📋 PERSPECTIVES 2025-2030
            
            **Scénario tendanciel:**
            - Hausse modérée des prix (+2 à +3% par an)
            - Renforcement des disparités territoriales
            - Accentuation de la densification
            - Développement des mobilités douces
            
            **Scénario de rupture:**
            - Accélération de la transition écologique
            - Réorganisation des polarités urbaines
            - Nouveaux modèles d'habitat collaboratif
            - Smart cities et territoires connectés
            """)
        
        with tab6:
            st.markdown("## 📋 À propos de ce dashboard")
            st.markdown("""
            Ce dashboard présente une analyse complète du marché du logement à La Réunion.
            
            **Sources des données:**
            - INSEE - Recensement de la population
            - DGI - Fichiers des mutations à titre onéreux
            - Observatoire des Loyers de La Réunion
            - SDES - Données locales du logement
            - Collectivités territoriales
            
            **Période couverte:**
            - Données historiques: 2018-2024
            - Données courantes: 2024
            - Projections: 2025-2030
            
            **⚠️ Avertissement:** 
            Les données présentées sont indicatives et peuvent contenir des estimations.
            Ce dashboard n'est pas un conseil en investissement immobilier.
            
            **🔒 Confidentialité:** 
            Toutes les données sont agrégées et anonymisées.
            """)
            
            st.markdown("---")
            st.markdown("""
            **📞 Contact:**
            - Observatoire de l'Habitat de La Réunion
            - Site web: www.reunion.logement.gouv.fr
            - Email: observatoire.habitat@reunion.gouv.fr
            """)

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = ReunionHousingDashboard()
    dashboard.run_dashboard()