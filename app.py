"""
APLIKASI ANALISIS SAHAM INDONESIA ULTIMATE
Technical Analysis + Bandarmologi + Broker Summary + Transaction Analysis
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import ta
import json
import os
import time
import random
import warnings
warnings.filterwarnings('ignore')

# Konfigurasi halaman
st.set_page_config(
    page_title="Analisis Saham Indonesia ULTIMATE",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom — kompatibel dark mode & light mode
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #378ADD;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        opacity: 0.7;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .tab-subheader {
        font-size: 1.4rem;
        font-weight: bold;
        margin: 16px 0 10px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(128,128,128,0.3);
    }
    .buy-signal {
        color: #00c853;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .sell-signal {
        color: #ff5252;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .neutral-signal {
        color: #ffd740;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .metric-card {
        background: rgba(55,138,221,0.12);
        border: 1px solid rgba(55,138,221,0.3);
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        margin: 8px 0;
    }
    .metric-card h3 {
        margin: 0;
        font-size: 1.8rem;
        color: #378ADD;
    }
    .accumulation {
        background: rgba(0,200,83,0.15);
        color: #00c853;
        border: 1px solid #00c853;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .distribution {
        background: rgba(255,82,82,0.15);
        color: #ff5252;
        border: 1px solid #ff5252;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .neutral {
        background: rgba(255,215,64,0.15);
        color: #ffd740;
        border: 1px solid #ffd740;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .info-box {
        background: rgba(55,138,221,0.12);
        border-left: 4px solid #378ADD;
        padding: 12px 16px;
        margin: 10px 0;
        border-radius: 0 6px 6px 0;
    }
    .warning-box {
        background: rgba(255,193,7,0.12);
        border-left: 4px solid #ffc107;
        padding: 12px 16px;
        margin: 10px 0;
        border-radius: 0 6px 6px 0;
    }
    .success-box {
        background: rgba(0,200,83,0.12);
        border-left: 4px solid #00c853;
        padding: 12px 16px;
        margin: 10px 0;
        border-radius: 0 6px 6px 0;
    }
    .bandar-card {
        background: rgba(127,119,221,0.12);
        border: 1px solid rgba(127,119,221,0.35);
        padding: 18px;
        border-radius: 12px;
        margin: 10px 0;
    }
    .strategy-box {
        background: rgba(55,138,221,0.10);
        border: 1px solid rgba(55,138,221,0.25);
        padding: 18px;
        border-radius: 10px;
        margin: 8px 0;
    }
    .big-lot {
        color: #ff5252;
        font-weight: bold;
        font-size: 1.1em;
    }
    .broker-card {
        background: rgba(40,167,69,0.10);
        border-left: 4px solid #28a745;
        padding: 12px 16px;
        margin: 5px 0;
        border-radius: 0 6px 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE & KONFIGURASI
# ============================================================================

DATA_FILE = "manual_broker_data.json"

def load_manual_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_manual_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Daftar saham Indonesia (LENGKAP - gabungan semua sumber)
SAHAM_INDONESIA = {
    # === A ===
    'AADI.JK': 'Adaro Andalan Indonesia Tbk.',
    'AALI.JK': 'Astra Agro Lestari Tbk.',
    'ABBA.JK': 'Mahaka Media Tbk.',
    'ABDA.JK': 'Asuransi Bina Dana Arta Tbk.',
    'ABMM.JK': 'ABM Investama Tbk.',
    'ACES.JK': 'Aspirasi Hidup Indonesia Tbk.',
    'ACRO.JK': 'Samcro Hyosung Adilestari Tbk.',
    'ACST.JK': 'Acset Indonusa Tbk.',
    'ADCP.JK': 'Adhi Commuter Properti Tbk.',
    'ADES.JK': 'Akasha Wira International Tbk.',
    'ADHI.JK': 'Adhi Karya (Persero) Tbk.',
    'ADMF.JK': 'Adira Dinamika Multi Finance T',
    'ADMG.JK': 'Polychem Indonesia Tbk.',
    'ADMR.JK': 'Alamtri Minerals Indonesia Tbk.',
    'ADRO.JK': 'Alamtri Resources Indonesia Tb',
    'AEGS.JK': 'Anugerah Spareparts Sejahtera',
    'AGAR.JK': 'Asia Sejahtera Mina Tbk.',
    'AGII.JK': 'Aneka Gas Industri Tbk',
    'AGRO.JK': 'Bank Raya Indonesia Tbk.',
    'AGRS.JK': 'Bank IBK Indonesia Tbk.',
    'AHAP.JK': 'Asuransi Harta Aman Pratama Tb',
    'AIMS.JK': 'Akbar Indo Makmur Stimec Tbk',
    'AISA.JK': 'FKS Food Sejahtera Tbk.',
    'AKKU.JK': 'Anugerah Kagum Karya Utama Tbk.',
    'AKPI.JK': 'Argha Karya Prima Industry Tbk.',
    'AKRA.JK': 'AKR Corporindo Tbk.',
    'AKSI.JK': 'Maming Enam Sembilan Mineral Tbk',
    'ALDO.JK': 'Alkindo Naratama Tbk.',
    'ALII.JK': 'Ancara Logistics Indonesia Tbk.',
    'ALKA.JK': 'Alakasa Industrindo Tbk.',
    'ALMI.JK': 'Alumindo Light Metal Industry Tbk',
    'ALTO.JK': 'Tri Banyan Tirta Tbk.',
    'AMAG.JK': 'Asuransi Multi Artha Guna Tbk.',
    'AMAN.JK': 'Makmur Berkah Amanda Tbk.',
    'AMAR.JK': 'Bank Amar Indonesia Tbk.',
    'AMFG.JK': 'Asahimas Flat Glass Tbk.',
    'AMIN.JK': 'Ateliers Mecaniques D Indonesie Tbk',
    'AMMN.JK': 'Amman Mineral Internasional Tb',
    'AMMS.JK': 'Agung Menjangan Mas Tbk.',
    'AMOR.JK': 'Ashmore Asset Management Indon',
    'AMRT.JK': 'Sumber Alfaria Trijaya Tbk.',
    'ANDI.JK': 'Andira Agro Tbk.',
    'ANJT.JK': 'Austindo Nusantara Jaya Tbk.',
    'ANTM.JK': 'Aneka Tambang Tbk.',
    'ANTO.JK': 'Aneka Tambang Tbk',
    'APEX.JK': 'Apexindo Pratama Duta Tbk.',
    'APIC.JK': 'Pacific Strategic Financial Tbk',
    'APII.JK': 'Arita Prima Indonesia Tbk.',
    'APLI.JK': 'Asiaplast Industries Tbk.',
    'APLN.JK': 'Agung Podomoro Land Tbk.',
    'AQUA.JK': 'Aqua Golden Mississippi',
    'ARCI.JK': 'Archi Indonesia Tbk.',
    'AREA.JK': 'Dunia Virtual Online Tbk.',
    'ARGA.JK': 'Argo Pantes Tbk',
    'ARGO.JK': 'Argo Pantes Tbk.',
    'ARII.JK': 'Atlas Resources Tbk.',
    'ARKA.JK': 'Arkha Jayanti Persada Tbk.',
    'ARKO.JK': 'Arkora Hydro Tbk.',
    'ARMY.JK': 'Armidian Karyatama Tbk.',
    'ARNA.JK': 'Arwana Citramulia Tbk.',
    'ARTA.JK': 'Arthavest Tbk.',
    'ARTI.JK': 'Ratu Prabu Energi Tbk.',
    'ARTO.JK': 'Bank Jago Tbk.',
    'ASBI.JK': 'Asuransi Bintang Tbk.',
    'ASDM.JK': 'Asuransi Dayin Mitra Tbk.',
    'ASGR.JK': 'Astra Graphia Tbk.',
    'ASHA.JK': 'Cilacap Samudera Fishing Indus',
    'ASII.JK': 'Astra International Tbk.',
    'ASJT.JK': 'Asuransi Jasa Tania Tbk.',
    'ASLC.JK': 'Autopedia Sukses Lestari Tbk.',
    'ASLI.JK': 'Asri Karya Lestari Tbk.',
    'ASMI.JK': 'Asuransi Maximus Graha Persada',
    'ASPI.JK': 'Andalan Sakti Primaindo Tbk.',
    'ASPR.JK': 'Asia Pramulia Tbk.',
    'ASRI.JK': 'Alam Sutera Realty Tbk.',
    'ASRM.JK': 'Asuransi Ramayana Tbk.',
    'ASSA.JK': 'Adi Sarana Armada Tbk.',
    'ATAP.JK': 'Trimitra Prawara Goldland Tbk.',
    'ATIC.JK': 'Anabatic Technologies Tbk.',
    'ATLA.JK': 'Atlantis Subsea Indonesia Tbk.',
    'ATPK.JK': 'Perusahaan Perseroan (Persero) Aneka Tambang Tbk',
    'AUST.JK': 'Austin Electric Indonesia Tbk',
    'AUTO.JK': 'Astra Otoparts Tbk.',
    'AVIA.JK': 'Avia Avian Tbk.',
    'AWAN.JK': 'Era Digital Media Tbk.',
    'AXIO.JK': 'Tera Data Indonusa Tbk.',
    'AYAM.JK': 'Janu Putra Sejahtera Tbk.',
    'AYLS.JK': 'Agro Yasa Lestari Tbk.',
    # === B ===
    'BABP.JK': 'Bank MNC Internasional Tbk.',
    'BABY.JK': 'Multitrend Indo Tbk.',
    'BACA.JK': 'Bank Capital Indonesia Tbk.',
    'BAIK.JK': 'Bersama Mencapai Puncak Tbk.',
    'BAJA.JK': 'Saranacentral Bajatama Tbk.',
    'BALI.JK': 'Bali Towerindo Sentra Tbk.',
    'BANK.JK': 'Bank MNC Internasional Tbk',
    'BAPA.JK': 'Bekasi Asri Pemula Tbk.',
    'BAPI.JK': 'Bhakti Agung Propertindo Tbk.',
    'BATA.JK': 'Sepatu Bata Tbk.',
    'BATR.JK': 'Benteng Api Technic Tbk.',
    'BAUT.JK': 'Mitra Angkasa Sejahtera Tbk.',
    'BAYU.JK': 'Bayu Buana Tbk.',
    'BBCA.JK': 'Bank Central Asia Tbk.',
    'BBHI.JK': 'Bank Harda Internasional Tbk',
    'BBKP.JK': 'Bank KB Indonesia Tbk.',
    'BBLD.JK': 'Buana Finance Tbk.',
    'BBMD.JK': 'Bank Mestika Dharma Tbk.',
    'BBMI.JK': 'Bank Bumi Arta Tbk',
    'BBNI.JK': 'Bank Negara Indonesia (Persero',
    'BBRI.JK': 'Bank Rakyat Indonesia (Persero) Tbk',
    'BBRM.JK': 'Pelayaran Nasional Bina Buana Raya Tbk',
    'BBSI.JK': 'Krom Bank Indonesia Tbk.',
    'BBSS.JK': 'Bumi Benowo Sukses Sejahtera T',
    'BBTN.JK': 'Bank Tabungan Negara (Persero) Tbk',
    'BBYB.JK': 'Bank Hibank Indonesia Tbk',
    'BCAP.JK': 'MNC Kapital Indonesia Tbk.',
    'BCIC.JK': 'Bank JTrust Indonesia Tbk.',
    'BCIP.JK': 'Bumi Citra Permai Tbk.',
    'BDKR.JK': 'Berdikari Pondasi Perkasa Tbk.',
    'BDMN.JK': 'Bank Danamon Indonesia Tbk.',
    'BEBS.JK': 'Berkah Beton Sadaya Tbk.',
    'BEEF.JK': 'Estika Tata Tiara Tbk.',
    'BEER.JK': 'Jobubu Jarum Minahasa Tbk.',
    'BEKS.JK': 'Bank Pembangunan Daerah Banten Tbk',
    'BELI.JK': 'Global Digital Niaga Tbk.',
    'BELL.JK': 'Trisula Textile Industries Tbk.',
    'BELS.JK': 'Global Digital Niaga Tbk',
    'BESS.JK': 'Batulicin Nusantara Maritim Tb',
    'BEST.JK': 'Bekasi Fajar Industrial Estate Tbk',
    'BFIN.JK': 'BFI Finance  Indonesia Tbk.',
    'BGTG.JK': 'Bank Ganesha Tbk.',
    'BHAT.JK': 'Bhinneka Life Support Tbk',
    'BHIT.JK': 'MNC Asia Holding Tbk.',
    'BIKA.JK': 'Binakarya Jaya Abadi Tbk.',
    'BIKE.JK': 'Sepeda Bersama Indonesia Tbk.',
    'BIMA.JK': 'Primarindo Asia Infrastructure Tbk',
    'BINA.JK': 'Bank Ina Perdana Tbk.',
    'BINO.JK': 'Perma Plasindo Tbk.',
    'BIPI.JK': 'Astrindo Nusantara Infrastrukt',
    'BIPP.JK': 'Bhuwanatala Indah Permai Tbk.',
    'BIRD.JK': 'Blue Bird Tbk.',
    'BISI.JK': 'BISI International Tbk.',
    'BJBR.JK': 'Bank Pembangunan Daerah Jawa Barat dan Banten Tbk',
    'BJTM.JK': 'Bank Pembangunan Daerah Jawa Timur Tbk',
    'BKDP.JK': 'Bukit Darmo Property Tbk.',
    'BKSL.JK': 'Sentul City Tbk.',
    'BKSW.JK': 'Bank QNB Indonesia Tbk.',
    'BLES.JK': 'Superior Prima Sukses Tbk.',
    'BLOG.JK': 'Trimitra Trans Persada Tbk.',
    'BLTA.JK': 'Berlian Laju Tanker Tbk.',
    'BLTZ.JK': 'Graha Layar Prima Tbk.',
    'BLUE.JK': 'Berkah Prima Perkasa Tbk.',
    'BMAS.JK': 'Bank Maspion Indonesia Tbk.',
    'BMBL.JK': 'Lavender Bina Cendikia Tbk.',
    'BMHS.JK': 'Bundamedik Tbk.',
    'BMRI.JK': 'Bank Mandiri (Persero) Tbk.',
    'BMSR.JK': 'Bintang Mitra Semestaraya Tbk.',
    'BMTR.JK': 'Bumi Serpong Damai Tbk',
    'BNBA.JK': 'Bank Bumi Arta Tbk.',
    'BNBR.JK': 'Bakrie & Brothers Tbk.',
    'BNGA.JK': 'Bank CIMB Niaga Tbk.',
    'BNII.JK': 'Bank Maybank Indonesia Tbk.',
    'BNLI.JK': 'Bank Permata Tbk.',
    'BOAT.JK': 'Newport Marine Services Tbk.',
    'BOBA.JK': 'Formosa Ingredient Factory Tbk.',
    'BOGA.JK': 'Apollo Global Interactive Tbk.',
    'BOLA.JK': 'Bali Bintang Sejahtera Tbk.',
    'BOLT.JK': 'Garuda Metalindo Tbk.',
    'BORN.JK': 'Borneo Lumbung Energy & Metal Tbk',
    'BOSS.JK': 'Borneo Olah Sarana Sukses Tbk.',
    'BPFI.JK': 'Woori Finance Indonesia Tbk.',
    'BPII.JK': 'Bali Penumbral Lestari Raya Tbk',
    'BPTR.JK': 'Batavia Prosperindo Trans Tbk.',
    'BRAM.JK': 'Bramhani Asset Tbk',
    'BREN.JK': 'Barito Renewables Energy Tbk.',
    'BRIS.JK': 'Bank Syariah Indonesia Tbk.',
    'BRMS.JK': 'Bumi Resources Minerals Tbk.',
    'BRNA.JK': 'Berlina Tbk.',
    'BRND.JK': 'Brandzili Tbk',
    'BRNG.JK': 'Baron Nusantara Abadi Tbk',
    'BRPI.JK': 'Papa Alfa Indonesia Tbk',
    'BRPT.JK': 'Barito Pacific Tbk.',
    'BRRC.JK': 'Raja Roti Cemerlang Tbk.',
    'BSBK.JK': 'Wulandari Bangun Laksana Tbk.',
    'BSDE.JK': 'Bumi Serpong Damai Tbk.',
    'BSIM.JK': 'Bank Sinarmas Tbk.',
    'BSML.JK': 'Bisnis Indonesia Mediatama Tbk',
    'BSSR.JK': 'Baramulti Suksessarana Tbk.',
    'BSWD.JK': 'Bank Of India Indonesia Tbk.',
    'BTEK.JK': 'Bumi Teknokultura Unggul Tbk.',
    'BTEL.JK': 'Bakrie Telecom Tbk.',
    'BTON.JK': 'Betonjaya Manunggal Tbk.',
    'BTPN.JK': 'Bank SMBC Indonesia Tbk.',
    'BTPS.JK': 'Bank BTPN Syariah Tbk.',
    'BUAH.JK': 'Alamandara Buanalestari Tbk',
    'BUDI.JK': 'Budi Starch & Sweetener Tbk.',
    'BUKA.JK': 'Bukalapak.com Tbk.',
    'BUKK.JK': 'Bukaka Teknik Utama Tbk.',
    'BULL.JK': 'Buana Lintas Lautan Tbk.',
    'BUMI.JK': 'Bumi Resources Tbk.',
    'BUVA.JK': 'Bukit Uluwatu Villa Tbk.',
    'BVIC.JK': 'Bank Victoria International Tbk',
    'BWFG.JK': 'Bank Woori Saudara Indonesia 1906 Tbk',
    'BWPT.JK': 'Eagle High Plantations Tbk.',
    'BYAN.JK': 'Bayan Resources Tbk.',
    # === C ===
    'CAKK.JK': 'Cahayaputra Asa Keramik Tbk.',
    'CAMP.JK': 'Campina Ice Cream Industry Tbk.',
    'CANI.JK': 'Capitol Nusantara Indonesia Tbk',
    'CARE.JK': 'Metro Healthcare Indonesia Tbk.',
    'CARS.JK': 'Industri dan Perdagangan Bintr',
    'CASA.JK': 'Capital Financial Indonesia Tb',
    'CASH.JK': 'Cashlez Worldwide Indonesia Tbk',
    'CASS.JK': 'Cahaya Aero Services Tbk.',
    'CATS.JK': 'Citra Tubindo Tbk',
    'CBDK.JK': 'Bangun Kosambi Sukses Tbk.',
    'CBMF.JK': 'Cahaya Bintang Medan Tbk.',
    'CBPE.JK': 'Citra Buana Prasida Tbk.',
    'CBRE.JK': 'Cakra Buana Resources Energi T',
    'CBUT.JK': 'Citra Borneo Utama Tbk.',
    'CCSI.JK': 'Communication Cable Systems Indonesia Tbk',
    'CDIA.JK': 'Chandra Daya Investasi Tbk.',
    'CEKA.JK': 'Wilmar Cahaya Indonesia Tbk.',
    'CENT.JK': 'Centratama Telekomunikasi Indonesia Tbk',
    'CEPU.JK': 'Citra Putra Kebun Nusantara Tbk',
    'CFIN.JK': 'Clipan Finance Indonesia Tbk.',
    'CGAS.JK': 'Citra Nusantara Gemilang Tbk.',
    'CHEK.JK': 'Diastika Biotekindo Tbk.',
    'CHEM.JK': 'Chemstar Indonesia Tbk.',
    'CHIP.JK': 'Pelita Teknologi Global Tbk.',
    'CINT.JK': 'Chitose Internasional Tbk.',
    'CITA.JK': 'Cita Mineral Investindo Tbk.',
    'CITY.JK': 'Natura City Developments Tbk.',
    'CLAY.JK': 'Citra Putra Realty Tbk.',
    'CLEO.JK': 'Sariguna Primatirta Tbk.',
    'CLPI.JK': 'Colorpak Indonesia Tbk.',
    'CMNP.JK': 'Citra Marga Nusaphala Persada Tbk',
    'CMNT.JK': 'Cemindo Gemilang Tbk.',
    'CMPI.JK': 'Citra Multimedia Indonesia Tbk',
    'CMPP.JK': 'AirAsia Indonesia Tbk.',
    'CMRY.JK': 'Cisarua Mountain Dairy Tbk.',
    'CNKO.JK': 'Exploitasi Energi Indonesia Tbk',
    'CNMA.JK': 'Nusantara Sejahtera Raya Tbk.',
    'CNTX.JK': 'Century Textile Industry Tbk.',
    'COAL.JK': 'Black Diamond Resources Tbk.',
    'COCO.JK': 'Wahana Interfood Nusantara Tbk.',
    'COIN.JK': 'Indokripto Koin Semesta Tbk.',
    'COWL.JK': 'Cowell Development Tbk.',
    'CPIN.JK': 'Charoen Pokphand Indonesia Tbk.',
    'CPRI.JK': 'Capri Nusa Satu Properti Tbk.',
    'CPRO.JK': 'Central Proteina Prima Tbk.',
    'CRAB.JK': 'Toba Surimi Industries Tbk.',
    'CRSN.JK': 'Carsurin Tbk.',
    'CSAP.JK': 'Catur Sentosa Adiprana Tbk.',
    'CSIS.JK': 'Cahayasakti Investindo Sukses Tbk',
    'CSMI.JK': 'Cipta Selera Murni Tbk.',
    'CSRA.JK': 'Cisadane Sawit Raya Tbk.',
    'CTBN.JK': 'Citra Tubindo Tbk.',
    'CTRA.JK': 'Ciputra Development Tbk.',
    'CTTH.JK': 'Citatah Tbk.',
    'CUAN.JK': 'Petrindo Jaya Kreasi Tbk.',
    'CYBR.JK': 'ITSEC Asia Tbk.',
    # === D ===
    'DAAZ.JK': 'Daaz Bara Lestari Tbk.',
    'DADA.JK': 'Diamond Citra Propertindo Tbk.',
    'DART.JK': 'Duta Anggada Realty Tbk.',
    'DATA.JK': 'Remala Abadi Tbk.',
    'DAYA.JK': 'Duta Intidaya Tbk.',
    'DCII.JK': 'DCI Indonesia Tbk.',
    'DEAL.JK': 'Dewata Freightinternational Tbk',
    'DEFI.JK': 'Danasupra Erapacific Tbk.',
    'DEPO.JK': 'Caturkarda Depo Bangunan Tbk.',
    'DEWA.JK': 'Darma Henwa Tbk.',
    'DEWI.JK': 'Dewi Shri Farmindo Tbk.',
    'DFAM.JK': 'Dafam Property Indonesia Tbk.',
    'DGIK.JK': 'Nusa Konstruksi Enjiniring Tbk.',
    'DGNS.JK': 'Diagnos Laboratorium Utama Tbk.',
    'DGWG.JK': 'Delta Giri Wacana Tbk.',
    'DIGI.JK': 'Arkadia Digital Media Tbk.',
    'DILD.JK': 'Intiland Development Tbk.',
    'DIVA.JK': 'Distribusi Voucher Nusantara Tbk',
    'DKFT.JK': 'Central Omega Resources Tbk.',
    'DKHH.JK': 'Cipta Sarana Medika Tbk.',
    'DLTA.JK': 'Delta Djakarta Tbk.',
    'DMAS.JK': 'Puradelta Lestari Tbk.',
    'DMMX.JK': 'Digital Mediatama Maxima Tbk.',
    'DMND.JK': 'Diamond Food Indonesia Tbk.',
    'DNAR.JK': 'Bank Oke Indonesia Tbk.',
    'DNET.JK': 'Indoritel Makmur Internasional',
    'DOID.JK': 'BUMA Internasional Grup Tbk.',
    'DOOH.JK': 'Era Media Sejahtera Tbk.',
    'DOSS.JK': 'Global Sukses Digital Tbk.',
    'DPNS.JK': 'Duta Pertiwi Nusantara Tbk.',
    'DPUM.JK': 'Dua Putra Utama Makmur Tbk.',
    'DRMA.JK': 'Dharma Polimetal Tbk.',
    'DSFI.JK': 'Dharma Samudera Fishing Industries Tbk',
    'DSNG.JK': 'Dharma Satya Nusantara Tbk.',
    'DSSA.JK': 'Dian Swastatika Sentosa Tbk.',
    'DUCK.JK': 'Jaya Bersama Indo Tbk.',
    'DUTI.JK': 'Duta Pertiwi Tbk.',
    'DVLA.JK': 'Darya-Varia Laboratoria Tbk.',
    'DWGL.JK': 'Dwi Guna Laksana Tbk.',
    'DYAN.JK': 'Dyandra Media International Tbk',
    # === E ===
    'EAST.JK': 'Eastparc Hotel Tbk.',
    'ECII.JK': 'Electronic City Indonesia Tbk.',
    'EDGE.JK': 'Indointernet Tbk.',
    'EKAD.JK': 'Ekadharma International Tbk.',
    'ELIT.JK': 'Data Sinergitama Jaya Tbk.',
    'ELPI.JK': 'Pelayaran Nasional Ekalya Purn',
    'ELSA.JK': 'Elnusa Tbk.',
    'ELTY.JK': 'Bakrieland Development Tbk.',
    'EMAS.JK': 'Merdeka Gold Resources Tbk.',
    'EMDE.JK': 'Megapolitan Developments Tbk.',
    'EMTK.JK': 'Elang Mahkota Teknologi Tbk.',
    'ENAK.JK': 'Champ Resto Indonesia Tbk.',
    'ENRG.JK': 'Energi Mega Persada Tbk.',
    'ENVY.JK': 'Envy Technologies Indonesia Tbk',
    'ENZO.JK': 'Morenzo Abadi Perkasa Tbk.',
    'EPAC.JK': 'Megalestari Epack Sentosaraya',
    'EPMT.JK': 'Enseval Putera Megatrading Tbk.',
    'ERAA.JK': 'Erajaya Swasembada Tbk.',
    'ERAL.JK': 'Sinar Eka Selaras Tbk.',
    'ERTX.JK': 'Eratex Djaja Tbk.',
    'ESIP.JK': 'Sinergi Inti Plastindo Tbk.',
    'ESSA.JK': 'ESSA Industries Indonesia Tbk.',
    'ESTA.JK': 'Esta Multi Usaha Tbk.',
    'ESTI.JK': 'Esta Multi Usaha Tbk',
    'ETWA.JK': 'Eterindo Wahanatama Tbk.',
    'EURO.JK': 'Estee Gold Feet Tbk.',
    'EXCL.JK': 'XLSMART Telecom Sejahtera Tbk.',
    # === F ===
    'FAPA.JK': 'FAP Agri Tbk.',
    'FAST.JK': 'Fast Food Indonesia Tbk.',
    'FASW.JK': 'Fajar Surya Wisesa Tbk.',
    'FILM.JK': 'MD Entertainment Tbk.',
    'FIMP.JK': 'Fimperkasa Utama Tbk.',
    'FIRE.JK': 'Alfa Energi Investama Tbk.',
    'FISH.JK': 'FKS Multi Agro Tbk.',
    'FITT.JK': 'Hotel Fitra International Tbk.',
    'FLMC.JK': 'Falmaco Nonwoven Industri Tbk.',
    'FMII.JK': 'Fortune Mate Indonesia Tbk.',
    'FOLK.JK': 'Multi Garam Utama Tbk.',
    'FOOD.JK': 'Sentra Food Indonesia Tbk.',
    'FORE.JK': 'Fore Kopi Indonesia Tbk.',
    'FORU.JK': 'Fortune Indonesia Tbk.',
    'FORZ.JK': 'Forza Land Indonesia Tbk',
    'FPNI.JK': 'Lotte Chemical Titan Nusantara Tbk',
    'FREN.JK': 'Smartfren Telecom Tbk',
    'FUJI.JK': 'Fuji Finance Indonesia Tbk.',
    'FUTR.JK': 'Futura Energi Global Tbk.',
    'FWCT.JK': 'Wijaya Cahaya Timber Tbk.',
    # === G ===
    'GAMA.JK': 'Aksara Global Development Tbk.',
    'GDST.JK': 'Gunawan Dianjaya Steel Tbk.',
    'GDYR.JK': 'Goodyear Indonesia Tbk.',
    'GEMA.JK': 'Gema Grahasarana Tbk.',
    'GEMS.JK': 'Golden Energy Mines Tbk.',
    'GGRM.JK': 'Gudang Garam Tbk.',
    'GGRP.JK': 'Gunung Raja Paksi Tbk.',
    'GHON.JK': 'Gihon Telekomunikasi Indonesia Tbk',
    'GIAA.JK': 'Garuda Indonesia (Persero) Tbk.',
    'GJTL.JK': 'Gajah Tunggal Tbk.',
    'GLOB.JK': 'Globe Kita Terang Tbk.',
    'GLVA.JK': 'Galva Technologies Tbk.',
    'GMFI.JK': 'Garuda Maintenance Facility Aero Asia Tbk',
    'GMTD.JK': 'Gowa Makassar Tourism Development Tbk',
    'GOLD.JK': 'Visi Telekomunikasi Indonesia Tbk',
    'GOLF.JK': 'Intra Golflink Resorts Tbk.',
    'GOLL.JK': 'Golden Plantation Tbk.',
    'GOOD.JK': 'Garudafood Putra Putri Jaya Tb',
    'GOTO.JK': 'GoTo Gojek Tokopedia Tbk.',
    'GPRA.JK': 'Perdana Gapuraprima Tbk.',
    'GPSO.JK': 'Geoprima Solusi Tbk.',
    'GRIA.JK': 'Ingria Pratama Capitalindo Tbk.',
    'GRPH.JK': 'Griptha Putra Persada Tbk.',
    'GRPM.JK': 'Graha Prima Mentari Tbk.',
    'GSMF.JK': 'Equity Development Investment Tbk',
    'GTBO.JK': 'Garda Tujuh Buana Tbk.',
    'GTRA.JK': 'Grahaprima Suksesmandiri Tbk.',
    'GTSI.JK': 'GTS Internasional Tbk.',
    'GULA.JK': 'Aman Agrindo Tbk.',
    'GUNA.JK': 'Gunanusa Eramandiri Tbk.',
    'GWSA.JK': 'Greenwood Sejahtera Tbk.',
    'GZCO.JK': 'Gozco Plantations Tbk.',
    # === H ===
    'HADE.JK': 'Himalaya Energi Perkasa Tbk.',
    'HAIS.JK': 'Hasnur Internasional Shipping',
    'HAJJ.JK': 'Arsy Buana Travelindo Tbk.',
    'HALO.JK': 'Haloni Jane Tbk.',
    'HATM.JK': 'Habco Trans Maritima Tbk.',
    'HBAT.JK': 'Minahasa Membangun Hebat Tbk.',
    'HDFA.JK': 'Radana Bhaskara Finance Tbk.',
    'HDIT.JK': 'Hensel Davest Indonesia Tbk.',
    'HEAL.JK': 'Medikaloka Hermina Tbk.',
    'HELI.JK': 'Jaya Trishindo Tbk.',
    'HERO.JK': 'DFI Retail Nusantara Tbk.',
    'HEXA.JK': 'Hexindo Adiperkasa Tbk.',
    'HGII.JK': 'Hero Global Investment Tbk.',
    'HILL.JK': 'Hillcon Tbk.',
    'HITS.JK': 'Humpuss Intermoda Transportasi Tbk',
    'HKMU.JK': 'Hakim Putra Karya Tbk',
    'HMSP.JK': 'H.M. Sampoerna Tbk.',
    'HOKI.JK': 'Buyung Poetra Sembada Tbk.',
    'HOME.JK': 'Hotel Mandarine Regency Tbk.',
    'HOMI.JK': 'Grand House Mulia Tbk.',
    'HOPE.JK': 'Harapan Duta Pertiwi Tbk.',
    'HOTL.JK': 'Saraswati Griya Lestari Tbk.',
    'HRME.JK': 'Menteng Heritage Realty Tbk.',
    'HRTA.JK': 'Hartadinata Abadi Tbk.',
    'HRUM.JK': 'Harum Energy Tbk.',
    'HUMI.JK': 'Humpuss Maritim Internasional',
    'HYGN.JK': 'Ecocare Indo Pasifik Tbk.',
    # === I ===
    'IATA.JK': 'MNC Energy Investments Tbk.',
    'IBFN.JK': 'Intan Baru Prana Tbk.',
    'IBOS.JK': 'Indo Boga Sukses Tbk.',
    'IBST.JK': 'Inti Bangun Sejahtera Tbk.',
    'ICBP.JK': 'Indofood CBP Sukses Makmur Tbk.',
    'ICON.JK': 'Island Concepts Indonesia Tbk.',
    'IDEA.JK': 'Idea Indonesia Akademi Tbk.',
    'IDPR.JK': 'Indonesia Pondasi Raya Tbk.',
    'IFII.JK': 'Indonesia Fibreboard Industry Tbk',
    'IFSH.JK': 'Ifishdeco Tbk.',
    'IGAR.JK': 'Champion Pacific Indonesia Tbk.',
    'IIKP.JK': 'Inti Agri Resources Tbk.',
    'IKAI.JK': 'Intikeramik Alamasri Industri Tbk',
    'IKAN.JK': 'Era Mandiri Cemerlang Tbk.',
    'IKBI.JK': 'Sumi Indo Kabel Tbk.',
    'IKPM.JK': 'Ikapharmindo Putramas Tbk.',
    'IMAS.JK': 'Indomobil Sukses Internasional Tbk',
    'IMJS.JK': 'Indomobil Multi Jasa Tbk.',
    'IMPC.JK': 'Impack Pratama Industri Tbk.',
    'INAF.JK': 'Indofarma Tbk.',
    'INAI.JK': 'Indal Aluminium Industry Tbk.',
    'INCF.JK': 'Indo Komoditi Korpora Tbk.',
    'INCI.JK': 'Intanwijaya Internasional Tbk.',
    'INCO.JK': 'Vale Indonesia Tbk.',
    'INDF.JK': 'Indofood Sukses Makmur Tbk.',
    'INDO.JK': 'Royalindo Investa Wijaya Tbk.',
    'INDR.JK': 'Indo-Rama Synthetics Tbk.',
    'INDS.JK': 'Indospring Tbk.',
    'INDX.JK': 'Tanah Laut Tbk.',
    'INDY.JK': 'Indika Energy Tbk.',
    'INET.JK': 'Sinergi Inti Andalan Prima Tbk.',
    'INKP.JK': 'Indah Kiat Pulp & Paper Tbk.',
    'INOV.JK': 'Inocycle Technology Group Tbk.',
    'INPC.JK': 'Bank Artha Graha Internasional Tbk',
    'INPP.JK': 'Indonesian Paradise Property Tbk',
    'INPS.JK': 'Indah Prakasa Sentosa Tbk.',
    'INRU.JK': 'Toba Pulp Lestari Tbk.',
    'INTA.JK': 'Intraco Penta Tbk.',
    'INTD.JK': 'Inter Delta Tbk.',
    'INTP.JK': 'Indocement Tunggal Prakarsa Tbk',
    'IOTF.JK': 'Sumber Sinergi Makmur Tbk.',
    'IPAC.JK': 'Era Graharealty Tbk.',
    'IPCC.JK': 'Indonesia Kendaraan Terminal Tbk',
    'IPCM.JK': 'Jasa Armada Indonesia Tbk.',
    'IPOL.JK': 'Indopoly Swakarsa Industry Tbk.',
    'IPPE.JK': 'Indo Pureco Pratama Tbk.',
    'IPTV.JK': 'MNC Vision Networks Tbk.',
    'IRRA.JK': 'Itama Ranoraya Tbk.',
    'IRSX.JK': 'Folago Global Nusantara Tbk.',
    'ISAP.JK': 'Isra Presisi Indonesia Tbk.',
    'ISAT.JK': 'Indosat Ooredoo Hutchison Tbk',
    'ISEA.JK': 'Indo American Seafoods Tbk.',
    'ISSP.JK': 'Steel Pipe Industry of Indonesia Tbk',
    'ITIC.JK': 'Indonesian Tobacco Tbk.',
    'ITMA.JK': 'Sumber Energi Andalan Tbk.',
    'ITMG.JK': 'Indo Tambangraya Megah Tbk.',
    # === J ===
    'JARR.JK': 'Jhonlin Agro Raya Tbk.',
    'JAST.JK': 'Jasnita Telekomindo Tbk.',
    'JATI.JK': 'Informasi Teknologi Indonesia',
    'JAWA.JK': 'Jaya Agra Wattie Tbk.',
    'JAYA.JK': 'Armada Berjaya Trans Tbk.',
    'JECC.JK': 'Jembo Cable Company Tbk.',
    'JGLE.JK': 'Graha Andrasentra Propertindo',
    'JIHD.JK': 'Jakarta International Hotels & Development Tbk',
    'JKON.JK': 'Jaya Konstruksi Manggala Pratama Tbk',
    'JMAS.JK': 'Asuransi Jiwa Syariah Jasa Mitra Abadi Tbk',
    'JPFA.JK': 'Japfa Comfeed Indonesia Tbk.',
    'JRPT.JK': 'Jaya Real Property Tbk.',
    'JSKY.JK': 'Sky Energy Indonesia Tbk.',
    'JSMR.JK': 'Jasa Marga (Persero) Tbk.',
    'JSPT.JK': 'Jakarta Setiabudi Internasional Tbk',
    'JTPE.JK': 'Jasuindo Tiga Perkasa Tbk.',
    # === K ===
    'KAEF.JK': 'Kimia Farma Tbk.',
    'KAQI.JK': 'Jantra Grupo Indonesia Tbk.',
    'KARW.JK': 'Meratus Jasa Prima Tbk.',
    'KAYU.JK': 'Darmi Bersaudara Tbk.',
    'KBAG.JK': 'Karya Bersama Anugerah Tbk.',
    'KBLI.JK': 'KMI Wire and Cable Tbk',
    'KBLM.JK': 'Kabelindo Murni Tbk.',
    'KBLV.JK': 'First Media Tbk.',
    'KBRI.JK': 'Kertas Basuki Rachmat Indonesia Tbk',
    'KDSI.JK': 'Kedawung Setia Industrial Tbk.',
    'KDTN.JK': 'Puri Sentul Permai Tbk.',
    'KEEN.JK': 'Kencana Energi Lestari Tbk.',
    'KEJU.JK': 'Mulia Boga Raya Tbk.',
    'KETR.JK': 'Ketrosden Triasmitra Tbk.',
    'KIAS.JK': 'Keramika Indonesia Assosiasi Tbk',
    'KICI.JK': 'Kedaung Indah Can Tbk.',
    'KIJA.JK': 'Kawasan Industri Jababeka Tbk.',
    'KING.JK': 'Hoffmen Cleanindo Tbk.',
    'KINO.JK': 'Kino Indonesia Tbk.',
    'KIOS.JK': 'Kioson Komersial Indonesia Tbk.',
    'KJEN.JK': 'Krida Jaringan Nusantara Tbk.',
    'KKES.JK': 'Kusuma Kemindo Sentosa Tbk.',
    'KKGI.JK': 'Resource Alam Indonesia Tbk.',
    'KLAS.JK': 'Pelayaran Kurnia Lautan Semest',
    'KLBF.JK': 'Kalbe Farma Tbk.',
    'KLIN.JK': 'Klinko Karya Imaji Tbk.',
    'KMDS.JK': 'Kurniamitra Duta Sentosa Tbk.',
    'KMTR.JK': 'Kirana Megatara Tbk.',
    'KOBX.JK': 'Kobexindo Tractors Tbk.',
    'KOCI.JK': 'Kokoh Exa Nusantara Tbk.',
    'KOIN.JK': 'Kokoh Inti Arebama Tbk.',
    'KOKA.JK': 'Koka Indonesia Tbk.',
    'KONI.JK': 'Perdana Bangun Pusaka Tbk.',
    'KOPI.JK': 'Excelitas Technologies Tbk',
    'KOTA.JK': 'DMS Propertindo Tbk.',
    'KPAL.JK': 'Steadfast Marine Tbk',
    'KPAS.JK': 'Cottonindo Ariesta Tbk',
    'KPIG.JK': 'MNC Tourism Indonesia Tbk.',
    'KRAH.JK': 'Grand Kartech Tbk',
    'KRAS.JK': 'Krakatau Steel (Persero) Tbk.',
    'KREN.JK': 'Quantum Clovera Investama Tbk.',
    'KRYA.JK': 'Bangun Karya Perkasa Jaya Tbk.',
    'KSIX.JK': 'Kentanix Supra International T',
    'KUAS.JK': 'Ace Oldfields Tbk.',
    # === L ===
    'LABA.JK': 'Ladangbaja Nusantara Tbk',
    'LABI.JK': 'Multi Labora Utama Tbk',
    'LABS.JK': 'UBC Medical Indonesia Tbk.',
    'LAJU.JK': 'Jasa Berdikari Logistics Tbk.',
    'LAND.JK': 'Trimitra Propertindo Tbk.',
    'LAPD.JK': 'Leyand International Tbk.',
    'LCGP.JK': 'Eureka Prima Jakarta Tbk.',
    'LCKM.JK': 'LCK Global Kedaton Tbk.',
    'LEAD.JK': 'Logisticsplus International Tbk',
    'LFLO.JK': 'Imago Mulia Persada Tbk.',
    'LIFE.JK': 'MSIG Life Insurance Indonesia',
    'LINK.JK': 'Link Net Tbk.',
    'LION.JK': 'Lion Metal Works Tbk.',
    'LIVE.JK': 'Homeco Victoria Makmur Tbk.',
    'LMAS.JK': 'Limas Indonesia Makmur Tbk.',
    'LMAX.JK': 'Lupromax Pelumas Indonesia Tbk.',
    'LMPI.JK': 'Langgeng Makmur Industri Tbk.',
    'LMSH.JK': 'Lionmesh Prima Tbk.',
    'LOPI.JK': 'Logisticsplus International Tb',
    'LPCK.JK': 'Lippo Cikarang Tbk.',
    'LPGI.JK': 'Lippo General Insurance Tbk.',
    'LPIN.JK': 'Multi Prima Sejahtera Tbk.',
    'LPKR.JK': 'Lippo Karawaci Tbk.',
    'LPLI.JK': 'Star Pacific Tbk.',
    'LPPF.JK': 'Matahari Department Store Tbk.',
    'LPPS.JK': 'Lenox Pasifik Investama Tbk.',
    'LRNA.JK': 'Eka Sari Lorena Transport Tbk.',
    'LSIP.JK': 'PP London Sumatra Indonesia Tb',
    'LTLS.JK': 'Lautan Luas Tbk.',
    'LUCK.JK': 'Sentral Mitra Informatika Tbk.',
    'LUCY.JK': 'Lima Dua Lima Tiga Tbk.',
    # === M ===
    'MABA.JK': 'Marga Abhinaya Abadi Tbk.',
    'MAGP.JK': 'Multi Agro Gemilang Plantation Tbk',
    'MAHA.JK': 'Mandiri Herindo Adiperkasa Tbk.',
    'MAIN.JK': 'Malindo Feedmill Tbk.',
    'MAMI.JK': 'Mas Murni Indonesia Tbk',
    'MANG.JK': 'Manggung Polahraya Tbk.',
    'MAPA.JK': 'Map Aktif Adiperkasa Tbk.',
    'MAPB.JK': 'MAP Boga Adiperkasa Tbk.',
    'MAPI.JK': 'Mitra Adiperkasa Tbk.',
    'MARI.JK': 'Mahaka Radio Integra Tbk.',
    'MARK.JK': 'Mark Dynamics Indonesia Tbk.',
    'MASA.JK': 'Multistrada Arah Sarana Tbk',
    'MASB.JK': 'Bank Multiarta Sentosa Tbk.',
    'MAXI.JK': 'Maxindo Karya Anugerah Tbk.',
    'MAYA.JK': 'Bank Mayapada Internasional Tbk',
    'MBAP.JK': 'Mitrabara Adiperdana Tbk.',
    'MBMA.JK': 'Merdeka Battery Materials Tbk.',
    'MBSS.JK': 'Mitrabahtera Segara Sejati Tbk.',
    'MBTO.JK': 'Martina Berto Tbk.',
    'MCAS.JK': 'M Cash Integrasi Tbk.',
    'MCOL.JK': 'Prima Andalan Mandiri Tbk.',
    'MCOR.JK': 'Bank China Construction Bank I',
    'MDIA.JK': 'Intermedia Capital Tbk.',
    'MDIY.JK': 'Daya Intiguna Yasa Tbk.',
    'MDKA.JK': 'Merdeka Copper Gold Tbk.',
    'MDKI.JK': 'Emdeki Utama Tbk.',
    'MDLA.JK': 'Medela Potentia Tbk.',
    'MDLN.JK': 'Modernland Realty Tbk.',
    'MDRN.JK': 'Modern Internasional Tbk.',
    'MEDC.JK': 'Medco Energi Internasional Tbk.',
    'MEDS.JK': 'Hetzer Medical Indonesia Tbk.',
    'MEGA.JK': 'Bank Mega Tbk.',
    'MEJA.JK': 'Harta Djaya Karya Tbk.',
    'MENN.JK': 'Menn Teknologi Indonesia Tbk.',
    'MERI.JK': 'Merry Riana Edukasi Tbk.',
    'MERK.JK': 'Merck Tbk.',
    'META.JK': 'Nusantara Infrastructure Tbk.',
    'MFIN.JK': 'Mandala Multifinance Tbk',
    'MFMI.JK': 'Multifiling Mitra Indonesia Tbk',
    'MGLV.JK': 'Panca Anugrah Wisesa Tbk.',
    'MGNA.JK': 'Magna Investama Mandiri Tbk.',
    'MGRO.JK': 'Mahkota Group Tbk.',
    'MHKI.JK': 'Multi Hanna Kreasindo Tbk.',
    'MICE.JK': 'Multi Indocitra Tbk.',
    'MIDI.JK': 'Midi Utama Indonesia Tbk.',
    'MIKA.JK': 'Mitra Keluarga Karyasehat Tbk.',
    'MINA.JK': 'Sanurhasta Mitra Tbk.',
    'MINE.JK': 'Sinar Terang Mandiri Tbk.',
    'MIRA.JK': 'Mitra International Resources Tbk',
    'MITI.JK': 'Mitra Investindo Tbk.',
    'MKAP.JK': 'Multikarya Asia Pasifik Raya T',
    'MKNT.JK': 'Mitra Komunikasi Nusantara Tbk.',
    'MKPI.JK': 'Metropolitan Kentjana Tbk.',
    'MKTR.JK': 'Menthobi Karyatama Raya Tbk.',
    'MLBI.JK': 'Multi Bintang Indonesia Tbk.',
    'MLIA.JK': 'Mulia Industrindo Tbk.',
    'MLPL.JK': 'Mega Perintis Tbk',
    'MLPT.JK': 'Multipolar Technology Tbk.',
    'MMIX.JK': 'Multi Medika Internasional Tbk.',
    'MMLP.JK': 'Mega Manunggal Property Tbk.',
    'MNCN.JK': 'Media Nusantara Citra Tbk.',
    'MOLI.JK': 'Madusari Murni Indah Tbk.',
    'MORA.JK': 'Mora Telematika Indonesia Tbk.',
    'MPIX.JK': 'Mitra Pedagang Indonesia Tbk.',
    'MPMX.JK': 'Mitra Pinasthika Mustika Tbk.',
    'MPOW.JK': 'Megapower Makmur Tbk.',
    'MPPA.JK': 'Matahari Putra Prima Tbk.',
    'MPRO.JK': 'Maha Properti Indonesia Tbk.',
    'MPXL.JK': 'MPX Logistics International Tb',
    'MRAT.JK': 'Mustika Ratu Tbk.',
    'MREI.JK': 'Maskapai Reasuransi Indonesia Tbk',
    'MSIE.JK': 'Multisarana Intan Eduka Tbk.',
    'MSIN.JK': 'MNC Digital Entertainment Tbk.',
    'MSJA.JK': 'Multi Spunindo Jaya Tbk.',
    'MSKY.JK': 'MNC Sky Vision Tbk.',
    'MSTI.JK': 'Mastersystem Infotama Tbk.',
    'MTDL.JK': 'Metrodata Electronics Tbk.',
    'MTEL.JK': 'Dayamitra Telekomunikasi Tbk.',
    'MTFN.JK': 'Capitalinc Investment Tbk.',
    'MTLA.JK': 'Metropolitan Land Tbk.',
    'MTMH.JK': 'Murni Sadar Tbk.',
    'MTPS.JK': 'Meta Epsi Tbk.',
    'MTRA.JK': 'Mitra Adiperkasa Tbk',
    'MTSM.JK': 'Metro Realty Tbk.',
    'MTWI.JK': 'Malacca Trust Wuwungan Insuran',
    'MUTU.JK': 'Mutuagung Lestari Tbk.',
    'MYOH.JK': 'Samindo Resources Tbk.',
    'MYOR.JK': 'Mayora Indah Tbk.',
    'MYTX.JK': 'Asia Pacific Investama Tbk.',
    # === N ===
    'NAIK.JK': 'Adiwarna Anugerah Abadi Tbk.',
    'NANO.JK': 'Nanotech Indonesia Global Tbk.',
    'NASA.JK': 'Andalan Perkasa Abadi Tbk.',
    'NASI.JK': 'Pengembangan Usaha Nasional Tbk',
    'NATO.JK': 'Olympus Strategic Indonesia Tb',
    'NAYZ.JK': 'Hassana Boga Sejahtera Tbk.',
    'NCKL.JK': 'Trimegah Bangun Persada Tbk.',
    'NELY.JK': 'Pelayaran Nelly Dwi Putri Tbk.',
    'NEST.JK': 'Esta Indonesia Tbk.',
    'NETV.JK': 'MDTV Media Technologies Tbk.',
    'NFCX.JK': 'NFC Indonesia Tbk.',
    'NICE.JK': 'Adhi Kartiko Pratama Tbk.',
    'NICK.JK': 'Charnic Capital Tbk.',
    'NICL.JK': 'PAM Mineral Tbk.',
    'NIKL.JK': 'Pelat Timah Nusantara Tbk.',
    'NINE.JK': 'Techno9 Indonesia Tbk.',
    'NIPS.JK': 'Nipress Tbk',
    'NIRO.JK': 'City Retail Developments Tbk.',
    'NISP.JK': 'Bank OCBC NISP Tbk.',
    'NOBU.JK': 'Bank Nationalnobu Tbk.',
    'NPGF.JK': 'Nusa Palapa Gemilang Tbk.',
    'NRCA.JK': 'Nusa Raya Cipta Tbk.',
    'NSSS.JK': 'Nusantara Sawit Sejahtera Tbk.',
    'NTBK.JK': 'Nusantara Inti Corpora Tbk',
    'NUSA.JK': 'Sinergi Megah Internusa Tbk.',
    'NZIA.JK': 'Nusantara Almazia Tbk.',
    # === O ===
    'OASA.JK': 'Maharaksa Biru Energi Tbk.',
    'OBAT.JK': 'Brigit Biofarmaka Teknologi Tb',
    'OBMD.JK': 'OBM Drilchem Tbk.',
    'OCAP.JK': 'MNC Kapital Indonesia Tbk',
    'OILS.JK': 'Indo Oil Perkasa Tbk.',
    'OKAS.JK': 'Ancora Indonesia Resources Tbk.',
    'OLIV.JK': 'Oscar Mitra Sukses Sejahtera T',
    'OMED.JK': 'Jayamas Medica Industri Tbk.',
    'OMRE.JK': 'Indonesia Prima Property Tbk.',
    'OPMS.JK': 'Optima Prima Metal Sinergi Tbk.',
    # === P ===
    'PACK.JK': 'Abadi Nusantara Hijau Investam',
    'PADA.JK': 'Personel Alih Daya Tbk.',
    'PADI.JK': 'Minna Padi Investama Sekuritas Tbk',
    'PALM.JK': 'Provident Investasi Bersama Tb',
    'PAMG.JK': 'Bima Sakti Pertiwi Tbk.',
    'PANI.JK': 'Pratama Abadi Nusa Industri Tbk',
    'PANR.JK': 'Panorama Sentrawisata Tbk.',
    'PANS.JK': 'Panin Sekuritas Tbk.',
    'PART.JK': 'Cipta Perdana Lancar Tbk.',
    'PBID.JK': 'Panca Budi Idaman Tbk.',
    'PBRX.JK': 'Pan Brothers Tbk.',
    'PBSA.JK': 'Paramita Bangun Sarana Tbk.',
    'PCAR.JK': 'Prima Cakrawala Abadi Tbk.',
    'PDES.JK': 'Destinasi Tirta Nusantara Tbk.',
    'PDPP.JK': 'Primadaya Plastisindo Tbk.',
    'PEGE.JK': 'Panca Global Securities Tbk',
    'PEHA.JK': 'Phapros Tbk.',
    'PEVE.JK': 'Penta Valent Tbk.',
    'PGAS.JK': 'Perusahaan Gas Negara (Persero) Tbk',
    'PGEO.JK': 'Pertamina Geothermal Energy Tbk',
    'PGJO.JK': 'Tourindo Guide Indonesia Tbk',
    'PGLI.JK': 'Pembangunan Graha Lestari Inda',
    'PGUN.JK': 'Pradiksi Gunatama Tbk.',
    'PICO.JK': 'Pelangi Indah Canindo Tbk.',
    'PIPA.JK': 'Multi Makmur Lemindo Tbk.',
    'PJAA.JK': 'Pembangunan Jaya Ancol Tbk.',
    'PJHB.JK': 'Pelayaran Jaya Hidup Baru Tbk.',
    'PKPK.JK': 'Paragon Karya Perkasa Tbk.',
    'PLAN.JK': 'Planet Properindo Jaya Tbk.',
    'PLAS.JK': 'Polaris Investama Tbk.',
    'PLIN.JK': 'Poliplas Indah Sejahtera Tbk',
    'PMJS.JK': 'Putra Mandiri Jembar Tbk.',
    'PMMP.JK': 'Panca Mitra Multiperdana Tbk.',
    'PMUI.JK': 'Prima Multi Usaha Indonesia Tb',
    'PNBN.JK': 'Bank Pan Indonesia Tbk.',
    'PNBS.JK': 'Bank Panin Dubai Syariah Tbk.',
    'PNGO.JK': 'Pinago Utama Tbk.',
    'PNIN.JK': 'Panin Financial Tbk',
    'PNLF.JK': 'Panin Financial Tbk.',
    'PNSE.JK': 'Pudjiadi & Sons Estate Tbk',
    'POLA.JK': 'Pool Advista Finance Tbk.',
    'POLI.JK': 'Pollux Hotels Group Tbk.',
    'POLL.JK': 'Pollux Properties Indonesia Tbk',
    'POLU.JK': 'Golden Great Borneo Tbk',
    'POLY.JK': 'Asia Pacific Fibers Tbk.',
    'POOL.JK': 'Pool Advista Indonesia Tbk.',
    'PORT.JK': 'Nusantara Pelabuhan Handal Tbk.',
    'POSA.JK': 'Bliss Properti Indonesia Tbk.',
    'POWR.JK': 'Cikarang Listrindo Tbk.',
    'PPGL.JK': 'Prima Globalindo Logistik Tbk.',
    'PPRE.JK': 'PP Presisi Tbk.',
    'PPRI.JK': 'Paperocks Indonesia Tbk.',
    'PPRO.JK': 'PP Properti Tbk.',
    'PRAS.JK': 'Prima Alloy Steel Universal Tbk',
    'PRAY.JK': 'Famon Awal Bros Sedaya Tbk.',
    'PRDA.JK': 'Prodia Widyahusada Tbk.',
    'PRIM.JK': 'Royal Prima Tbk.',
    'PSAB.JK': 'J Resources Asia Pasifik Tbk.',
    'PSAT.JK': 'Pancaran Samudera Transport Tb',
    'PSDN.JK': 'Prasidha Aneka Niaga Tbk.',
    'PSGO.JK': 'Palma Serasih Tbk.',
    'PSKT.JK': 'Red Planet Indonesia Tbk.',
    'PSSI.JK': 'Pelita Samudera Shipping Tbk',
    'PTBA.JK': 'Bukit Asam (Persero) Tbk.',
    'PTDU.JK': 'Djasa Ubersakti Tbk.',
    'PTIS.JK': 'Indo Straits Tbk.',
    'PTMP.JK': 'Mitra Pack Tbk.',
    'PTMR.JK': 'Master Print Tbk.',
    'PTPP.JK': 'PP (Persero) Tbk.',
    'PTPS.JK': 'Pulau Subur Tbk.',
    'PTPW.JK': 'Pratama Widya Tbk.',
    'PTRO.JK': 'Petrosea Tbk.',
    'PTSN.JK': 'Sat Nusapersada Tbk.',
    'PTSP.JK': 'Pioneerindo Gourmet Internatio',
    'PUDP.JK': 'Pudjiadi Prestige Tbk.',
    'PURA.JK': 'Putra Rajawali Kencana Tbk.',
    'PURE.JK': 'Trinitan Metals and Minerals Tbk',
    'PURI.JK': 'Puri Global Sukses Tbk.',
    'PWON.JK': 'Pakuwon Jati Tbk.',
    'PYFA.JK': 'Pyridam Farma Tbk.',
    'PZZA.JK': 'Sarimelati Kencana Tbk.',
    # === R ===
    'RAAM.JK': 'Tripar Multivision Plus Tbk.',
    'RAFI.JK': 'Sari Kreasi Boga Tbk.',
    'RAJA.JK': 'Rukun Raharja Tbk.',
    'RALS.JK': 'Ramayana Lestari Sentosa Tbk.',
    'RANC.JK': 'Supra Boga Lestari Tbk.',
    'RATU.JK': 'Raharja Energi Cepu Tbk.',
    'RBMS.JK': 'Ristia Bintang Mahkotasejati Tbk',
    'RCCC.JK': 'Utama Radar Cahaya Tbk.',
    'RDTX.JK': 'Roda Vivatex Tbk.',
    'REAL.JK': 'Repower Asia Indonesia Tbk.',
    'RELF.JK': 'Graha Mitra Asia Tbk.',
    'RELI.JK': 'Reliance Sekuritas Indonesia Tbk',
    'RGAS.JK': 'Kian Santang Muliatama Tbk.',
    'RICY.JK': 'Ricky Putra Globalindo Tbk.',
    'RIGS.JK': 'Rig Tenders Indonesia Tbk.',
    'RIMO.JK': 'Rimo International Lestari Tbk.',
    'RISE.JK': 'Jaya Sukses Makmur Sentosa Tbk.',
    'RLCO.JK': 'Abadi Lestari Indonesia Tbk.',
    'RMKE.JK': 'RMK Energy Tbk.',
    'RMKO.JK': 'Royaltama Mulia Kontraktorindo',
    'ROCK.JK': 'Rockfields Properti Indonesia Tbk',
    'RODA.JK': 'Pikko Land Development Tbk.',
    'RONY.JK': 'Aracord Nusantara Group Tbk.',
    'ROTI.JK': 'Nippon Indosari Corpindo Tbk.',
    'RSCH.JK': 'Charlie Hospital Semarang Tbk.',
    'RSGK.JK': 'Kedoya Adyaraya Tbk.',
    'RUIS.JK': 'Radiant Utama Interinsco Tbk.',
    'RUNS.JK': 'Global Sukses Solusi Tbk.',
    # === S ===
    'SAFE.JK': 'Steady Safe Tbk.',
    'SAGE.JK': 'Saptausaha Gemilangindah Tbk.',
    'SAME.JK': 'Sarana Meditama Metropolitan Tbk',
    'SAMF.JK': 'Saraswanti Anugerah Makmur Tbk.',
    'SAPX.JK': 'Satria Antaran Prima Tbk.',
    'SATU.JK': 'Kota Satu Properti Tbk.',
    'SBAT.JK': 'Sejahtera Bintang Abadi Textile Tbk',
    'SBMA.JK': 'Surya Biru Murni Acetylene Tbk.',
    'SCCO.JK': 'Supreme Cable Manufacturing & Commerce Tbk',
    'SCMA.JK': 'Surya Citra Media Tbk.',
    'SCNP.JK': 'Selaras Citra Nusantara Perkas',
    'SCPI.JK': 'Organon Pharma Indonesia Tbk.',
    'SDMU.JK': 'Sidomulyo Selaras Tbk.',
    'SDPC.JK': 'Millennium Pharmacon International Tbk',
    'SDRA.JK': 'Bank Woori Saudara Indonesia 1906 Tbk',
    'SEMA.JK': 'Semacom Integrated Tbk.',
    'SFAN.JK': 'Surya Fajar Capital Tbk.',
    'SGER.JK': 'Sumber Global Energy Tbk.',
    'SGRO.JK': 'Sinar Mas Agribusiness and Food Tbk',
    'SHID.JK': 'Hotel Sahid Jaya International Tbk',
    'SHIP.JK': 'Sillo Maritime Perdana Tbk.',
    'SICO.JK': 'Sigma Energy Compressindo Tbk.',
    'SIDO.JK': 'Industri Jamu dan Farmasi Sido Muncul Tbk',
    'SILO.JK': 'Siloam International Hospitals Tbk',
    'SIMA.JK': 'Siwani Makmur Tbk.',
    'SIMP.JK': 'Salim Ivomas Pratama Tbk.',
    'SINI.JK': 'Singaraja Putra Tbk.',
    'SIPD.JK': 'Sreeya Sewu Indonesia Tbk.',
    'SKBM.JK': 'Sekar Bumi Tbk.',
    'SKLT.JK': 'Sekar Laut Tbk.',
    'SKRN.JK': 'Superkrane Mitra Utama Tbk.',
    'SKYB.JK': 'Northcliff Citranusa Indonesia Tbk',
    'SLIS.JK': 'Gaya Abadi Sempurna Tbk.',
    'SMAR.JK': 'Sinar Mas Agro Resources and T',
    'SMBR.JK': 'Semen Baturaja (Persero) Tbk.',
    'SMCB.JK': 'Solusi Bangun Indonesia Tbk.',
    'SMDM.JK': 'Suryamas Dutamakmur Tbk.',
    'SMDR.JK': 'Samudera Indonesia  Tbk.',
    'SMGA.JK': 'Sumber Mineral Global Abadi Tb',
    'SMGR.JK': 'Semen Indonesia (Persero) Tbk.',
    'SMIL.JK': 'Sarana Mitra Luas Tbk.',
    'SMKL.JK': 'Satyamitra Kemas Lestari Tbk.',
    'SMKM.JK': 'Sumber Mas Konstruksi Tbk.',
    'SMLE.JK': 'Sinergi Multi Lestarindo Tbk.',
    'SMMA.JK': 'Sinarmas Multiartha Tbk.',
    'SMMT.JK': 'Pratama Abadi Nusa Industri Tbk',
    'SMRA.JK': 'Summarecon Agung Tbk.',
    'SMRU.JK': 'SMR Utama Tbk.',
    'SMSM.JK': 'Selamat Sempurna Tbk.',
    'SNLK.JK': 'Sunter Lakeside Hotel Tbk.',
    'SOCI.JK': 'Soechi Lines Tbk.',
    'SOFA.JK': 'Boston Furniture Industries Tbk',
    'SOHO.JK': 'Soho Global Health Tbk.',
    'SOLA.JK': 'Xolare RCR Energy Tbk.',
    'SONA.JK': 'Sona Topas Tourism Industry Tbk',
    'SORG.JK': 'Sorini Agro Asia Corporindo Tbk',
    'SOSS.JK': 'Shield On Service Tbk.',
    'SOTS.JK': 'Satria Mega Kencana Tbk.',
    'SOUL.JK': 'Mitra Tirta Buwana Tbk.',
    'SPMA.JK': 'Suparma Tbk.',
    'SPRE.JK': 'Soraya Berjaya Indonesia Tbk.',
    'SPTO.JK': 'Surya Pertiwi Tbk.',
    'SQMI.JK': 'Wilton Makmur Indonesia Tbk.',
    'SRAJ.JK': 'Sejahteraraya Anugrahjaya Tbk.',
    'SRIL.JK': 'Sri Rejeki Isman Tbk.',
    'SRSN.JK': 'Indo Acidatama Tbk.',
    'SRTG.JK': 'Saratoga Investama Sedaya Tbk.',
    'SSIA.JK': 'Surya Semesta Internusa Tbk.',
    'SSMS.JK': 'Sawit Sumbermas Sarana Tbk.',
    'SSTM.JK': 'Sunson Textile Manufacturer Tbk',
    'STAA.JK': 'Sumber Tani Agung Resources Tb',
    'STAR.JK': 'Buana Artha Anugerah Tbk.',
    'STRK.JK': 'Lovina Beach Brewery Tbk.',
    'STTP.JK': 'Siantar Top Tbk.',
    'SUGI.JK': 'Sugih Energy Tbk.',
    'SULI.JK': 'SLJ Global Tbk.',
    'SUNI.JK': 'Sunindo Pratama Tbk.',
    'SUPA.JK': 'Super Bank Indonesia Tbk.',
    'SUPR.JK': 'Solusi Tunas Pratama Tbk.',
    'SURE.JK': 'Super Energy Tbk.',
    'SURI.JK': 'Maja Agung Latexindo Tbk.',
    'SWAT.JK': 'Sriwahana Adityakarta Tbk.',
    'SWID.JK': 'Saraswanti Indoland Developmen',
    # === T ===
    'TADI.JK': 'Adi Tour Tbk',
    'TALF.JK': 'Tunas Alfin Tbk.',
    'TAMA.JK': 'Lancartama Sejati Tbk.',
    'TAMU.JK': 'Pelayaran Tamarin Samudra Tbk.',
    'TAPG.JK': 'Triputra Agro Persada Tbk.',
    'TARA.JK': 'Agung Semesta Sejahtera Tbk.',
    'TAXI.JK': 'Express Transindo Utama Tbk.',
    'TAYS.JK': 'Jaya Swarasa Agung Tbk.',
    'TBIG.JK': 'Tower Bersama Infrastructure T',
    'TBLA.JK': 'Tunas Baru Lampung Tbk.',
    'TBMS.JK': 'Tembaga Mulia Semanan Tbk.',
    'TCID.JK': 'Mandom Indonesia Tbk.',
    'TCPI.JK': 'Transcoal Pacific Tbk.',
    'TDPM.JK': 'Tridomain Performance Materials Tbk',
    'TEBE.JK': 'Dana Brata Luhur Tbk.',
    'TECH.JK': 'Indosterling Technomedia Tbk.',
    'TELE.JK': 'Tiphone Mobile Indonesia Tbk',
    'TFAS.JK': 'Telefast Indonesia Tbk.',
    'TFCO.JK': 'Tifico Fiber Indonesia Tbk.',
    'TGKA.JK': 'Tigaraksa Satria Tbk.',
    'TGRA.JK': 'Terregra Asia Energy Tbk.',
    'TGUK.JK': 'Platinum Wahab Nusantara Tbk.',
    'TIFA.JK': 'KDB Tifa Finance Tbk.',
    'TINS.JK': 'Timah Tbk.',
    'TIRA.JK': 'Tira Austenite Tbk.',
    'TIRT.JK': 'Tirta Mahakam Resources Tbk.',
    'TKIM.JK': 'Pabrik Kertas Tjiwi Kimia Tbk.',
    'TLDN.JK': 'Teladan Prima Agro Tbk.',
    'TLKM.JK': 'Telkom Indonesia (Persero) Tbk.',
    'TMAS.JK': 'Temas Tbk.',
    'TMPO.JK': 'Tempo Inti Media Tbk',
    'TNCA.JK': 'Trimuda Nuansa Citra Tbk.',
    'TOBA.JK': 'Toba Bara Sejahtera Tbk',
    'TOOL.JK': 'Rohartindo Nusantara Luas Tbk.',
    'TOPS.JK': 'Totalindo Eka Persada Tbk.',
    'TOSK.JK': 'Topindo Solusi Komunika Tbk.',
    'TOTL.JK': 'Total Bangun Persada Tbk.',
    'TOTO.JK': 'Surya Toto Indonesia Tbk.',
    'TOWR.JK': 'Sarana Menara Nusantara Tbk.',
    'TOYS.JK': 'Sunindo Adipersada Tbk.',
    'TPIA.JK': 'Chandra Asri Petrochemical',
    'TPMA.JK': 'Trans Power Marine Tbk.',
    'TRAM.JK': 'Trada Alam Minera Tbk.',
    'TRGU.JK': 'Cerestar Indonesia Tbk.',
    'TRIL.JK': 'Triwira Insanlestari Tbk.',
    'TRIM.JK': 'Trimegah Sekuritas Indonesia Tbk',
    'TRIN.JK': 'Perintis Triniti Properti Tbk.',
    'TRIO.JK': 'Trikomsel Oke Tbk.',
    'TRIS.JK': 'Trisula International Tbk.',
    'TRJA.JK': 'Transkon Jaya Tbk.',
    'TRON.JK': 'Teknologi Karya Digital Nusa T',
    'TRST.JK': 'Trias Sentosa Tbk.',
    'TRUE.JK': 'Triniti Dinamik Tbk.',
    'TRUK.JK': 'Guna Timur Raya Tbk.',
    'TRUS.JK': 'Trust Finance Indonesia Tbk.',
    'TSPC.JK': 'Tempo Scan Pacific Tbk.',
    'TUGU.JK': 'Asuransi Tugu Pratama Indonesia Tbk',
    'TURI.JK': 'Tunas Ridean Tbk',
    'TYRE.JK': 'King Tire Indonesia Tbk.',
    # === U ===
    'UANG.JK': 'Pakuan Tbk.',
    'UCID.JK': 'Uni-Charm Indonesia Tbk.',
    'UDNG.JK': 'Agro Bahari Nusantara Tbk.',
    'UFOE.JK': 'Damai Sejahtera Abadi Tbk.',
    'ULTJ.JK': 'Ultra Jaya Milk Industry & Trading Company Tbk',
    'UNIC.JK': 'Unggul Indah Cahaya Tbk.',
    'UNIQ.JK': 'Ulima Nitra Tbk.',
    'UNIT.JK': 'Nusantara Inti Corpora Tbk.',
    'UNSP.JK': 'Bakrie Sumatera Plantations Tbk',
    'UNTD.JK': 'Terang Dunia Internusa Tbk.',
    'UNTR.JK': 'United Tractors Tbk.',
    'UNVR.JK': 'Unilever Indonesia Tbk.',
    'URBN.JK': 'Urban Jakarta Propertindo Tbk.',
    'UVCR.JK': 'Trimegah Karya Pratama Tbk.',
    # === V ===
    'VAST.JK': 'Vastland Indonesia Tbk.',
    'VERN.JK': 'Verona Indah Pictures Tbk.',
    'VICI.JK': 'Victoria Care Indonesia Tbk.',
    'VICO.JK': 'Victoria Investama Tbk.',
    'VIDS.JK': 'Vidio Dot Com Tbk',
    'VINS.JK': 'Victoria Insurance Tbk.',
    'VISI.JK': 'Satu Visi Putra Tbk.',
    'VIVA.JK': 'Visi Media Asia Tbk.',
    'VKTR.JK': 'VKTR Teknologi Mobilitas Tbk.',
    'VOKS.JK': 'Voksel Electric Tbk.',
    'VRNA.JK': 'Mizuho Leasing Indonesia Tbk.',
    'VTNY.JK': 'Venteny Fortuna International',
    # === W ===
    'WAPO.JK': 'Wahana Pronatural Tbk.',
    'WEGE.JK': 'Wijaya Karya Bangunan Gedung Tbk',
    'WEHA.JK': 'WEHA Transportasi Indonesia Tb',
    'WGSH.JK': 'Wira Global Solusi Tbk.',
    'WICO.JK': 'Wicaksana Overseas International Tbk',
    'WIDI.JK': 'Widiant Jaya Krenindo Tbk.',
    'WIFI.JK': 'Solusi Sinergi Digital Tbk.',
    'WIIM.JK': 'Wismilak Inti Makmur Tbk.',
    'WIKA.JK': 'Wijaya Karya (Persero) Tbk.',
    'WINE.JK': 'Hatten Bali Tbk.',
    'WINR.JK': 'Winner Nusantara Jaya Tbk.',
    'WINS.JK': 'Wintermar Offshore Marine Tbk.',
    'WIRG.JK': 'WIR ASIA Tbk.',
    'WISM.JK': 'Wisma Kodel Tbk',
    'WIYA.JK': 'Widya Yutama Tbk',
    'WMPP.JK': 'Widodo Makmur Perkasa Tbk.',
    'WMUU.JK': 'Widodo Makmur Unggas Tbk.',
    'WOMF.JK': 'Wahana Ottomitra Multiartha Tbk',
    'WOOD.JK': 'Integra Indocabinet Tbk.',
    'WOWS.JK': 'Ginting Jaya Energi Tbk.',
    'WSBP.JK': 'Waskita Beton Precast Tbk.',
    'WSKT.JK': 'Waskita Karya (Persero) Tbk.',
    'WTON.JK': 'Wijaya Karya Beton Tbk.',
    # === Y ===
    'YELO.JK': 'Yelooo Integra Datanet Tbk.',
    'YOII.JK': 'Asuransi Digital Bersama Tbk.',
    'YPAS.JK': 'Yanaprima Hastapersada Tbk.',
    'YULE.JK': 'Yulie Sekuritas Indonesia Tbk.',
    'YUPI.JK': 'Yupi Indo Jelly Gum Tbk.',
    # === Z ===
    'ZATA.JK': 'Bersama Zatta Jaya Tbk.',
    'ZBRA.JK': 'Dosni Roha Indonesia Tbk.',
    'ZINC.JK': 'Kapuas Prima Coal Tbk.',
    'ZONE.JK': 'Mega Perintis Tbk.',
    'ZYRX.JK': 'Zyrexindo Mandiri Buana Tbk.',
}

# Daftar Broker
BROKER_LIST = {
    'YU': 'Yuanta Sekuritas', 'MS': 'Morgan Stanley', 'KS': 'Kresna Sekuritas',
    'NI': 'BNP Paribas', 'RX': 'Macquarie', 'AK': 'UBS', 'GR': 'Goldman Sachs',
    'BK': 'Credit Suisse', 'TP': 'Citigroup', 'ML': 'Merrill Lynch',
    'DX': 'Deutsche Bank', 'JP': 'JP Morgan', 'CL': 'CitiGroup',
    'BB': 'Bahana Sekuritas', 'DM': 'Danamon Sekuritas', 'PD': 'Panin Sekuritas',
    'BM': 'Mandiri Sekuritas', 'BJ': 'BJB Sekuritas', 'BS': 'Sinarmas Sekuritas',
    'MK': 'Mega Kapital', 'FO': 'Sinar Mas Sekuritas', 'KK': 'Kwik Kian Gie',
    'HD': 'Henan Putihrai', 'MU': 'UOB Kay Hian', 'CC': 'CIMB Sekuritas',
    'GA': 'Aldiracita Sekuritas', 'IP': 'MNC Sekuritas', 'RA': 'Reliance Sekuritas',
    'MG': 'Mega Capital', 'GV': 'Avian Sekuritas', 'YR': 'RHB Sekuritas',
    'SF': 'Solusi Sekuritas', 'DR': 'DBS Vickers', 'HS': 'HSBC Sekuritas',
    'OC': 'OCBC Sekuritas', 'MA': 'Maybank Sekuritas', 'SA': 'Standard Chartered',
    'AB': 'Anabatic Technologies', 'ID': 'Indosurya Bersinar', 'EF': 'Ekokapital',
    'LG': 'Lautandhana', 'AH': 'Ahamania Sekuritas', 'AZ': 'Aziz Traders',
    'BA': 'Bareksa Sekuritas', 'BC': 'BCA Sekuritas', 'BD': 'Batavia Prosperindo',
    'BI': 'Bumiindonesia', 'BL': 'Bell Potter', 'BN': 'Nusantara Capital',
    'BO': 'Bosowa Sekuritas', 'BP': 'BNP Paribas', 'BQ': 'Barclays Capital',
    'BR': 'BRI Danareksa', 'BT': 'Batavia Prosperindo', 'BU': 'UBS Indonesia',
    'BV': 'Valbury Sekuritas', 'BW': 'Woori Investment', 'BX': 'Bumiputera Sekuritas',
    'BY': 'Byron Sekuritas', 'BZ': 'Bessemer Trust', 'CA': 'Ciptadana Sekuritas',
    'CB': 'CIMB Niaga', 'CD': 'Credit Suisse', 'CG': 'CGS-CIMB Sekuritas',
    'ZZ': 'Retail/Individual'
}

# ============================================================================
# FUNGSI TEKNIKAL ANALISIS
# ============================================================================

@st.cache_data(ttl=600)
def get_stock_data(symbol, period='1y', interval='1d'):
    """Mengambil data saham dari Yahoo Finance dengan retry logic"""
    max_retries = 4
    base_delay = 3  # detik

    for attempt in range(max_retries):
        try:
            # Jitter acak agar tidak semua request bersamaan
            if attempt > 0:
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0.5, 2.0)
                time.sleep(delay)

            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval, timeout=15)

            if df is not None and not df.empty and len(df) >= 5:
                df.index = pd.to_datetime(df.index)
                if df.index.tz is not None:
                    df.index = df.index.tz_localize(None)
                return df

        except Exception as e:
            err_str = str(e).lower()
            if 'too many requests' in err_str or 'rate limit' in err_str or '429' in err_str:
                if attempt < max_retries - 1:
                    wait = base_delay * (2 ** attempt) + random.uniform(1, 3)
                    st.warning(f"⏳ Yahoo Finance rate limit, mencoba lagi dalam {wait:.0f} detik... ({attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
                else:
                    st.error("❌ Yahoo Finance membatasi request. Tunggu beberapa menit lalu coba lagi.")
            else:
                st.error(f"❌ Error mengambil data {symbol}: {e}")
            return None

    st.error(f"❌ Gagal mengambil data {symbol} setelah {max_retries} percobaan. Coba lagi dalam 1-2 menit.")
    return None

def calculate_indicators(df):
    """Menghitung berbagai indikator teknikal lengkap"""
    if df is None or df.empty:
        return None
    
    df = df.copy()
    
    # Moving Averages
    df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
    df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
    df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
    df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
    df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
    
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Hist'] = macd.macd_diff()
    
    # RSI
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    
    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df['Close'])
    df['BB_Upper'] = bollinger.bollinger_hband()
    df['BB_Middle'] = bollinger.bollinger_mavg()
    df['BB_Lower'] = bollinger.bollinger_lband()
    df['BB_Width'] = bollinger.bollinger_wband()
    
    # Stochastic
    stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
    df['Stoch_K'] = stoch.stoch()
    df['Stoch_D'] = stoch.stoch_signal()
    
    # ATR
    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])
    
    # Volume
    df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
    
    # ADX
    adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'])
    df['ADX'] = adx.adx()
    df['DI_Plus'] = adx.adx_pos()
    df['DI_Minus'] = adx.adx_neg()
    
    # Fibonacci
    recent_high = df['High'].rolling(window=20).max()
    recent_low = df['Low'].rolling(window=20).min()
    diff = recent_high - recent_low
    df['Fib_0'] = recent_high
    df['Fib_236'] = recent_high - 0.236 * diff
    df['Fib_382'] = recent_high - 0.382 * diff
    df['Fib_500'] = recent_high - 0.500 * diff
    df['Fib_618'] = recent_high - 0.618 * diff
    df['Fib_100'] = recent_low
    
    # Support/Resistance
    df['Support'] = df['Low'].rolling(window=20).min()
    df['Resistance'] = df['High'].rolling(window=20).max()
    
    return df

def analyze_strategy(df, strategy_type):
    """Analisis strategi trading lengkap"""
    if df is None or len(df) < 50:
        return None
    
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    signals = {
        'rekomendasi': 'HOLD',
        'confidence': 0,
        'alasan': [],
        'entry': None,
        'stop_loss': None,
        'take_profit': None,
        'risk_reward': None
    }
    
    if strategy_type == 'Scalping':
        ema_buy = latest['EMA_12'] > latest['EMA_26'] and prev['EMA_12'] <= prev['EMA_26']
        ema_sell = latest['EMA_12'] < latest['EMA_26'] and prev['EMA_12'] >= prev['EMA_26']
        rsi_valid = 30 < latest['RSI'] < 70
        bb_bounce_up = latest['Close'] > latest['BB_Lower'] and prev['Close'] <= prev['BB_Lower']
        bb_bounce_down = latest['Close'] < latest['BB_Upper'] and prev['Close'] >= prev['BB_Upper']
        volume_spike = latest['Volume_Ratio'] > 1.5
        
        if ema_buy and rsi_valid and (bb_bounce_up or volume_spike):
            signals['rekomendasi'] = 'BUY'
            signals['confidence'] = 75
            signals['alasan'] = ['EMA 12/26 bullish crossover', 'RSI netral', 'Volume spike' if volume_spike else 'BB bounce']
            signals['entry'] = latest['Close']
            signals['stop_loss'] = latest['Close'] - (latest['ATR'] * 1.5)
            signals['take_profit'] = latest['Close'] + (latest['ATR'] * 2)
        elif ema_sell and rsi_valid and (bb_bounce_down or volume_spike):
            signals['rekomendasi'] = 'SELL'
            signals['confidence'] = 75
            signals['alasan'] = ['EMA 12/26 bearish crossover', 'RSI netral', 'Volume spike' if volume_spike else 'BB rejection']
            signals['entry'] = latest['Close']
            signals['stop_loss'] = latest['Close'] + (latest['ATR'] * 1.5)
            signals['take_profit'] = latest['Close'] - (latest['ATR'] * 2)
            
    elif strategy_type == 'Intraday':
        macd_buy = latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']
        macd_sell = latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']
        rsi_oversold = latest['RSI'] < 30
        rsi_overbought = latest['RSI'] > 70
        strong_trend = latest['ADX'] > 25
        above_sma20 = latest['Close'] > latest['SMA_20']
        below_sma20 = latest['Close'] < latest['SMA_20']
        
        if (macd_buy or (macd_buy and rsi_oversold)) and strong_trend and above_sma20:
            signals['rekomendasi'] = 'BUY'
            signals['confidence'] = 80
            signals['alasan'] = ['MACD bullish crossover', f'RSI oversold ({latest["RSI"]:.1f})' if rsi_oversold else f'ADX kuat ({latest["ADX"]:.1f})', 'Di atas SMA 20']
            signals['entry'] = latest['Close']
            signals['stop_loss'] = latest['Support']
            signals['take_profit'] = latest['Resistance']
        elif (macd_sell or (macd_sell and rsi_overbought)) and strong_trend and below_sma20:
            signals['rekomendasi'] = 'SELL'
            signals['confidence'] = 80
            signals['alasan'] = ['MACD bearish crossover', f'RSI overbought ({latest["RSI"]:.1f})' if rsi_overbought else f'ADX kuat ({latest["ADX"]:.1f})', 'Di bawah SMA 20']
            signals['entry'] = latest['Close']
            signals['stop_loss'] = latest['Resistance']
            signals['take_profit'] = latest['Support']
            
    else:  # Investasi
        golden_cross = latest['SMA_50'] > latest['SMA_200'] and prev['SMA_50'] <= prev['SMA_200']
        death_cross = latest['SMA_50'] < latest['SMA_200'] and prev['SMA_50'] >= prev['SMA_200']
        bullish_trend = latest['SMA_50'] > latest['SMA_200']
        bearish_trend = latest['SMA_50'] < latest['SMA_200']
        near_fib_618 = abs(latest['Close'] - latest['Fib_618']) / latest['Close'] < 0.02
        
        if golden_cross or (bullish_trend and near_fib_618):
            signals['rekomendasi'] = 'BUY'
            signals['confidence'] = 85
            signals['alasan'] = ['Golden Cross!' if golden_cross else 'Trend bullish', 'Harga di atas SMA 50', 'Bounce Fib 61.8%' if near_fib_618 else 'Momentum positif']
            signals['entry'] = latest['Close']
            signals['stop_loss'] = latest['Fib_100'] * 0.98
            signals['take_profit'] = latest['Fib_0'] * 1.05
        elif death_cross or (bearish_trend and latest['Close'] < latest['SMA_50']):
            signals['rekomendasi'] = 'SELL'
            signals['confidence'] = 85
            signals['alasan'] = ['Death Cross!' if death_cross else 'Trend bearish', 'Harga di bawah SMA 50', 'Breakdown support']
            signals['entry'] = latest['Close']
            signals['stop_loss'] = latest['Resistance'] * 1.02
            signals['take_profit'] = latest['Support'] * 0.95
    
    if signals['entry'] and signals['stop_loss'] and signals['take_profit']:
        risk = abs(signals['entry'] - signals['stop_loss'])
        reward = abs(signals['take_profit'] - signals['entry'])
        if risk > 0:
            signals['risk_reward'] = round(reward / risk, 2)
    
    return signals

# ============================================================================
# FUNGSI BANDARMOLOGI
# ============================================================================

def analyze_bandarmology(df, symbol, manual_data=None):
    """Bandarmologi enhanced: OBV + A/D Line + CMF + MFI + OBV Slope + Divergence"""
    if df is None or len(df) < 20:
        return None

    close  = df['Close'].copy()
    high   = df['High'].copy()
    low    = df['Low'].copy()
    volume = df['Volume'].copy()

    # ── OBV (On-Balance Volume) ──────────────────────────────────────────────
    obv = [0]
    for i in range(1, len(df)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.append(obv[-1] + volume.iloc[i])
        elif close.iloc[i] < close.iloc[i-1]:
            obv.append(obv[-1] - volume.iloc[i])
        else:
            obv.append(obv[-1])
    obv_s        = pd.Series(obv, index=close.index)
    obv_sma20    = obv_s.rolling(20).mean()
    obv_sma5     = obv_s.rolling(5).mean()
    obv_trend    = 'UP'   if obv_s.iloc[-1] > obv_sma20.iloc[-1] else 'DOWN'
    # OBV slope (5-day momentum)
    obv_slope    = obv_s.iloc[-1] - obv_s.iloc[-6] if len(obv_s) > 5 else 0
    obv_accel    = obv_sma5.iloc[-1] > obv_sma5.iloc[-6] if len(obv_sma5) > 5 else False
    df['OBV']     = obv_s.values
    df['OBV_SMA'] = obv_sma20.values

    # ── A/D Line (Accumulation/Distribution) ────────────────────────────────
    hl_range  = (high - low).replace(0, 1e-9)
    mfm       = ((close - low) - (high - close)) / hl_range
    ad_line   = (mfm * volume).cumsum()
    ad_sma20  = ad_line.rolling(20).mean()
    ad_trend  = 'UP' if ad_line.iloc[-1] > ad_line.iloc[-20] else 'DOWN'
    ad_slope  = ad_line.iloc[-1] - ad_line.iloc[-6] if len(ad_line) > 5 else 0
    df['AD_Line'] = ad_line.values

    # ── CMF (Chaikin Money Flow, 20-period) ─────────────────────────────────
    cmf_num   = (mfm * volume).rolling(20).sum()
    cmf_den   = volume.rolling(20).sum().replace(0, 1e-9)
    cmf       = (cmf_num / cmf_den).iloc[-1]
    cmf_prev  = (cmf_num / cmf_den).iloc[-5] if len(cmf_num) > 4 else cmf
    cmf_trend = 'UP' if cmf > 0 else 'DOWN'
    cmf_signal= (
        'STRONG BUY' if cmf > 0.15 else
        'BUY'        if cmf > 0.05 else
        'NEUTRAL'    if cmf > -0.05 else
        'SELL'       if cmf > -0.15 else
        'STRONG SELL'
    )

    # ── MFI (Money Flow Index, 14-period) ───────────────────────────────────
    typical_price = (high + low + close) / 3
    raw_mf        = typical_price * volume
    pos_mf        = raw_mf.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
    neg_mf        = raw_mf.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
    mfi           = (100 - 100 / (1 + pos_mf / neg_mf.replace(0, 1e-9))).iloc[-1]
    mfi_signal    = (
        'OVERBOUGHT (Distribusi)'  if mfi > 80 else
        'NETRAL BULLISH'           if mfi > 55 else
        'NETRAL'                   if mfi > 45 else
        'NETRAL BEARISH'           if mfi > 20 else
        'OVERSOLD (Akumulasi)'
    )

    # ── Price trend & Volume ratio ───────────────────────────────────────────
    price_trend = 'UP'   if close.iloc[-1] > close.iloc[-20] else 'DOWN'
    price_vs5   = 'UP'   if close.iloc[-1] > close.iloc[-6]  else 'DOWN'
    vol_ratio   = volume.tail(5).mean() / volume.mean() if volume.mean() > 0 else 1.0

    # ── Divergence detection ─────────────────────────────────────────────────
    # Bullish divergence: price lower low, OBV higher low
    price_ll = close.iloc[-1] < close.iloc[-10]
    obv_hl   = obv_s.iloc[-1] > obv_s.iloc[-10]
    # Bearish divergence: price higher high, OBV lower high
    price_hh = close.iloc[-1] > close.iloc[-10]
    obv_lh   = obv_s.iloc[-1] < obv_s.iloc[-10]

    if price_ll and obv_hl:
        divergence = 'BULLISH (Potensi reversal naik)'
    elif price_hh and obv_lh:
        divergence = 'BEARISH (Potensi reversal turun)'
    else:
        divergence = 'TIDAK ADA'

    # ── SCORING ──────────────────────────────────────────────────────────────
    score = 0
    signals_list = []

    if obv_trend == 'UP':                   score += 20; signals_list.append('OBV di atas SMA20')
    if obv_slope > 0:                       score += 10; signals_list.append('OBV slope naik (momentum)')
    if obv_accel:                           score +=  5; signals_list.append('OBV accelerating')
    if ad_trend == 'UP':                    score += 20; signals_list.append('A/D Line naik')
    if ad_slope > 0:                        score +=  5; signals_list.append('A/D slope naik')
    if cmf > 0.05:                          score += 15; signals_list.append(f'CMF positif ({cmf:.2f})')
    if cmf > cmf_prev:                      score +=  5; signals_list.append('CMF membaik')
    if mfi < 40:                            score += 15; signals_list.append(f'MFI oversold ({mfi:.0f})')
    elif 40 <= mfi <= 60:                   score +=  5; signals_list.append(f'MFI netral ({mfi:.0f})')
    if price_trend == obv_trend:            score += 10; signals_list.append('Price-OBV konfirmasi')
    if vol_ratio > 1.3:                     score +=  5; signals_list.append(f'Volume naik {vol_ratio:.1f}x')
    if 'BULLISH' in divergence:             score += 15; signals_list.append('Divergence bullish!')

    # Kurangi skor untuk sinyal negatif
    if obv_trend == 'DOWN' and ad_trend == 'DOWN': score -= 10
    if cmf < -0.1:                                  score -= 10
    if mfi > 80:                                    score -= 10
    if 'BEARISH' in divergence:                     score -= 15

    score = max(0, min(100, score))

    # ── Kesimpulan ────────────────────────────────────────────────────────────
    if score >= 70:
        trend = 'STRONG ACCUMULATION'
        interp = 'Smart money masuk dengan kuat. Peluang beli sangat baik.'
        impl   = 'Cari entry di support atau pullback. SL di bawah support terdekat.'
    elif score >= 50:
        trend = 'ACCUMULATION'
        interp = 'Tanda akumulasi terlihat jelas. Momentum membaik.'
        impl   = 'Monitor konfirmasi breakout. Entry bertahap di support.'
    elif score >= 35:
        trend = 'NEUTRAL'
        interp = 'Belum ada sinyal tegas. Pasar dalam konsolidasi.'
        impl   = 'Tunggu konfirmasi dari volume dan price action.'
    elif score >= 20:
        trend = 'DISTRIBUTION'
        interp = 'Sinyal distribusi mulai muncul. Waspadai tekanan jual.'
        impl   = 'Kurangi posisi bertahap. Pasang SL lebih ketat.'
    else:
        trend = 'STRONG DISTRIBUTION'
        interp = 'Smart money keluar. Tekanan jual dominan.'
        impl   = 'Hindari beli. Pertimbangkan cut loss jika masih pegang.'

    analysis = {
        'data_type':    'DATA NYATA — Yahoo Finance (Delay ~15 mnt)',
        'last_update':  df.index[-1].strftime('%Y-%m-%d'),
        'trend':        trend,
        'strength':     score,
        'interpretation': interp,
        'trading_implications': impl,
        'has_realtime': False,
        'indicators': {
            'obv_trend':   obv_trend,
            'obv_slope':   obv_slope,
            'ad_trend':    ad_trend,
            'ad_slope':    ad_slope,
            'cmf':         round(cmf, 4),
            'cmf_signal':  cmf_signal,
            'mfi':         round(mfi, 1),
            'mfi_signal':  mfi_signal,
            'price_trend': price_trend,
            'vol_ratio':   round(vol_ratio, 2),
            'divergence':  divergence,
            'signals':     signals_list,
        },
        # Raw series untuk chart
        '_obv':     obv_s,
        '_ad':      ad_line,
        '_cmf':     (cmf_num / cmf_den),
        '_mfi_raw': (100 - 100 / (1 + pos_mf / neg_mf.replace(0, 1e-9))),
    }

    if manual_data and symbol in manual_data:
        analysis['manual_data']  = manual_data[symbol]
        analysis['has_realtime'] = True

    return analysis

# ============================================================================
# FUNGSI SCRAPER IDX FOREIGN NET (DATA NYATA HARIAN)
# ============================================================================

@st.cache_data(ttl=3600)
def get_idx_foreign_net(symbol):
    """Ambil data foreign net harian dari IDX (data nyata, update EOD)"""
    try:
        import urllib.request as urlreq
        code = symbol.replace('.JK', '')
        url = (
            f"https://www.idx.co.id/primary/TradingSummary/GetStockSummary"
            f"?code={code}&start=0&length=10"
        )
        req = urlreq.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json',
            'Referer': 'https://www.idx.co.id/',
        })
        with urlreq.urlopen(req, timeout=10) as resp:
            raw = json.loads(resp.read().decode())
        data = raw.get('data', [])
        if not data:
            return None
        rows = []
        for d in data[:10]:
            try:
                fb = float(d.get('ForeignBuy',  0) or 0)
                fs = float(d.get('ForeignSell', 0) or 0)
                rows.append({
                    'Tanggal':     d.get('Date', '')[:10],
                    'Foreign_Buy': fb,
                    'Foreign_Sell':fs,
                    'Foreign_Net': fb - fs,
                    'Volume':      float(d.get('Volume', 0) or 0),
                    'Value':       float(d.get('Value',  0) or 0),
                    'Freq':        int(  d.get('Frequency', 0) or 0),
                })
            except Exception:
                continue
        return pd.DataFrame(rows) if rows else None
    except Exception:
        return None


@st.cache_data(ttl=3600)
def get_institutional_ownership(symbol):
    """Ambil institutional ownership dari yfinance (update mingguan)"""
    try:
        ticker = yf.Ticker(symbol)
        info   = ticker.info
        inst_pct    = info.get('heldPercentInstitutions', None)
        insider_pct = info.get('heldPercentInsiders',     None)
        float_sh    = info.get('floatShares',             None)
        shares_out  = info.get('sharesOutstanding',       None)
        try:
            inst_holders = ticker.institutional_holders
        except Exception:
            inst_holders = None
        return {
            'inst_pct':     inst_pct,
            'insider_pct':  insider_pct,
            'float_shares': float_sh,
            'shares_out':   shares_out,
            'inst_holders': inst_holders,
        }
    except Exception:
        return None


# ============================================================================
# FUNGSI BANDARMOLOGI ENHANCED
# ============================================================================

# ============================================================================
# FUNGSI VISUALISASI
# ============================================================================

def create_main_chart(df, symbol, strategy):
    """Chart utama dengan semua indikator"""
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.15, 0.15, 0.2],
        subplot_titles=('Price Action', 'MACD', 'RSI', 'Volume')
    )
    
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name='OHLC'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', line=dict(color='blue', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(color='orange', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], name='SMA 200', line=dict(color='red', width=1)), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper', line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower', line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['Support'], name='Support', line=dict(color='green', width=1, dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Resistance'], name='Resistance', line=dict(color='red', width=1, dash='dot')), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='red')), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name='Histogram', marker_color='gray'), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Volume_SMA'], name='Vol SMA 20', line=dict(color='orange')), row=4, col=1)
    
    fig.update_layout(
        title=f'{symbol} - Analisis Teknikal ({strategy})',
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def create_bandarmology_chart(df):
    """Chart khusus bandarmologi"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=('Price & Volume', 'OBV (On Balance Volume)', 'Accumulation/Distribution')
    )
    
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name='Price'
    ), row=1, col=1)
    
    colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'red' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors, opacity=0.3), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['OBV'], name='OBV', line=dict(color='blue')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['OBV_SMA'], name='OBV SMA 20', line=dict(color='orange', dash='dash')), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['AD_Line'], name='A/D Line', line=dict(color='purple')), row=3, col=1)
    
    fig.update_layout(height=700, showlegend=True, xaxis_rangeslider_visible=False)
    return fig

def create_broker_chart(broker_data):
    """Visualisasi aktivitas broker"""
    df = broker_data['detail']
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Net Value by Broker', 'Buy vs Sell', 'Foreign vs Local', 'Top 10 Activity'),
        specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "pie"}, {"type": "bar"}]]
    )
    
    colors = ['green' if x > 0 else 'red' for x in df['Net_Value']]
    fig.add_trace(go.Bar(y=df['Kode'], x=df['Net_Value'], orientation='h', marker_color=colors, name='Net Value'), row=1, col=1)
    
    fig.add_trace(go.Bar(x=df['Kode'], y=df['Buy_Value'], name='Buy', marker_color='green'), row=1, col=2)
    fig.add_trace(go.Bar(x=df['Kode'], y=df['Sell_Value'], name='Sell', marker_color='red'), row=1, col=2)
    
    foreign_total = df[df['Type'] == 'Foreign']['Total_Value'].sum()
    local_total = df[df['Type'] == 'Local']['Total_Value'].sum()
    fig.add_trace(go.Pie(labels=['Foreign', 'Local'], values=[foreign_total, local_total], hole=0.4), row=2, col=1)
    
    top_10 = df.head(10)
    fig.add_trace(go.Bar(x=top_10['Kode'], y=top_10['Total_Value'], marker_color='blue', name='Total Value'), row=2, col=2)
    
    fig.update_layout(height=800, showlegend=True, barmode='group')
    return fig

# ============================================================================
# FUNGSI GROQ AI ANALYST
# ============================================================================

def groq_ai_analyze(prompt, groq_api_key, model="llama3-8b-8192"):
    """Kirim prompt ke Groq API dan return response text"""
    try:
        import urllib.request
        import urllib.error

        payload = json.dumps({
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah analis saham Indonesia profesional yang berpengalaman. "
                        "Berikan analisis yang tajam, actionable, dan dalam Bahasa Indonesia. "
                        "Gunakan data teknikal yang diberikan untuk insight mendalam. "
                        "Format respons dengan poin-poin yang jelas dan ringkas."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
            "max_tokens": 1500,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json",
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error Groq API: {str(e)}"


def build_scanner_prompt(df_res):
    """Buat prompt dari hasil scanner untuk dikirim ke Groq"""
    top_buy   = df_res[df_res['Rekomendasi'].isin(['STRONG BUY','BUY'])].nlargest(10, 'Score')
    top_vol   = df_res.nlargest(8, 'Vol_Ratio')
    top_akum  = df_res[df_res['Bandar'] == 'AKUMULASI'].nlargest(8, 'Score')
    top_gain  = df_res.nlargest(8, 'Change_1D')
    top_loss  = df_res.nsmallest(8, 'Change_1D')

    def fmt_row(r):
        return (f"  {r['Symbol']} ({r['Nama'][:20]}): "
                f"Score={r['Score']}, RSI={r['RSI']:.0f}, "
                f"Vol={r['Vol_Ratio']:.1f}x, 1D={r['Change_1D']:+.1f}%, "
                f"Bandar={r['Bandar']}, Sinyal={r['Sinyal']}")

    lines = [
        f"=== HASIL SCAN PASAR SAHAM INDONESIA — {datetime.now().strftime('%d %b %Y %H:%M')} ===",
        f"Total saham teranalisis: {len(df_res)}",
        f"STRONG BUY: {len(df_res[df_res['Rekomendasi']=='STRONG BUY'])} | "
        f"BUY: {len(df_res[df_res['Rekomendasi']=='BUY'])} | "
        f"NEUTRAL: {len(df_res[df_res['Rekomendasi']=='NEUTRAL'])} | "
        f"SELL: {len(df_res[df_res['Rekomendasi'].isin(['SELL','WEAK SELL'])])}",
        f"Volume Anomali (>2x): {len(df_res[df_res['Vol_Anomaly']])}",
        f"Akumulasi: {len(df_res[df_res['Bandar']=='AKUMULASI'])} | "
        f"Distribusi: {len(df_res[df_res['Bandar']=='DISTRIBUSI'])}",
        "",
        "TOP BUY SIGNAL:",
        *[fmt_row(r) for _, r in top_buy.iterrows()],
        "",
        "TOP VOLUME ANOMALI:",
        *[fmt_row(r) for _, r in top_vol.iterrows()],
        "",
        "TOP AKUMULASI (Bandarmologi):",
        *[fmt_row(r) for _, r in top_akum.iterrows()],
        "",
        "TOP GAINER HARI INI:",
        *[fmt_row(r) for _, r in top_gain.iterrows()],
        "",
        "TOP LOSER HARI INI:",
        *[fmt_row(r) for _, r in top_loss.iterrows()],
    ]

    prompt = "\n".join(lines) + """

Berdasarkan data scan di atas, berikan analisis komprehensif meliputi:

1. 🌡️ **SENTIMEN PASAR** — Bagaimana kondisi pasar IDX hari ini secara keseluruhan?

2. 🏆 **TOP 5 SAHAM PILIHAN** — Saham terbaik untuk dipertimbangkan hari ini beserta alasannya

3. 🚨 **ALERT VOLUME ANOMALI** — Saham mana yang perlu diwaspadai karena pergerakan volume tidak wajar?

4. 🕵️ **SINYAL BANDARMOLOGI** — Saham mana yang terindikasi sedang diakumulasi smart money?

5. ⚡ **TOP GAINER & LOSER** — Analisis momentum dan apakah masih layak dikejar atau justru dihindari?

6. 🎯 **STRATEGI HARI INI** — Rekomendasi konkret untuk trader intraday dan swing trader

7. ⚠️ **RISIKO & DISCLAIMER** — Peringatan risiko yang perlu diperhatikan

Jawab dalam Bahasa Indonesia yang profesional namun mudah dipahami."""
    return prompt


def build_single_stock_prompt(row):
    """Prompt AI untuk satu saham dari hasil scanner"""
    return f"""
Analisis saham berikut dari hasil scanner teknikal:

Kode     : {row['Symbol']} — {row['Nama']}
Harga    : Rp {row['Harga']:,.0f}
Perubahan: 1D={row['Change_1D']:+.2f}% | 1W={row['Change_1W']:+.2f}% | 1M={row['Change_1M']:+.2f}%
Score    : {row['Score']}/100 → {row['Rekomendasi']}
RSI      : {row['RSI']:.1f}
Vol Ratio: {row['Vol_Ratio']:.2f}x rata-rata 20 hari
Bandar   : {row['Bandar']} (OBV: {row['OBV_Trend']})
BB Pos   : {row['BB_Pos']:.0%} (0%=bawah, 100%=atas Bollinger Band)
Support  : Rp {row['Support']:,.0f}
Resistance: Rp {row['Resistance']:,.0f}
MACD Cross: {'✅ Bullish Cross' if row['MACD_Cross'] else '❌ Belum cross'}
Sinyal   : {row['Sinyal']}

Berikan analisis singkat (max 300 kata) mencakup:
1. **Kesimpulan** — layak beli/jual/hold?
2. **Alasan Teknikal** — indikator apa yang mendukung keputusan ini?
3. **Level Entry** — harga masuk yang ideal
4. **Stop Loss & Target** — level SL dan TP yang disarankan
5. **Risiko** — apa yang perlu diwaspadai?

Jawab dalam Bahasa Indonesia yang padat dan actionable.
"""


# ============================================================================
# FUNGSI SCANNER MASSAL
# ============================================================================

BLUECHIP_LIST = [
    'BBCA.JK','BBRI.JK','BMRI.JK','BBNI.JK','TLKM.JK','ASII.JK',
    'UNVR.JK','KLBF.JK','ICBP.JK','INDF.JK','UNTR.JK','PGAS.JK',
    'ADRO.JK','PTBA.JK','ITMG.JK','ANTM.JK','TINS.JK','SMGR.JK',
    'INTP.JK','CPIN.JK','JPFA.JK','INKP.JK','TKIM.JK','EXCL.JK',
    'ISAT.JK','BYAN.JK','HRUM.JK','BSSR.JK','MBAP.JK','GEMS.JK',
    'BRPT.JK','TPIA.JK','ESSA.JK','BRIS.JK','ARTO.JK','GOTO.JK',
    'BUKA.JK','MYOR.JK','STTP.JK','ULTJ.JK','CLEO.JK','CMRY.JK',
    'HEAL.JK','MIKA.JK','SILO.JK','AMRT.JK','LPPF.JK','MAPI.JK',
    'AVIA.JK','MARK.JK','TLKM.JK','BBTN.JK','BJBR.JK','BJTM.JK',
    'ERAA.JK','RALS.JK','SCMA.JK','MNCN.JK','TBIG.JK','TOWR.JK',
]


def quick_scan_stock(symbol):
    """Scan cepat satu saham — return dict hasil atau None"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='6mo', interval='1d', timeout=12)
        if df is None or df.empty or len(df) < 30:
            return None

        df.index = pd.to_datetime(df.index)
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        close  = df['Close']
        volume = df['Volume']
        high   = df['High']
        low    = df['Low']
        open_  = df['Open']

        # ── Harga & perubahan ──────────────────────────────────────────
        price     = close.iloc[-1]
        price_1d  = (close.iloc[-1] / close.iloc[-2]  - 1) * 100 if len(close) > 1  else 0
        price_1w  = (close.iloc[-1] / close.iloc[-6]  - 1) * 100 if len(close) > 5  else 0
        price_1mo = (close.iloc[-1] / close.iloc[-22] - 1) * 100 if len(close) > 21 else 0

        # ── Moving averages ────────────────────────────────────────────
        sma20  = close.rolling(20).mean().iloc[-1]
        sma50  = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else sma20
        sma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else sma20

        # ── RSI ────────────────────────────────────────────────────────
        delta = close.diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rs    = gain / loss.replace(0, 1e-9)
        rsi   = (100 - 100 / (1 + rs)).iloc[-1]

        # ── MACD ───────────────────────────────────────────────────────
        ema12       = close.ewm(span=12).mean()
        ema26       = close.ewm(span=26).mean()
        macd_line   = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        macd_val    = macd_line.iloc[-1]
        macd_sig    = signal_line.iloc[-1]
        macd_cross  = (macd_val > macd_sig) and (macd_line.iloc[-2] <= signal_line.iloc[-2])

        # ── Stochastic ─────────────────────────────────────────────────
        lo14  = low.rolling(14).min()
        hi14  = high.rolling(14).max()
        stoch_k = ((close - lo14) / (hi14 - lo14).replace(0, 1e-9) * 100).iloc[-1]

        # ── Volume anomali ─────────────────────────────────────────────
        vol_avg   = volume.rolling(20).mean().iloc[-1]
        vol_ratio = volume.iloc[-1] / vol_avg if vol_avg > 0 else 1.0
        vol_5d    = volume.tail(5).mean()
        vol_trend = 'NAIK' if vol_5d > vol_avg else 'TURUN'

        # ── OBV (Bandarmologi) ─────────────────────────────────────────
        obv = [0]
        for i in range(1, len(df)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i-1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        obv_s     = pd.Series(obv)
        obv_sma   = obv_s.rolling(20).mean()
        obv_trend = 'UP' if obv_s.iloc[-1] > obv_sma.iloc[-1] else 'DOWN'
        obv_slope = obv_s.iloc[-1] - obv_s.iloc[-5]  # slope 5 hari

        # ── A/D Line ───────────────────────────────────────────────────
        hl  = (high - low).replace(0, 1e-9)
        mfm = ((close - low) - (high - close)) / hl
        ad  = (mfm * volume).cumsum()
        ad_trend = 'UP' if ad.iloc[-1] > ad.iloc[-10] else 'DOWN'

        # ── Bollinger Bands ────────────────────────────────────────────
        bb_mid   = close.rolling(20).mean()
        bb_std   = close.rolling(20).std()
        bb_upper = (bb_mid + 2 * bb_std).iloc[-1]
        bb_lower = (bb_mid - 2 * bb_std).iloc[-1]
        bb_range = bb_upper - bb_lower
        bb_pos   = (price - bb_lower) / bb_range if bb_range > 0 else 0.5
        bb_pct   = (bb_range / bb_mid.iloc[-1]) * 100  # BB width %

        # ── ATR & Support/Resistance ───────────────────────────────────
        tr  = pd.concat([high-low, (high-close.shift()).abs(), (low-close.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        support    = low.rolling(20).min().iloc[-1]
        resistance = high.rolling(20).max().iloc[-1]

        # ── Candle pattern (sederhana) ─────────────────────────────────
        body      = abs(close.iloc[-1] - open_.iloc[-1])
        full_rng  = high.iloc[-1] - low.iloc[-1]
        is_doji   = body / full_rng < 0.1 if full_rng > 0 else False
        is_green  = close.iloc[-1] > open_.iloc[-1]
        is_hammer = (
            (low.iloc[-1] < min(open_.iloc[-1], close.iloc[-1]) - body) and
            body / full_rng < 0.4
        ) if full_rng > 0 else False

        # ── Top Gainer / Loser flag ────────────────────────────────────
        is_top_gainer = price_1d >= 3.0
        is_top_loser  = price_1d <= -3.0

        # ── SCORING ───────────────────────────────────────────────────
        score   = 0
        signals = []

        # Trend (30 pts)
        if price > sma20:                     score += 10; signals.append('Di atas SMA20')
        if price > sma50:                     score += 10; signals.append('Di atas SMA50')
        if sma20 > sma50:                     score += 10; signals.append('SMA20 > SMA50 (uptrend)')

        # Momentum (25 pts)
        if rsi < 35:                          score += 15; signals.append(f'RSI oversold ({rsi:.0f})')
        elif 35 <= rsi <= 55:                 score += 10; signals.append(f'RSI zona beli ({rsi:.0f})')
        if macd_cross:                        score += 10; signals.append('MACD bullish cross ⚡')
        elif macd_val > macd_sig:             score +=  5; signals.append('MACD > signal')

        # Volume (25 pts)
        if vol_ratio >= 3.0:                  score += 25; signals.append(f'Vol spike BESAR {vol_ratio:.1f}x 🚨')
        elif vol_ratio >= 2.0:                score += 15; signals.append(f'Vol anomali {vol_ratio:.1f}x')
        elif vol_ratio >= 1.5:                score += 8;  signals.append(f'Vol tinggi {vol_ratio:.1f}x')

        # Bandarmologi (20 pts)
        if obv_trend == 'UP':                 score += 10; signals.append('OBV naik (akumulasi)')
        if ad_trend  == 'UP':                 score += 5;  signals.append('A/D Line naik')
        if obv_slope > 0 and ad_trend=='UP':  score += 5;  signals.append('Smart money masuk')

        # Bollinger (10 pts)
        if bb_pos < 0.15:                     score += 10; signals.append('Dekat BB bawah (oversold BB)')
        elif bb_pos < 0.3:                    score +=  5; signals.append('Zona BB bawah')

        # Candle bonus
        if is_hammer and is_green:            score += 5;  signals.append('Hammer bullish 🔨')
        if price_1d > 0 and vol_ratio > 1.5: score += 5;  signals.append('Up day + vol tinggi')

        # ── Rekomendasi ────────────────────────────────────────────────
        if score >= 75:    rec = 'STRONG BUY';  rec_color = '🟢🟢'
        elif score >= 55:  rec = 'BUY';         rec_color = '🟢'
        elif score >= 38:  rec = 'NEUTRAL';     rec_color = '🟡'
        elif score >= 22:  rec = 'WEAK SELL';   rec_color = '🔴'
        else:              rec = 'SELL';        rec_color = '🔴🔴'

        # Bandarmologi status
        if obv_trend == 'UP' and ad_trend == 'UP' and price > sma20:
            bandar_status = 'AKUMULASI'
        elif obv_trend == 'DOWN' and ad_trend == 'DOWN' and price < sma20:
            bandar_status = 'DISTRIBUSI'
        else:
            bandar_status = 'NETRAL'

        return {
            'Symbol':        symbol,
            'Nama':          SAHAM_INDONESIA.get(symbol, symbol),
            'Harga':         price,
            'Change_1D':     price_1d,
            'Change_1W':     price_1w,
            'Change_1M':     price_1mo,
            'RSI':           rsi,
            'Stoch_K':       stoch_k,
            'MACD_Cross':    macd_cross,
            'MACD_Val':      macd_val,
            'Vol_Ratio':     vol_ratio,
            'Vol_Trend':     vol_trend,
            'Vol_Anomaly':   vol_ratio >= 2.0,
            'OBV_Trend':     obv_trend,
            'AD_Trend':      ad_trend,
            'Bandar':        bandar_status,
            'BB_Pos':        bb_pos,
            'BB_Width':      bb_pct,
            'Score':         score,
            'Rekomendasi':   rec,
            'Rec_Color':     rec_color,
            'Sinyal':        ', '.join(signals[:5]),
            'Support':       support,
            'Resistance':    resistance,
            'ATR':           atr,
            'SMA20':         sma20,
            'SMA50':         sma50,
            'Top_Gainer':    is_top_gainer,
            'Top_Loser':     is_top_loser,
        }
    except Exception:
        return None


def run_scanner(symbols_to_scan, progress_bar, status_text):
    """Scan list saham dengan delay anti-rate-limit"""
    results = []
    total   = len(symbols_to_scan)
    failed  = 0

    for i, sym in enumerate(symbols_to_scan):
        status_text.markdown(
            f"🔍 Scanning **{sym}** ({i+1}/{total}) — "
            f"✅ Berhasil: {len(results)} | ❌ Gagal: {failed}"
        )
        progress_bar.progress((i + 1) / total)

        result = quick_scan_stock(sym)
        if result:
            results.append(result)
        else:
            failed += 1

        # Delay adaptif: lebih lambat setiap 50 saham agar tidak kena rate limit
        if (i + 1) % 50 == 0:
            time.sleep(random.uniform(3.0, 5.0))
        else:
            time.sleep(random.uniform(0.25, 0.55))

    return pd.DataFrame(results) if results else pd.DataFrame()


def render_scanner_tab():
    """Render tab scanner lengkap dengan AI Analyst (Groq)"""
    st.markdown('<div class="tab-subheader">🔭 Stock Scanner — Scan Massal + AI Analyst (Groq)</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="info-box">📌 Scanner otomatis menghitung RSI, MACD, Volume Anomali, Bandarmologi (OBV/A/D), '
        'Bollinger Bands, Top Gainer/Loser pada semua saham IDX — lalu AI Groq memberikan insight mendalam.</div>',
        unsafe_allow_html=True
    )

    # ── Groq API Key — auto-load dari Streamlit Secrets (silent) ───────────
    groq_key = st.secrets.get("GROQ_API_KEY", "")

    # Model selector ringkas — hanya tampil, tidak ada notifikasi
    with st.expander('⚙️ Pengaturan Model AI', expanded=False):
        groq_model = st.selectbox('Model Groq AI:', [
            'llama3-8b-8192',
            'llama3-70b-8192',
            'mixtral-8x7b-32768',
            'gemma2-9b-it',
        ], help='llama3-70b lebih cerdas, llama3-8b lebih cepat')
        if not groq_key:
            manual_key = st.text_input('API Key (jika belum di Secrets):', type='password', placeholder='gsk_...')
            if manual_key.strip():
                groq_key = manual_key.strip()
    if 'groq_model' not in dir():
        groq_model = 'llama3-8b-8192'
    st.markdown('---')

    # ── Pengaturan scanner ─────────────────────────────────────────────────
    cfg1, cfg2, cfg3, cfg4 = st.columns(4)

    with cfg1:
        scan_mode = st.selectbox('Mode Scan:', [
            'LQ45 & Blue Chip (cepat)',
            'Custom (pilih sendiri)',
            'Semua Saham IDX (lambat ~15 menit)',
        ])

    with cfg2:
        filter_rec = st.multiselect('Filter Sinyal:', [
            'STRONG BUY', 'BUY', 'NEUTRAL', 'WEAK SELL', 'SELL'
        ], default=['STRONG BUY', 'BUY'])

    with cfg3:
        filter_bandar = st.selectbox('Filter Bandarmologi:', [
            'Semua', 'AKUMULASI', 'DISTRIBUSI', 'NETRAL'
        ])

    with cfg4:
        filter_vol   = st.checkbox('🚨 Volume Anomali saja (≥2x)', value=False)
        filter_gain  = st.checkbox('📈 Top Gainer saja (≥+3%)',   value=False)
        filter_loss  = st.checkbox('📉 Top Loser saja (≤-3%)',    value=False)
        sort_by      = st.selectbox('Urutkan berdasarkan:', [
            'Score', 'Change_1D', 'Vol_Ratio', 'RSI', 'Change_1W', 'Change_1M'
        ])

    # ── Pilihan saham ──────────────────────────────────────────────────────
    if scan_mode == 'Custom (pilih sendiri)':
        custom_picks = st.multiselect(
            'Pilih saham yang ingin di-scan (maks 150):',
            options=list(SAHAM_INDONESIA.keys()),
            default=BLUECHIP_LIST[:20],
            format_func=lambda x: f"{x} – {SAHAM_INDONESIA[x]}",
        )
        symbols_to_scan = custom_picks[:150]
    elif scan_mode == 'LQ45 & Blue Chip (cepat)':
        symbols_to_scan = BLUECHIP_LIST
        st.info(f'📋 Akan scan **{len(symbols_to_scan)}** saham LQ45 & Blue Chip (~1-2 menit)')
    else:
        symbols_to_scan = list(SAHAM_INDONESIA.keys())
        st.warning(
            f'⚠️ Scan semua **{len(symbols_to_scan)}** saham IDX. '
            f'Estimasi waktu ~{len(symbols_to_scan)//4} menit. '
            f'Pastikan koneksi internet stabil dan jangan tutup browser!'
        )

    # ── Tombol scan ────────────────────────────────────────────────────────
    st.markdown('---')
    btn1, btn2, btn3 = st.columns([1.5, 1.5, 4])
    with btn1:
        start_scan = st.button('🚀 Mulai Scan', use_container_width=True, type='primary')
    with btn2:
        clear_scan = st.button('🗑️ Hapus Hasil', use_container_width=True)
    with btn3:
        if 'scanner_results' in st.session_state:
            n = len(st.session_state['scanner_results'])
            st.success(f"✅ Cache hasil: {n} saham. Klik Mulai Scan untuk refresh.")

    if clear_scan:
        st.session_state.pop('scanner_results', None)
        st.session_state.pop('ai_market_analysis', None)
        st.rerun()

    # ── Eksekusi scan ──────────────────────────────────────────────────────
    if start_scan:
        if not symbols_to_scan:
            st.warning('Pilih minimal 1 saham.')
        else:
            st.session_state.pop('scanner_results', None)
            st.session_state.pop('ai_market_analysis', None)
            prog  = st.progress(0)
            stxt  = st.empty()
            t0    = time.time()

            df_results = run_scanner(symbols_to_scan, prog, stxt)

            elapsed = time.time() - t0
            prog.empty()
            stxt.empty()

            if not df_results.empty:
                st.session_state['scanner_results'] = df_results
                st.success(
                    f'✅ Scan selesai dalam {elapsed:.0f} detik! '
                    f'{len(df_results)}/{len(symbols_to_scan)} saham berhasil dianalisis.'
                )
            else:
                st.error('❌ Tidak ada data berhasil diambil. Tunggu 2 menit lalu coba lagi.')

    # ── Tampilkan hasil ────────────────────────────────────────────────────
    if 'scanner_results' not in st.session_state:
        return

    df_all = st.session_state['scanner_results'].copy()
    df_res = df_all.copy()

    # Terapkan filter
    if filter_rec:
        df_res = df_res[df_res['Rekomendasi'].isin(filter_rec)]
    if filter_bandar != 'Semua':
        df_res = df_res[df_res['Bandar'] == filter_bandar]
    if filter_vol:
        df_res = df_res[df_res['Vol_Anomaly']]
    if filter_gain:
        df_res = df_res[df_res['Top_Gainer']]
    if filter_loss:
        df_res = df_res[df_res['Top_Loser']]

    asc    = sort_by == 'RSI'
    df_res = df_res.sort_values(sort_by, ascending=asc)

    if df_res.empty:
        st.info('Tidak ada saham yang memenuhi filter. Coba longgarkan kriteria.')
        return

    # ────────────────────────────────────────────────────────────────────────
    # SUB-TAB HASIL
    # ────────────────────────────────────────────────────────────────────────
    stab1, stab2, stab3, stab4, stab5, stab6 = st.tabs([
        '📊 Ringkasan & Tabel',
        '📈 Top Gainer / Loser',
        '🚨 Volume Anomali',
        '🕵️ Bandarmologi',
        '🎯 BUY/SELL Signal',
        '🤖 AI Analyst (Groq)',
    ])

    # ── SUB-TAB 1: Ringkasan & Tabel ──────────────────────────────────────
    with stab1:
        m1,m2,m3,m4,m5,m6 = st.columns(6)
        with m1: st.metric('STRONG BUY 🟢🟢', len(df_all[df_all['Rekomendasi']=='STRONG BUY']))
        with m2: st.metric('BUY 🟢',          len(df_all[df_all['Rekomendasi']=='BUY']))
        with m3: st.metric('NEUTRAL 🟡',      len(df_all[df_all['Rekomendasi']=='NEUTRAL']))
        with m4: st.metric('SELL 🔴',         len(df_all[df_all['Rekomendasi'].isin(['SELL','WEAK SELL'])]))
        with m5: st.metric('Vol Anomali 🚨',  len(df_all[df_all['Vol_Anomaly']]))
        with m6: st.metric('Akumulasi 🕵️',   len(df_all[df_all['Bandar']=='AKUMULASI']))

        st.markdown(f'**Menampilkan {len(df_res)} saham (dari {len(df_all)} hasil scan)**')

        disp = df_res[[
            'Rec_Color','Symbol','Nama','Harga','Change_1D','Change_1W','Change_1M',
            'Score','RSI','Vol_Ratio','Bandar','Sinyal'
        ]].rename(columns={
            'Rec_Color':'','Symbol':'Kode','Nama':'Nama Perusahaan',
            'Harga':'Harga','Change_1D':'1D%','Change_1W':'1W%','Change_1M':'1M%',
            'Score':'Score','RSI':'RSI','Vol_Ratio':'Vol Ratio','Bandar':'Bandarmologi','Sinyal':'Sinyal'
        }).copy()
        disp['Harga']    = disp['Harga'].apply(lambda x: f'Rp {x:,.0f}')
        disp['1D%']      = disp['1D%'].apply(lambda x: f'{x:+.2f}%')
        disp['1W%']      = disp['1W%'].apply(lambda x: f'{x:+.2f}%')
        disp['1M%']      = disp['1M%'].apply(lambda x: f'{x:+.2f}%')
        disp['RSI']      = disp['RSI'].apply(lambda x: f'{x:.1f}')
        disp['Vol Ratio']= disp['Vol Ratio'].apply(lambda x: f'{x:.2f}x')
        disp['Score']    = disp['Score'].apply(lambda x: f'{x}/100')
        st.dataframe(disp, use_container_width=True, hide_index=True, height=520)

        # Scatter: Score vs RSI
        st.subheader('🗺️ Peta Saham: Score vs RSI')
        cmap = {'STRONG BUY':'#00c853','BUY':'#64dd17','NEUTRAL':'#ffd600',
                'WEAK SELL':'#ff6d00','SELL':'#dd2c00'}
        fig_sc = go.Figure()
        for rec, grp in df_res.groupby('Rekomendasi'):
            fig_sc.add_trace(go.Scatter(
                x=grp['RSI'], y=grp['Score'], mode='markers+text',
                name=rec, text=grp['Symbol'].str.replace('.JK',''),
                textposition='top center', textfont=dict(size=9),
                marker=dict(size=9, color=cmap.get(rec,'#999')),
                hovertemplate='<b>%{text}</b><br>RSI:%{x:.1f} Score:%{y}<extra></extra>',
            ))
        fig_sc.add_vline(x=30, line_dash='dash', line_color='green', annotation_text='Oversold 30')
        fig_sc.add_vline(x=70, line_dash='dash', line_color='red',   annotation_text='Overbought 70')
        fig_sc.add_hline(y=55, line_dash='dot',  line_color='orange',annotation_text='Score 55')
        fig_sc.update_layout(height=520, xaxis_title='RSI', yaxis_title='Score',
                             legend_title='Rekomendasi', margin=dict(t=30))
        st.plotly_chart(fig_sc, use_container_width=True)

        # Download
        csv_dl = df_all.to_csv(index=False).encode('utf-8')
        st.download_button('📥 Download Semua Hasil (CSV)', data=csv_dl,
                           file_name=f'scanner_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                           mime='text/csv')

    # ── SUB-TAB 2: Top Gainer / Loser ─────────────────────────────────────
    with stab2:
        st.subheader('📈 Top Gainer & Loser Hari Ini')
        g1, g2 = st.columns(2)

        top_gain = df_all.nlargest(15, 'Change_1D')
        top_loss = df_all.nsmallest(15, 'Change_1D')

        with g1:
            st.markdown('### 🟢 Top 15 Gainer')
            fig_g = go.Figure(go.Bar(
                y=top_gain['Symbol'].str.replace('.JK',''),
                x=top_gain['Change_1D'], orientation='h',
                marker_color='#00c853',
                text=top_gain['Change_1D'].apply(lambda x: f'{x:+.2f}%'),
                textposition='outside',
                hovertext=top_gain['Nama'],
            ))
            fig_g.update_layout(height=480, xaxis_title='Perubahan %',
                                margin=dict(l=10,r=60))
            st.plotly_chart(fig_g, use_container_width=True)

            st.dataframe(top_gain[['Symbol','Nama','Harga','Change_1D','Vol_Ratio','RSI','Rekomendasi']
                         ].rename(columns={'Change_1D':'1D%','Vol_Ratio':'Vol Ratio'
                         }).assign(**{
                             'Harga': top_gain['Harga'].apply(lambda x: f'Rp {x:,.0f}'),
                             '1D%': top_gain['Change_1D'].apply(lambda x: f'{x:+.2f}%'),
                             'Vol Ratio': top_gain['Vol_Ratio'].apply(lambda x: f'{x:.1f}x'),
                             'RSI': top_gain['RSI'].apply(lambda x: f'{x:.0f}'),
                         }), use_container_width=True, hide_index=True)

        with g2:
            st.markdown('### 🔴 Top 15 Loser')
            fig_l = go.Figure(go.Bar(
                y=top_loss['Symbol'].str.replace('.JK',''),
                x=top_loss['Change_1D'], orientation='h',
                marker_color='#dd2c00',
                text=top_loss['Change_1D'].apply(lambda x: f'{x:+.2f}%'),
                textposition='outside',
                hovertext=top_loss['Nama'],
            ))
            fig_l.update_layout(height=480, xaxis_title='Perubahan %',
                                margin=dict(l=10,r=60))
            st.plotly_chart(fig_l, use_container_width=True)

            st.dataframe(top_loss[['Symbol','Nama','Harga','Change_1D','Vol_Ratio','RSI','Rekomendasi']
                         ].rename(columns={'Change_1D':'1D%','Vol_Ratio':'Vol Ratio'
                         }).assign(**{
                             'Harga': top_loss['Harga'].apply(lambda x: f'Rp {x:,.0f}'),
                             '1D%': top_loss['Change_1D'].apply(lambda x: f'{x:+.2f}%'),
                             'Vol Ratio': top_loss['Vol_Ratio'].apply(lambda x: f'{x:.1f}x'),
                             'RSI': top_loss['RSI'].apply(lambda x: f'{x:.0f}'),
                         }), use_container_width=True, hide_index=True)

        # 1W & 1M
        st.markdown('---')
        w1, w2 = st.columns(2)
        with w1:
            st.subheader('📅 Top Gainer 1 Minggu')
            top_1w = df_all.nlargest(10,'Change_1W')[['Symbol','Nama','Change_1W','Change_1D','RSI']]
            top_1w['Change_1W'] = top_1w['Change_1W'].apply(lambda x: f'{x:+.2f}%')
            top_1w['Change_1D'] = top_1w['Change_1D'].apply(lambda x: f'{x:+.2f}%')
            top_1w['RSI']       = top_1w['RSI'].apply(lambda x: f'{x:.0f}')
            st.dataframe(top_1w, use_container_width=True, hide_index=True)
        with w2:
            st.subheader('📅 Top Gainer 1 Bulan')
            top_1m = df_all.nlargest(10,'Change_1M')[['Symbol','Nama','Change_1M','Change_1D','RSI']]
            top_1m['Change_1M'] = top_1m['Change_1M'].apply(lambda x: f'{x:+.2f}%')
            top_1m['Change_1D'] = top_1m['Change_1D'].apply(lambda x: f'{x:+.2f}%')
            top_1m['RSI']       = top_1m['RSI'].apply(lambda x: f'{x:.0f}')
            st.dataframe(top_1m, use_container_width=True, hide_index=True)

    # ── SUB-TAB 3: Volume Anomali ──────────────────────────────────────────
    with stab3:
        st.subheader('🚨 Deteksi Volume Anomali')
        vol_df = df_all.sort_values('Vol_Ratio', ascending=False)

        v1, v2, v3 = st.columns(3)
        with v1: st.metric('Vol ≥ 5x (Extreme)', len(vol_df[vol_df['Vol_Ratio']>=5]))
        with v2: st.metric('Vol ≥ 2x (Anomali)',  len(vol_df[vol_df['Vol_Ratio']>=2]))
        with v3: st.metric('Vol ≥ 1.5x (Tinggi)', len(vol_df[vol_df['Vol_Ratio']>=1.5]))

        top_vol = vol_df.head(20)
        fig_vol = go.Figure(go.Bar(
            y=top_vol['Symbol'].str.replace('.JK',''),
            x=top_vol['Vol_Ratio'], orientation='h',
            marker_color=['#b71c1c' if v>=5 else '#e53935' if v>=3 else '#fb8c00' if v>=2 else '#fdd835'
                         for v in top_vol['Vol_Ratio']],
            text=top_vol['Vol_Ratio'].apply(lambda x: f'{x:.1f}x'),
            textposition='outside',
            hovertext=top_vol.apply(lambda r: f"{r['Nama']}<br>Change: {r['Change_1D']:+.2f}%", axis=1),
        ))
        fig_vol.add_vline(x=2, line_dash='dash', line_color='red', annotation_text='Anomali (2x)')
        fig_vol.update_layout(height=550, xaxis_title='Volume Ratio vs Avg 20 Hari',
                              margin=dict(l=10,r=80))
        st.plotly_chart(fig_vol, use_container_width=True)

        st.subheader('📋 Detail Volume Anomali (≥ 1.5x)')
        vol_detail = vol_df[vol_df['Vol_Ratio']>=1.5][[
            'Symbol','Nama','Harga','Change_1D','Vol_Ratio','RSI','Bandar','Rekomendasi','Sinyal'
        ]].copy()
        vol_detail['Harga']     = vol_detail['Harga'].apply(lambda x: f'Rp {x:,.0f}')
        vol_detail['Change_1D'] = vol_detail['Change_1D'].apply(lambda x: f'{x:+.2f}%')
        vol_detail['Vol_Ratio'] = vol_detail['Vol_Ratio'].apply(lambda x: f'{x:.2f}x')
        vol_detail['RSI']       = vol_detail['RSI'].apply(lambda x: f'{x:.0f}')
        st.dataframe(vol_detail, use_container_width=True, hide_index=True, height=400)

    # ── SUB-TAB 4: Bandarmologi ───────────────────────────────────────────
    with stab4:
        st.subheader('🕵️ Scanner Bandarmologi — Deteksi Akumulasi & Distribusi Smart Money')

        b1, b2, b3 = st.columns(3)
        akum_df = df_all[df_all['Bandar']=='AKUMULASI'].sort_values('Score', ascending=False)
        dist_df = df_all[df_all['Bandar']=='DISTRIBUSI'].sort_values('Score')
        netral_df = df_all[df_all['Bandar']=='NETRAL']

        with b1: st.metric('🟢 Akumulasi',  len(akum_df))
        with b2: st.metric('🔴 Distribusi', len(dist_df))
        with b3: st.metric('🟡 Netral',     len(netral_df))

        bc1, bc2 = st.columns(2)
        with bc1:
            st.markdown('### 🟢 Top Akumulasi (Smart Money Masuk)')
            top_akum = akum_df.head(15)
            fig_ak = go.Figure(go.Bar(
                y=top_akum['Symbol'].str.replace('.JK',''),
                x=top_akum['Score'], orientation='h',
                marker_color='#00c853',
                text=top_akum['Score'].apply(lambda x: f'{x}/100'),
                textposition='inside',
                hovertext=top_akum['Nama'],
            ))
            fig_ak.update_layout(height=450, xaxis_title='Score',
                                 xaxis_range=[0,100], margin=dict(l=10))
            st.plotly_chart(fig_ak, use_container_width=True)

            akum_disp = akum_df.head(15)[['Symbol','Nama','Harga','Change_1D','Vol_Ratio','RSI','OBV_Trend','AD_Trend']].copy()
            akum_disp['Harga']     = akum_disp['Harga'].apply(lambda x: f'Rp {x:,.0f}')
            akum_disp['Change_1D'] = akum_disp['Change_1D'].apply(lambda x: f'{x:+.2f}%')
            akum_disp['Vol_Ratio'] = akum_disp['Vol_Ratio'].apply(lambda x: f'{x:.1f}x')
            akum_disp['RSI']       = akum_disp['RSI'].apply(lambda x: f'{x:.0f}')
            st.dataframe(akum_disp, use_container_width=True, hide_index=True)

        with bc2:
            st.markdown('### 🔴 Top Distribusi (Smart Money Keluar)')
            top_dist = dist_df.head(15)
            fig_di = go.Figure(go.Bar(
                y=top_dist['Symbol'].str.replace('.JK',''),
                x=top_dist['Score'], orientation='h',
                marker_color='#dd2c00',
                text=top_dist['Score'].apply(lambda x: f'{x}/100'),
                textposition='inside',
                hovertext=top_dist['Nama'],
            ))
            fig_di.update_layout(height=450, xaxis_title='Score',
                                 xaxis_range=[0,100], margin=dict(l=10))
            st.plotly_chart(fig_di, use_container_width=True)

            dist_disp = dist_df.head(15)[['Symbol','Nama','Harga','Change_1D','Vol_Ratio','RSI','OBV_Trend','AD_Trend']].copy()
            dist_disp['Harga']     = dist_disp['Harga'].apply(lambda x: f'Rp {x:,.0f}')
            dist_disp['Change_1D'] = dist_disp['Change_1D'].apply(lambda x: f'{x:+.2f}%')
            dist_disp['Vol_Ratio'] = dist_disp['Vol_Ratio'].apply(lambda x: f'{x:.1f}x')
            dist_disp['RSI']       = dist_disp['RSI'].apply(lambda x: f'{x:.0f}')
            st.dataframe(dist_disp, use_container_width=True, hide_index=True)

    # ── SUB-TAB 5: BUY/SELL Signal ────────────────────────────────────────
    with stab5:
        st.subheader('🎯 Ranking BUY / SELL Signal')

        buy_df  = df_all[df_all['Rekomendasi'].isin(['STRONG BUY','BUY'])].sort_values('Score', ascending=False)
        sell_df = df_all[df_all['Rekomendasi'].isin(['SELL','WEAK SELL'])].sort_values('Score')

        s1, s2 = st.columns(2)
        with s1:
            st.markdown('### 🟢 TOP BUY SIGNAL')
            top_buy = buy_df.head(20)
            fig_buy = go.Figure(go.Bar(
                y=top_buy['Symbol'].str.replace('.JK',''),
                x=top_buy['Score'], orientation='h',
                marker_color=['#00c853' if r=='STRONG BUY' else '#64dd17'
                             for r in top_buy['Rekomendasi']],
                text=top_buy.apply(lambda r: f"{r['Rekomendasi']} ({r['Score']})", axis=1),
                textposition='inside',
                hovertext=top_buy['Sinyal'],
            ))
            fig_buy.update_layout(height=520, xaxis_title='Score',
                                  xaxis_range=[0,100], margin=dict(l=10))
            st.plotly_chart(fig_buy, use_container_width=True)

        with s2:
            st.markdown('### 🔴 TOP SELL SIGNAL')
            top_sell = sell_df.head(20)
            if not top_sell.empty:
                fig_sell = go.Figure(go.Bar(
                    y=top_sell['Symbol'].str.replace('.JK',''),
                    x=top_sell['Score'], orientation='h',
                    marker_color=['#dd2c00' if r=='SELL' else '#ff6d00'
                                 for r in top_sell['Rekomendasi']],
                    text=top_sell.apply(lambda r: f"{r['Rekomendasi']} ({r['Score']})", axis=1),
                    textposition='inside',
                    hovertext=top_sell['Sinyal'],
                ))
                fig_sell.update_layout(height=520, xaxis_title='Score',
                                       xaxis_range=[0,100], margin=dict(l=10))
                st.plotly_chart(fig_sell, use_container_width=True)
            else:
                st.info('Tidak ada sinyal SELL dari hasil scan ini.')

        # Tabel buy detail
        st.markdown('---')
        st.subheader('📋 Detail Top BUY dengan Level Entry')
        buy_detail = buy_df.head(20).copy()
        buy_detail['Entry']     = buy_detail['Harga'].apply(lambda x: f'Rp {x:,.0f}')
        buy_detail['Stop Loss'] = (buy_detail['Support'] * 0.985).apply(lambda x: f'Rp {x:,.0f}')
        buy_detail['Target']    = (buy_detail['Resistance'] * 1.02).apply(lambda x: f'Rp {x:,.0f}')
        buy_detail['Harga']     = buy_detail['Harga'].apply(lambda x: f'Rp {x:,.0f}')
        buy_detail['Change_1D'] = buy_detail['Change_1D'].apply(lambda x: f'{x:+.2f}%')
        buy_detail['RSI']       = buy_detail['RSI'].apply(lambda x: f'{x:.0f}')
        buy_detail['Vol_Ratio'] = buy_detail['Vol_Ratio'].apply(lambda x: f'{x:.1f}x')
        st.dataframe(buy_detail[[
            'Symbol','Nama','Harga','Change_1D','RSI','Vol_Ratio',
            'Bandar','Entry','Stop Loss','Target','Sinyal'
        ]], use_container_width=True, hide_index=True)

    # ── SUB-TAB 6: AI Analyst (Groq) ──────────────────────────────────────
    with stab6:
        st.subheader('🤖 AI Analyst — Powered by Groq (LLaMA / Mixtral)')

        if not groq_key:
            st.warning(
                '⚠️ Masukkan **Groq API Key** di bagian atas halaman scanner untuk mengaktifkan fitur AI.\n\n'
                'API key gratis di [console.groq.com](https://console.groq.com)'
            )
        else:
            # ── Analisis pasar keseluruhan ─────────────────────────────
            st.markdown('### 🌡️ Analisis Pasar Keseluruhan (Market Overview)')

            col_ai1, col_ai2 = st.columns([1, 3])
            with col_ai1:
                run_market_ai = st.button('🔍 Analisis Pasar Sekarang', use_container_width=True, type='primary')
            with col_ai2:
                if 'ai_market_analysis' in st.session_state:
                    st.success('✅ Analisis pasar sudah tersedia (scroll ke bawah)')

            if run_market_ai:
                with st.spinner('🤖 AI sedang menganalisis kondisi pasar...'):
                    prompt  = build_scanner_prompt(df_all)
                    ai_resp = groq_ai_analyze(prompt, groq_key, groq_model)
                    st.session_state['ai_market_analysis'] = ai_resp

            if 'ai_market_analysis' in st.session_state:
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.markdown(st.session_state['ai_market_analysis'])
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('---')

            # ── Analisis saham individual ──────────────────────────────
            st.markdown('### 🎯 Analisis AI untuk Saham Individual')
            st.info('Pilih saham dari hasil scanner untuk mendapatkan analisis AI mendalam')

            ai_cols = st.columns([2, 1])
            with ai_cols[0]:
                sel_sym = st.selectbox(
                    'Pilih saham:',
                    options=df_all['Symbol'].tolist(),
                    format_func=lambda x: f"{x} — {df_all[df_all['Symbol']==x]['Nama'].values[0]} "
                                         f"(Score: {df_all[df_all['Symbol']==x]['Score'].values[0]}, "
                                         f"{df_all[df_all['Symbol']==x]['Rekomendasi'].values[0]})",
                )
            with ai_cols[1]:
                run_stock_ai = st.button('🤖 Analisis Saham Ini', use_container_width=True, type='primary')

            if run_stock_ai and sel_sym:
                row = df_all[df_all['Symbol'] == sel_sym].iloc[0]
                with st.spinner(f'🤖 AI menganalisis {sel_sym}...'):
                    prompt   = build_single_stock_prompt(row)
                    ai_stock = groq_ai_analyze(prompt, groq_key, groq_model)

                st.markdown(f'#### Analisis AI untuk {sel_sym} — {row["Nama"]}')

                # Metric ringkas di atas
                mc1,mc2,mc3,mc4 = st.columns(4)
                with mc1: st.metric('Score', f"{row['Score']}/100")
                with mc2: st.metric('RSI',   f"{row['RSI']:.1f}")
                with mc3: st.metric('Vol Ratio', f"{row['Vol_Ratio']:.2f}x")
                with mc4: st.metric('Bandarmologi', row['Bandar'])

                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown(ai_stock)
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Quick scan 5 saham teratas ─────────────────────────────
            st.markdown('---')
            st.markdown('### ⚡ Analisis Cepat Top 5 BUY Signal')
            if st.button('🚀 Analisis Top 5 Sekaligus', use_container_width=False):
                top5 = df_all[df_all['Rekomendasi'].isin(['STRONG BUY','BUY'])].nlargest(5,'Score')
                if top5.empty:
                    st.info('Tidak ada sinyal BUY dari hasil scan.')
                else:
                    for _, row in top5.iterrows():
                        with st.spinner(f'Menganalisis {row["Symbol"]}...'):
                            p  = build_single_stock_prompt(row)
                            ar = groq_ai_analyze(p, groq_key, groq_model)
                        with st.expander(
                            f"{row['Rec_Color']} {row['Symbol']} — {row['Nama']} "
                            f"(Score: {row['Score']}, RSI: {row['RSI']:.0f})"
                        ):
                            st.markdown(ar)
                        time.sleep(1)  # jeda antar request Groq


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    st.markdown('<h1 class="main-header">📈 ANALISIS SAHAM INDONESIA ULTIMATE</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Technical Analysis + Bandarmologi + Broker Summary + Transaction Analysis</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header('⚙️ Pengaturan Analisis')
    
    # Pilih strategi
    strategy = st.sidebar.selectbox(
        'Strategi Trading:',
        ['Scalping', 'Intraday', 'Investasi'],
        help='Scalping: 1-15 menit | Intraday: 30 menit - 4 jam | Investasi: Daily/Swing'
    )
    
    # Search / filter saham
    search_query = st.sidebar.text_input('🔍 Cari Saham (kode/nama):', placeholder='contoh: BBCA atau Bank Central')
    
    if search_query:
        filtered = {
            k: v for k, v in SAHAM_INDONESIA.items()
            if search_query.upper() in k or search_query.lower() in v.lower()
        }
        stock_options = filtered if filtered else SAHAM_INDONESIA
    else:
        stock_options = SAHAM_INDONESIA
    
    selected_stock = st.sidebar.selectbox(
        f'Pilih Saham ({len(stock_options)} tersedia):',
        options=list(stock_options.keys()),
        format_func=lambda x: f"{x} - {stock_options[x]}"
    )
    
    # Timeframe berdasarkan strategi
    if strategy == 'Scalping':
        period = st.sidebar.selectbox('Periode:', ['1d', '5d', '1mo'], index=1)
        interval = st.sidebar.selectbox('Interval:', ['1m', '5m', '15m', '30m'], index=2)
    elif strategy == 'Intraday':
        period = st.sidebar.selectbox('Periode:', ['5d', '1mo', '3mo'], index=1)
        interval = st.sidebar.selectbox('Interval:', ['15m', '30m', '1h', '4h'], index=2)
    else:
        period = st.sidebar.selectbox('Periode:', ['1mo', '3mo', '6mo', '1y', '2y'], index=2)
        interval = st.sidebar.selectbox('Interval:', ['1d', '1wk', '1mo'], index=0)
    
    # Input Data Manual (Real-time)
    st.sidebar.markdown('---')
    st.sidebar.subheader('📥 Input Data Real-time Anda')
    
    with st.sidebar.expander('Input Data Broker Hari Ini'):
        manual_data = load_manual_data()
        
        col1, col2 = st.columns(2)
        with col1:
            foreign_buy = st.number_input('Foreign Buy (Miliar)', min_value=0.0, value=0.0, step=0.1)
            local_buy = st.number_input('Local Buy (Miliar)', min_value=0.0, value=0.0, step=0.1)
        with col2:
            foreign_sell = st.number_input('Foreign Sell (Miliar)', min_value=0.0, value=0.0, step=0.1)
            local_sell = st.number_input('Local Sell (Miliar)', min_value=0.0, value=0.0, step=0.1)
        
        big_lot_buy = st.number_input('Big Lot Buy (Juta)', min_value=0, value=0, step=100)
        big_lot_sell = st.number_input('Big Lot Sell (Juta)', min_value=0, value=0, step=100)
        
        if st.button('💾 Simpan Data'):
            manual_data[selected_stock] = {
                'timestamp': datetime.now().isoformat(),
                'foreign': {'buy': foreign_buy, 'sell': foreign_sell, 'net': foreign_buy - foreign_sell},
                'local': {'buy': local_buy, 'sell': local_sell, 'net': local_buy - local_sell},
                'big_lot': {'buy': big_lot_buy, 'sell': big_lot_sell, 'net': big_lot_buy - big_lot_sell}
            }
            save_manual_data(manual_data)
            st.success('Data tersimpan!')
    
    # Info jumlah saham
    st.sidebar.markdown('---')
    st.sidebar.info(f'📊 Total: **{len(SAHAM_INDONESIA)}** saham tersedia')

    # Tips rate limit
    with st.sidebar.expander('⚠️ Jika muncul error Rate Limit'):
        st.markdown("""
        Yahoo Finance membatasi jumlah request.
        **Solusi:**
        - Tunggu 1-2 menit lalu coba lagi
        - Klik tombol **Clear Cache** di bawah
        - Ganti ke periode/interval yang berbeda
        - Coba saham lain terlebih dahulu
        """)
    
    if st.sidebar.button('🗑️ Clear Cache & Retry', use_container_width=True):
        st.cache_data.clear()
        st.success('Cache dibersihkan! Silakan analisis ulang.')
        st.rerun()

    # Tombol analisis
    analyze_button = st.sidebar.button('🔍 Analisis Lengkap', use_container_width=True)
    
    # Main Content
    if analyze_button or 'data_loaded' in st.session_state:
        if analyze_button:
            st.session_state.data_loaded = True
            st.session_state.symbol = selected_stock
            st.session_state.strategy = strategy
            st.session_state.period = period
            st.session_state.interval = interval
        
        symbol = st.session_state.get('symbol', selected_stock)
        current_strategy = st.session_state.get('strategy', strategy)
        
        with st.spinner(f'Menganalisis {symbol} - {SAHAM_INDONESIA.get(symbol, "")}...'):
            df = get_stock_data(symbol, period, interval)
            
            if df is not None and len(df) > 20:
                df = calculate_indicators(df)
                
                tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                    '📊 Technical Analysis',
                    '🎯 Strategy Signals',
                    '🕵️ Bandarmologi & Foreign Flow',
                    '📡 Foreign Net IDX (Nyata)',
                    '🏛️ Institutional Ownership',
                    '🔮 Hybrid Forecast',
                    '🔭 Stock Scanner',
                ])
                
                # ================================================================
                # TAB 1: TECHNICAL ANALYSIS
                # ================================================================
                with tab1:
                    st.markdown('<div class="tab-subheader">📊 Analisis Teknikal Lengkap</div>', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        current_price = df['Close'].iloc[-1]
                        st.metric('Harga Terakhir', f'Rp {current_price:,.0f}')
                    with col2:
                        change = (df['Close'].iloc[-1] / df['Close'].iloc[-2] - 1) * 100
                        st.metric('Perubahan', f'{change:.2f}%')
                    with col3:
                        st.metric('Volume', f'{df["Volume"].iloc[-1]:,.0f}')
                    with col4:
                        st.metric('RSI (14)', f'{df["RSI"].iloc[-1]:.1f}')
                    
                    fig = create_main_chart(df, symbol, current_strategy)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.subheader('📋 Ringkasan Indikator')
                    tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)
                    
                    with tech_col1:
                        st.markdown('**Moving Averages**')
                        st.markdown(f'SMA 20: Rp {df["SMA_20"].iloc[-1]:,.0f}')
                        st.markdown(f'SMA 50: Rp {df["SMA_50"].iloc[-1]:,.0f}')
                        st.markdown(f'SMA 200: Rp {df["SMA_200"].iloc[-1]:,.0f}')
                    
                    with tech_col2:
                        st.markdown('**Momentum**')
                        st.markdown(f'RSI: {df["RSI"].iloc[-1]:.1f}')
                        st.markdown(f'MACD: {df["MACD"].iloc[-1]:.2f}')
                        st.markdown(f'Stoch K: {df["Stoch_K"].iloc[-1]:.1f}')
                    
                    with tech_col3:
                        st.markdown('**Volatilitas**')
                        st.markdown(f'ATR: {df["ATR"].iloc[-1]:.0f}')
                        st.markdown(f'BB Width: {df["BB_Width"].iloc[-1]:.2f}')
                        st.markdown(f'ADX: {df["ADX"].iloc[-1]:.1f}')
                    
                    with tech_col4:
                        st.markdown('**Support/Resistance**')
                        st.markdown(f'Support: Rp {df["Support"].iloc[-1]:,.0f}')
                        st.markdown(f'Resistance: Rp {df["Resistance"].iloc[-1]:,.0f}')
                        st.markdown(f'Fib 61.8%: Rp {df["Fib_618"].iloc[-1]:,.0f}')
                
                # ================================================================
                # TAB 2: STRATEGY SIGNALS
                # ================================================================
                with tab2:
                    st.markdown('<div class="tab-subheader">🎯 Sinyal Strategi Trading</div>', unsafe_allow_html=True)
                    
                    signals = analyze_strategy(df, current_strategy)
                    
                    if signals:
                        signal_col1, signal_col2, signal_col3, signal_col4 = st.columns(4)
                        
                        with signal_col1:
                            if signals['rekomendasi'] == 'BUY':
                                st.markdown(f'<div class="metric-card"><h3 class="buy-signal">🟢 {signals["rekomendasi"]}</h3></div>', unsafe_allow_html=True)
                            elif signals['rekomendasi'] == 'SELL':
                                st.markdown(f'<div class="metric-card"><h3 class="sell-signal">🔴 {signals["rekomendasi"]}</h3></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="metric-card"><h3 class="neutral-signal">🟡 {signals["rekomendasi"]}</h3></div>', unsafe_allow_html=True)
                        
                        with signal_col2:
                            st.metric('Confidence', f"{signals['confidence']}%")
                        
                        with signal_col3:
                            if signals['risk_reward']:
                                st.metric('Risk:Reward', f"1:{signals['risk_reward']}")
                            else:
                                st.metric('Risk:Reward', 'N/A')
                        
                        with signal_col4:
                            trend = 'Uptrend' if df['SMA_50'].iloc[-1] > df['SMA_200'].iloc[-1] else 'Downtrend'
                            st.metric('Trend Jangka Panjang', trend)
                        
                        st.markdown('---')
                        st.subheader('🎯 Trading Plan')
                        
                        plan_col1, plan_col2, plan_col3 = st.columns(3)
                        with plan_col1:
                            st.markdown(f'<div class="info-box"><b>Entry:</b> Rp {signals["entry"]:,.0f}</div>' if signals["entry"] else '<div class="info-box"><b>Entry:</b> -</div>', unsafe_allow_html=True)
                        with plan_col2:
                            st.markdown(f'<div class="warning-box"><b>Stop Loss:</b> Rp {signals["stop_loss"]:,.0f}</div>' if signals["stop_loss"] else '<div class="warning-box"><b>Stop Loss:</b> -</div>', unsafe_allow_html=True)
                        with plan_col3:
                            st.markdown(f'<div class="success-box"><b>Take Profit:</b> Rp {signals["take_profit"]:,.0f}</div>' if signals["take_profit"] else '<div class="success-box"><b>Take Profit:</b> -</div>', unsafe_allow_html=True)
                        
                        st.subheader('📝 Alasan Sinyal')
                        for alasan in signals['alasan']:
                            st.markdown(f'- {alasan}')
                        
                        with st.expander('ℹ️ Tentang Strategi Ini'):
                            if current_strategy == 'Scalping':
                                st.markdown("""
                                **Strategi Scalping (1-15 menit)**
                                - Menggunakan EMA 12/26 untuk sinyal cepat
                                - Bollinger Bands untuk identifikasi overbought/oversold
                                - Volume spike untuk konfirmasi
                                - Target: 0.5-2% per trade
                                - Risk: Stop loss ketat (1.5x ATR)
                                """)
                            elif current_strategy == 'Intraday':
                                st.markdown("""
                                **Strategi Intraday (30 menit - 4 jam)**
                                - MACD signal line cross untuk momentum
                                - RSI overbought/oversold untuk timing
                                - ADX > 25 untuk filter trend kuat
                                - Target: 2-5% per trade
                                - Risk: Support/Resistance sebagai SL
                                """)
                            else:
                                st.markdown("""
                                **Strategi Investasi (Daily/Swing)**
                                - Golden/Death Cross untuk trend jangka panjang
                                - Fibonacci retracement untuk entry optimal
                                - SMA 50/200 untuk konfirmasi trend
                                - Target: 10-20% per posisi
                                - Risk: 2% di bawah support utama
                                """)
                
                # ================================================================
                # TAB 3: BANDARMOLOGI ENHANCED
                # ================================================================
                with tab3:
                    st.markdown('<div class="tab-subheader">🕵️ Bandarmologi Enhanced — OBV + A/D + CMF + MFI</div>', unsafe_allow_html=True)
                    st.markdown('<div class="info-box">📡 <b>Data Nyata</b> dari Yahoo Finance (delay ~15 mnt). Semua indikator dihitung dari harga & volume asli — bukan simulasi.</div>', unsafe_allow_html=True)

                    manual_data = load_manual_data()
                    bandar = analyze_bandarmology(df, symbol, manual_data)

                    if bandar:
                        ind = bandar["indicators"]
                        trend_color = ("#00c853" if "ACCUMULATION" in bandar["trend"]
                                      else "#dd2c00" if "DISTRIBUTION" in bandar["trend"]
                                      else "#ffd600")
                        st.markdown(
                            f'<div style="background:{trend_color}22;border-left:4px solid {trend_color};'
                            f'padding:12px 16px;border-radius:8px;margin-bottom:1rem;">'
                            f'<b style="font-size:1.1rem;">{bandar["trend"]}</b> | Score: <b>{bandar["strength"]}/100</b><br>'
                            f'<span>{bandar["interpretation"]}</span></div>', unsafe_allow_html=True
                        )
                        mc1,mc2,mc3,mc4 = st.columns(4)
                        with mc1: st.metric("OBV Trend",  ind["obv_trend"], "▲ Naik" if ind["obv_trend"]=="UP" else "▼ Turun")
                        with mc2: st.metric("A/D Line",   ind["ad_trend"],  "▲ Naik" if ind["ad_trend"]=="UP"  else "▼ Turun")
                        with mc3: st.metric("CMF (20)", f'{ind["cmf"]:+.3f}', ind["cmf_signal"])
                        with mc4: st.metric("MFI (14)", f'{ind["mfi"]:.1f}', ind["mfi_signal"])
                        st.markdown("---")

                        # 4-panel chart
                        fig_b = make_subplots(rows=4, cols=1, shared_xaxes=True,
                            vertical_spacing=0.03, row_heights=[0.40,0.20,0.20,0.20],
                            subplot_titles=("Harga + Volume","OBV + A/D (dinormalisasi)","CMF","MFI"))
                        fig_b.add_trace(go.Candlestick(
                            x=df.index,open=df["Open"],high=df["High"],low=df["Low"],close=df["Close"],
                            name="Harga",showlegend=False), row=1,col=1)
                        vc = ["green" if df["Close"].iloc[i]>=df["Open"].iloc[i] else "red" for i in range(len(df))]
                        fig_b.add_trace(go.Bar(x=df.index,y=df["Volume"],marker_color=vc,opacity=0.4,name="Volume",showlegend=False),row=1,col=1)

                        obv_s = bandar["_obv"]; ad_s = bandar["_ad"]
                        def norm(s):
                            mn,mx=s.min(),s.max(); return (s-mn)/(mx-mn+1e-9)*100
                        fig_b.add_trace(go.Scatter(x=df.index,y=norm(obv_s),name="OBV",line=dict(color="#1D9E75",width=1.5)),row=2,col=1)
                        fig_b.add_trace(go.Scatter(x=df.index,y=norm(ad_s),name="A/D",line=dict(color="#7F77DD",width=1.5,dash="dot")),row=2,col=1)

                        cmf_s = bandar["_cmf"]
                        cmf_c = ["#00c853" if v>0 else "#dd2c00" for v in cmf_s]
                        fig_b.add_trace(go.Bar(x=df.index,y=cmf_s,marker_color=cmf_c,name="CMF",showlegend=False),row=3,col=1)
                        fig_b.add_hline(y=0.1, line_dash="dash",line_color="green",row=3,col=1)
                        fig_b.add_hline(y=-0.1,line_dash="dash",line_color="red",  row=3,col=1)
                        fig_b.add_hline(y=0,   line_dash="dot", line_color="gray", row=3,col=1)

                        mfi_s = bandar["_mfi_raw"].fillna(50)
                        fig_b.add_trace(go.Scatter(x=df.index,y=mfi_s,name="MFI",
                            line=dict(color="#EF9F27",width=1.5),fill="tozeroy",fillcolor="rgba(239,159,39,0.1)"),row=4,col=1)
                        fig_b.add_hline(y=80,line_dash="dash",line_color="red",  annotation_text="OB 80",row=4,col=1)
                        fig_b.add_hline(y=20,line_dash="dash",line_color="green",annotation_text="OS 20",row=4,col=1)
                        fig_b.update_layout(height=720,xaxis_rangeslider_visible=False,showlegend=True)
                        st.plotly_chart(fig_b,use_container_width=True)

                        st.subheader("✅ Sinyal Terdeteksi")
                        sc1,sc2 = st.columns(2)
                        for i,sig in enumerate(ind["signals"]):
                            with sc1 if i%2==0 else sc2: st.markdown(f"✔ {sig}")

                        if ind["divergence"] != "TIDAK ADA":
                            dvc = "#00c853" if "BULLISH" in ind["divergence"] else "#dd2c00"
                            st.markdown(f'<div style="background:{dvc}22;border-left:4px solid {dvc};padding:10px 14px;border-radius:6px;margin-top:1rem;">⚡ <b>Divergence:</b> {ind["divergence"]}</div>',unsafe_allow_html=True)

                        st.markdown("---")
                        st.info(f'💡 **Rekomendasi:** {bandar["trading_implications"]}')

                        with st.expander("📖 Cara Membaca Indikator"):
                            st.markdown("""
**OBV:** Volume kumulatif berbasis arah harga. Naik = akumulasi, Turun = distribusi.
**A/D Line:** Mengukur posisi close vs high-low range. Lebih sensitif dari OBV.
**CMF > +0.1:** Tekanan beli kuat (akumulasi). **CMF < -0.1:** Tekanan jual (distribusi).
**MFI < 20:** Oversold → potensi beli. **MFI > 80:** Overbought → potensi jual.
**Divergence Bullish:** Harga lower low, OBV higher low → smart money masuk diam-diam.
**Divergence Bearish:** Harga higher high, OBV lower high → smart money keluar diam-diam.
                            """)

                # ================================================================
                # TAB 4: FOREIGN NET IDX (DATA NYATA)
                # ================================================================
                with tab4:
                    st.markdown('<div class="tab-subheader">📡 Foreign Net IDX — Data Transaksi Asing Harian</div>', unsafe_allow_html=True)
                    st.markdown('<div class="info-box">📊 <b>Sumber: IDX resmi</b> (idx.co.id) — Data foreign buy/sell per saham, update setiap akhir sesi perdagangan. Ini data NYATA, bukan simulasi.</div>', unsafe_allow_html=True)

                    with st.spinner("Mengambil data foreign net dari IDX..."):
                        fn_df = get_idx_foreign_net(symbol)

                    if fn_df is not None and not fn_df.empty:
                        # Metrics hari terakhir
                        latest = fn_df.iloc[0]
                        fn_val  = latest["Foreign_Net"]
                        fn_color = "🟢" if fn_val > 0 else "🔴"
                        m1,m2,m3,m4 = st.columns(4)
                        with m1: st.metric("Foreign Net (Terakhir)", f"{fn_color} {fn_val/1e9:.2f}B" if abs(fn_val)>1e9 else f"{fn_color} {fn_val/1e6:.1f}M", "Net Buy" if fn_val>0 else "Net Sell")
                        with m2: st.metric("Foreign Buy",  f"Rp {latest['Foreign_Buy']/1e9:.2f}B"  if latest["Foreign_Buy"]>1e9  else f"Rp {latest['Foreign_Buy']/1e6:.1f}M")
                        with m3: st.metric("Foreign Sell", f"Rp {latest['Foreign_Sell']/1e9:.2f}B" if latest["Foreign_Sell"]>1e9 else f"Rp {latest['Foreign_Sell']/1e6:.1f}M")
                        with m4: st.metric("Frekuensi", f"{int(latest['Freq']):,}")
                        st.markdown("---")

                        # Chart foreign net per hari
                        fig_fn = go.Figure()
                        fig_fn.add_trace(go.Bar(
                            x=fn_df["Tanggal"], y=fn_df["Foreign_Net"],
                            marker_color=["#00c853" if v>0 else "#dd2c00" for v in fn_df["Foreign_Net"]],
                            name="Foreign Net", text=[f"{'▲' if v>0 else '▼'} {v/1e9:.2f}B" if abs(v)>1e9 else f"{v/1e6:.1f}M" for v in fn_df["Foreign_Net"]],
                            textposition="outside"
                        ))
                        fig_fn.add_hline(y=0, line_color="gray", line_dash="dot")
                        fig_fn.update_layout(title=f"Foreign Net Flow — {symbol}", height=380,
                                             xaxis_title="Tanggal", yaxis_title="Net (Rp)")
                        st.plotly_chart(fig_fn, use_container_width=True)

                        # Tabel detail
                        st.subheader("📋 Data 10 Hari Terakhir")
                        fn_disp = fn_df.copy()
                        for col in ["Foreign_Buy","Foreign_Sell","Foreign_Net","Value"]:
                            fn_disp[col] = fn_disp[col].apply(lambda x: f"Rp {x/1e9:.2f}B" if abs(x)>1e9 else f"Rp {x/1e6:.1f}M")
                        fn_disp["Volume"] = fn_disp["Volume"].apply(lambda x: f"{x:,.0f}")
                        fn_disp["Freq"]   = fn_disp["Freq"].apply(lambda x: f"{x:,}")
                        st.dataframe(fn_disp.rename(columns={
                            "Tanggal":"Tanggal","Foreign_Buy":"Asing Beli","Foreign_Sell":"Asing Jual",
                            "Foreign_Net":"Net Asing","Volume":"Volume","Value":"Nilai","Freq":"Frekuensi"
                        }), use_container_width=True, hide_index=True)

                        # Analisis tren asing
                        net_vals = fn_df["Foreign_Net"].values
                        net_5d = net_vals[:5].sum()
                        trend_asing = "KONSISTEN BELI" if all(v>0 for v in net_vals[:5]) else "KONSISTEN JUAL" if all(v<0 for v in net_vals[:5]) else "MIXED"
                        st.markdown(f"**Tren 5 hari terakhir:** {trend_asing} | Net 5 hari: {'🟢' if net_5d>0 else '🔴'} Rp {net_5d/1e9:.2f}B" if abs(net_5d)>1e9 else f"**Tren 5 hari:** {trend_asing} | Net: {'🟢' if net_5d>0 else '🔴'} Rp {net_5d/1e6:.1f}M")
                    else:
                        st.warning("⚠️ Data foreign net dari IDX tidak tersedia untuk saham ini. Kemungkinan saham tidak aktif atau IDX sedang maintenance.")
                        st.info("Coba lagi nanti, atau cek langsung di [idx.co.id](https://www.idx.co.id/id/data-pasar/ringkasan-perdagangan-saham/)")

                # ================================================================
                # TAB 5: INSTITUTIONAL OWNERSHIP
                # ================================================================
                with tab5:
                    st.markdown('<div class="tab-subheader">🏛️ Institutional Ownership — Data Kepemilikan Institusi</div>', unsafe_allow_html=True)
                    st.markdown('<div class="info-box">📊 <b>Sumber: Yahoo Finance</b> — Data kepemilikan institusi (reksa dana, dana pensiun, asing). Update berkala (mingguan/bulanan). Proxy smart money jangka menengah.</div>', unsafe_allow_html=True)

                    with st.spinner("Mengambil data institutional ownership..."):
                        inst = get_institutional_ownership(symbol)

                    if inst:
                        i1,i2,i3 = st.columns(3)
                        with i1:
                            ip = inst["inst_pct"]
                            st.metric("Institutional Holdings",
                                      f"{ip*100:.1f}%" if ip else "N/A",
                                      "Smart money tinggi" if ip and ip>0.3 else "Smart money rendah" if ip else "")
                        with i2:
                            inp = inst["insider_pct"]
                            st.metric("Insider Holdings",
                                      f"{inp*100:.1f}%" if inp else "N/A",
                                      "Manajemen yakin" if inp and inp>0.1 else "")
                        with i3:
                            so = inst["shares_out"]
                            st.metric("Shares Outstanding",
                                      f"{so/1e9:.2f}B" if so and so>1e9 else f"{so/1e6:.1f}M" if so else "N/A")

                        st.markdown("---")

                        inst_h = inst["inst_holders"]
                        if inst_h is not None and not inst_h.empty:
                            st.subheader("🏦 Top Institutional Holders")
                            st.markdown("*Institusi-institusi besar yang memegang saham ini:*")
                            try:
                                disp_inst = inst_h.copy()
                                if "Shares" in disp_inst.columns:
                                    disp_inst["Shares"] = disp_inst["Shares"].apply(lambda x: f"{x:,.0f}")
                                if "% Out" in disp_inst.columns:
                                    disp_inst["% Out"] = disp_inst["% Out"].apply(lambda x: f"{x*100:.2f}%" if x<1 else f"{x:.2f}%")
                                if "Value" in disp_inst.columns:
                                    disp_inst["Value"] = disp_inst["Value"].apply(lambda x: f"${x/1e6:.1f}M" if x else "N/A")
                                st.dataframe(disp_inst, use_container_width=True, hide_index=True)
                            except Exception:
                                st.dataframe(inst_h, use_container_width=True, hide_index=True)

                            # Gauge chart institutional %
                            if inst["inst_pct"]:
                                pct = inst["inst_pct"] * 100
                                fig_gauge = go.Figure(go.Indicator(
                                    mode="gauge+number+delta",
                                    value=pct,
                                    title={"text": "Institutional Ownership %"},
                                    gauge={
                                        "axis": {"range": [0, 100]},
                                        "bar": {"color": "#1D9E75"},
                                        "steps": [
                                            {"range": [0,  20], "color": "#FCEBEB"},
                                            {"range": [20, 50], "color": "#FAEEDA"},
                                            {"range": [50,100], "color": "#EAF3DE"},
                                        ],
                                        "threshold": {"line": {"color": "red","width":2},"thickness":0.75,"value":30}
                                    },
                                    delta={"reference": 30, "increasing": {"color":"green"}, "decreasing": {"color":"red"}}
                                ))
                                fig_gauge.update_layout(height=300)
                                st.plotly_chart(fig_gauge, use_container_width=True)

                            # Interpretasi
                            ip2 = inst["inst_pct"] or 0
                            if ip2 > 0.5:
                                msg = "🟢 **Institutional ownership sangat tinggi** (>50%) — Saham ini banyak dipegang institusi besar. Biasanya lebih stabil dan likuid."
                            elif ip2 > 0.3:
                                msg = "🟡 **Institutional ownership sedang** (30-50%) — Cukup menarik bagi smart money. Potensi momentum jika institusi tambah posisi."
                            elif ip2 > 0.1:
                                msg = "🟠 **Institutional ownership rendah** (10-30%) — Kurang diminati institusi. Bisa jadi peluang jika fundamental bagus."
                            else:
                                msg = "🔴 **Institutional ownership sangat rendah** (<10%) — Saham ini mayoritas dipegang retail. Waspadai volatilitas tinggi."
                            st.markdown(msg)
                        else:
                            st.info("Data institusi holder tidak tersedia dari Yahoo Finance untuk saham ini.")
                            if inst["inst_pct"]:
                                st.metric("Institutional %", f"{inst['inst_pct']*100:.1f}%")
                    else:
                        st.warning("⚠️ Data institutional ownership tidak tersedia. Yahoo Finance mungkin belum mengindeks saham ini.")

                # ================================================================
                # TAB 6: HYBRID FORECAST
                # ================================================================
                with tab6:
                    st.markdown('<div class="tab-subheader">🔮 Hybrid Forecast (Gabungan Semua Analisis)</div>', unsafe_allow_html=True)
                    
                    tech_signals = analyze_strategy(df, current_strategy)
                    bandar_signals = analyze_bandarmology(df, symbol, manual_data)
                    trans_signals = None  # fitur transaksi simulasi dihapus
                    
                    score = 0
                    reasons = []
                    
                    if tech_signals:
                        if tech_signals['rekomendasi'] == 'BUY': score += 25
                        elif tech_signals['rekomendasi'] == 'SELL': score -= 25
                        if tech_signals['confidence'] > 70: score += 10
                        reasons.append(f"📊 Technical ({current_strategy}): {tech_signals['rekomendasi']} ({tech_signals['confidence']}%)")
                    
                    if bandar_signals:
                        if 'ACCUMULATION' in bandar_signals['trend']: score += 25
                        elif 'DISTRIBUTION' in bandar_signals['trend']: score -= 25
                        if bandar_signals['indicators']['divergence'] == 'Bullish': score += 15
                        elif bandar_signals['indicators']['divergence'] == 'Bearish': score -= 15
                        reasons.append(f"🕵️ Bandarmologi: {bandar_signals['trend']}")
                    
                    if trans_signals:
                        bp = trans_signals['transaction_patterns']['buy_pressure']
                        if bp > 0.6: score += 20
                        elif bp < 0.4: score -= 20
                        reasons.append(f"💰 Transaction Buy Pressure: {bp*100:.0f}%")
                    
                    if bandar_signals and bandar_signals['has_realtime']:
                        md = bandar_signals['manual_data']
                        if md['foreign']['net'] > 0: score += 15
                        if md['big_lot']['net'] > 0: score += 10
                        reasons.append(f"📥 Your Data: Foreign {md['foreign']['net']:.1f}M")
                    
                    score = max(0, min(100, score + 50))
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown(f'<h1>{score}/100</h1>', unsafe_allow_html=True)
                        st.markdown('Hybrid Score')
                        
                        if score >= 80:
                            rec = "STRONG BUY 🟢"
                            color = "#00c853"
                            action = "Beli agresif dengan position size normal"
                        elif score >= 65:
                            rec = "BUY 🟢"
                            color = "#64dd17"
                            action = "Beli dengan konfirmasi candlestick"
                        elif score >= 50:
                            rec = "NEUTRAL 🟡"
                            color = "#ffd600"
                            action = "Tunggu breakout atau pullback"
                        elif score >= 35:
                            rec = "REDUCE 🟠"
                            color = "#ff6d00"
                            action = "Pertimbangkan take profit parsial"
                        else:
                            rec = "SELL 🔴"
                            color = "#dd2c00"
                            action = "Cut loss atau short (jika memungkinkan)"
                        
                        st.markdown(f'<h2 style="color: {color}; margin-top: 10px;">{rec}</h2>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown(f'<div class="strategy-box"><b>Rekomendasi Aksi:</b><br>{action}</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader('📝 Komponen Score:')
                        for reason in reasons:
                            st.markdown(f"- {reason}")
                        
                        st.markdown('---')
                        st.subheader('⚖️ Confidence Level:')
                        
                        confidence = "HIGH" if (bandar_signals and bandar_signals['has_realtime']) else "MEDIUM"
                        color_conf = "green" if confidence == "HIGH" else "orange"
                        st.markdown(f'<span style="color: {color_conf}; font-weight: bold; font-size: 1.2rem;">{confidence}</span>', unsafe_allow_html=True)
                        
                        if confidence == "HIGH":
                            st.success("✅ Anda memiliki data real-time yang memperkuat analisis")
                        else:
                            st.warning("⚠️ Tambahkan data broker real-time untuk meningkatkan akurasi")
                    
                    st.markdown('---')
                    st.subheader('🎲 Decision Matrix')
                    
                    matrix_data = {
                        'Komponen': ['Technical Analysis', 'Bandarmologi', 'Transaction Flow', 'Your Input Data', 'Final Score'],
                        'Bobot': ['30%', '25%', '20%', '25%', '100%'],
                        'Status': [
                            tech_signals['rekomendasi'] if tech_signals else 'N/A',
                            bandar_signals['trend'] if bandar_signals else 'N/A',
                            f"Buy Pressure {trans_signals['transaction_patterns']['buy_pressure']*100:.0f}%" if trans_signals else 'N/A',
                            'Available ✅' if (bandar_signals and bandar_signals['has_realtime']) else 'Not Available ❌',
                            f"{score}/100"
                        ],
                        'Gunakan Untuk': [
                            'Entry/Timing',
                            'Trend Direction',
                            'Konfirmasi institusi',
                            'Validasi real-time',
                            'Risk Management'
                        ]
                    }
                    st.table(pd.DataFrame(matrix_data))
                


                # Download data
                st.markdown('---')
                csv = df.to_csv().encode('utf-8')
                st.download_button(
                    label='📥 Download Data CSV',
                    data=csv,
                    file_name=f'{symbol}_{datetime.now().strftime("%Y%m%d")}.csv',
                    mime='text/csv'
                )
                
                # ================================================================
                # TAB 7: STOCK SCANNER
                # ================================================================
                with tab7:
                    render_scanner_tab()

            else:
                st.error(f'❌ Data tidak cukup untuk **{symbol}**.')
                st.markdown("""
                **Kemungkinan penyebab & solusi:**
                - 🕐 **Rate limit Yahoo Finance** → Tunggu 1-2 menit, lalu klik *Clear Cache & Retry* di sidebar
                - 📅 **Periode terlalu pendek** → Coba ganti ke periode lebih panjang (misal: `6mo` atau `1y`)
                - ⏱️ **Interval tidak tersedia** → Interval `1m`/`5m` hanya tersedia untuk data 7 hari terakhir
                - 📡 **Koneksi internet** → Periksa koneksi Anda
                """)
                if st.button('🔄 Coba Lagi'):
                    st.cache_data.clear()
                    st.rerun()
    
    else:
        # Welcome Screen
        st.info('👈 Pilih saham di sidebar lalu klik **Analisis Lengkap** — atau langsung pakai **🔭 Stock Scanner** di bawah!')
        st.markdown('---')
        render_scanner_tab()
        st.markdown('---')
        st.subheader(f'✨ {len(SAHAM_INDONESIA)} Saham Tersedia — Fitur Utama Aplikasi')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="strategy-box">', unsafe_allow_html=True)
            st.markdown('**📊 Technical Analysis**')
            st.markdown('• Scalping, Intraday, Investasi')
            st.markdown('• 15+ Indikator teknikal')
            st.markdown('• Sinyal BUY/SELL otomatis')
            st.markdown('• Risk Management')
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="strategy-box">', unsafe_allow_html=True)
            st.markdown('**🕵️ Bandarmologi**')
            st.markdown('• On-Balance Volume (OBV)')
            st.markdown('• Accumulation/Distribution')
            st.markdown('• Deteksi Smart Money')
            st.markdown('• Analisis trend T+1')
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="strategy-box">', unsafe_allow_html=True)
            st.markdown('**💼 Broker & Transaction**')
            st.markdown('• Analisis per broker')
            st.markdown('• Foreign vs Local flow')
            st.markdown('• Big lots detection')
            st.markdown('• Input data real-time')
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('---')
        st.markdown("""
        ### 🎯 Cara Penggunaan Optimal:
        
        1. **Cari Saham** menggunakan kotak pencarian di sidebar (kode atau nama)
        2. **Pilih Strategi** sesuai timeframe trading Anda
        3. **Analisis Technical** untuk entry/exit points
        4. **Cek Bandarmologi** untuk arah trend smart money
        5. **Lihat Broker Summary** untuk dominasi asing/lokal
        6. **Input Data Anda** dari platform broker untuk validasi real-time
        7. **Lihat Hybrid Forecast** untuk keputusan final
        
        **Catatan:** Semua fitur sudah terintegrasi dalam 6 tab di atas!
        """)

if __name__ == '__main__':
    main()
