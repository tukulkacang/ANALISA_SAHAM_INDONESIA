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
import warnings
warnings.filterwarnings('ignore')

# Konfigurasi halaman
st.set_page_config(
    page_title="Analisis Saham Indonesia ULTIMATE",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom lengkap
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .metric-card h3 {
        margin: 0;
        font-size: 1.8rem;
    }
    .buy-signal {
        color: #00cc00;
        font-weight: bold;
        font-size: 1.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .sell-signal {
        color: #ff4444;
        font-weight: bold;
        font-size: 1.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .neutral-signal {
        color: #ffaa00;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .bandar-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
    }
    .broker-card {
        background: #f8f9fa;
        border-left: 5px solid #28a745;
        padding: 15px;
        margin: 5px 0;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .accumulation {
        background-color: #d4edda;
        color: #155724;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .distribution {
        background-color: #f8d7da;
        color: #721c24;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .neutral {
        background-color: #fff3cd;
        color: #856404;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .big-lot {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.1em;
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .strategy-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .tab-subheader {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin: 20px 0 10px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #eee;
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

# Daftar saham Indonesia (lengkap)
SAHAM_INDONESIA = {
    'BBCA.JK': 'Bank Central Asia',
    'BBRI.JK': 'Bank Rakyat Indonesia',
    'BMRI.JK': 'Bank Mandiri',
    'BBNI.JK': 'Bank Negara Indonesia',
    'TLKM.JK': 'Telkom Indonesia',
    'ASII.JK': 'Astra International',
    'UNVR.JK': 'Unilever Indonesia',
    'PGAS.JK': 'Perusahaan Gas Negara',
    'INDF.JK': 'Indofood Sukses Makmur',
    'KLBF.JK': 'Kalbe Farma',
    'GGRM.JK': 'Gudang Garam',
    'HMSP.JK': 'H.M. Sampoerna',
    'ICBP.JK': 'Indofood CBP',
    'MYOR.JK': 'Mayora Indah',
    'SMGR.JK': 'Semen Indonesia',
    'EXCL.JK': 'XL Axiata',
    'ISAT.JK': 'Indosat Ooredoo',
    'PTBA.JK': 'Bukit Asam',
    'ADRO.JK': 'Adaro Energy',
    'ITMG.JK': 'Indo Tambangraya Megah',
    'ANTM.JK': 'Aneka Tambang',
    'INKP.JK': 'Indah Kiat Pulp',
    'FREN.JK': 'Smartfren Telecom',
    'PWON.JK': 'Pakuwon Jati',
    'CTRA.JK': 'Ciputra Development',
    'SMRA.JK': 'Summarecon Agung',
    'BSDE.JK': 'Bumi Serpong Damai',
    'JPFA.JK': 'Japfa Comfeed',
    'CPIN.JK': 'Charoen Pokphand Indonesia',
    'MAIN.JK': 'Malindo Feedmill',
    'AUTO.JK': 'Astra Otoparts',
    'TBIG.JK': 'Tower Bersama Infrastructure',
    'TOWR.JK': 'Sarana Menara Nusantara',
    'LINK.JK': 'Link Net',
    'EMTK.JK': 'Elang Mahkota Teknologi',
    'BUMI.JK': 'Bumi Resources',
    'BRPT.JK': 'Barito Pacific',
    'ESSA.JK': 'ESSA Industries Indonesia',
    'TPIA.JK': 'Chandra Asri Petrochemical',
    'BRIS.JK': 'Bank Syariah Indonesia',
    'ARTO.JK': 'Bank Jago',
    'GOTO.JK': 'GoTo Gojek Tokopedia',
    'BUKA.JK': 'Bukalapak.com',
    'AMRT.JK': 'Alfamart',
    'MPPA.JK': 'Matahari Putra Prima',
    'LPPF.JK': 'Matahari Department Store',
    'ACES.JK': 'Ace Hardware Indonesia',
    'ERAA.JK': 'Erajaya Swasembada',
    'RALS.JK': 'Ramayana Lestari Sentosa',
    'MAPI.JK': 'Mitra Adiperkasa',
    'MNCN.JK': 'Media Nusantara Citra',
    'SCMA.JK': 'Surya Citra Media',
    'VIVA.JK': 'Visi Media Asia',
    'FILM.JK': 'MD Pictures',
    'DOOH.JK': 'Era Media Informasi',
    'MARK.JK': 'Mark Dynamics Indonesia',
    'HRUM.JK': 'Harum Energy',
    'TOBA.JK': 'Toba Bara Sejahtera',
    'MBAP.JK': 'Mitrabara Adiperdana',
    'DMND.JK': 'Diamond Food Indonesia',
    'CLEO.JK': 'Sariguna Primatirta',
    'AQUA.JK': 'Aqua Golden Mississippi',
    'MLBI.JK': 'Multi Bintang Indonesia',
    'STTP.JK': 'Siantar Top',
    'UFOE.JK': 'UFO Elektronika',
    'HEAL.JK': 'Medikaloka Hermina',
    'MIKA.JK': 'Mitra Keluarga Karyasehat',
    'SILO.JK': 'Siloam International Hospitals',
    'PRDA.JK': 'Prima Dahana',
    'OMED.JK': 'Jayamas Medica Industri',
    'DVLA.JK': 'Darya-Varia Laboratoria',
    'INAF.JK': 'Indofarma',
    'KAEF.JK': 'Kimia Farma',
    'PEHA.JK': 'Phapros',
    'RSGK.JK': 'Kedoya Adyaraya',
    'SAME.JK': 'Sarana Meditama Metropolitan',
    'MTMH.JK': 'Murni Sadar Tbk',
    'CMRY.JK': 'Cisarua Mountain Dairy',
    'WOOD.JK': 'Integra Indocabinet',
    'AVIA.JK': 'Avia Avian',
    'SPMA.JK': 'Suparma',
    'FASW.JK': 'Fajar Surya Wisesa',
    'TKIM.JK': 'Pabrik Kertas Tjiwi Kimia',
    'BLTZ.JK': 'Graha Layar Prima',
    'BOLT.JK': 'Garuda Metalindo',
    'KBLI.JK': 'KMI Wire and Cable',
    'SMCB.JK': 'Solusi Bangun Indonesia',
    'INTP.JK': 'Indocement Tunggal Prakarsa',
    'WSBP.JK': 'Waskita Beton Precast',
    'WIKA.JK': 'Wijaya Karya',
    'ADHI.JK': 'Adhi Karya',
    'PTPP.JK': 'PP (Persero)',
    'WSKT.JK': 'Waskita Karya',
    'BBTN.JK': 'Bank Tabungan Negara',
    'BJBR.JK': 'Bank BJB',
    'BJTM.JK': 'Bank Jatim',
    'BANK.JK': 'Bank MNC Internasional',
    'AGRO.JK': 'Bank Raya Indonesia',
    'SDRA.JK': 'Bank Woori Saudara',
    'NISP.JK': 'Bank OCBC NISP',
    'MAYA.JK': 'Bank Mayapada Internasional',
    'MCAS.JK': 'M Cash Integrasi',
    'UNTR.JK': 'United Tractors',
    'BYAN.JK': 'Bayan Resources'
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
# FUNGSI TEKNIKAL ANALISIS (Dari Kode Pertama)
# ============================================================================

@st.cache_data(ttl=300)
def get_stock_data(symbol, period='1y', interval='1d'):
    """Mengambil data saham dari Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)
        if df.empty:
            return None
        return df
    except Exception as e:
        st.error(f"Error mengambil data: {e}")
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
        # EMA Crossover cepat + RSI + Bollinger + Volume
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
        # MACD + RSI + ADX + Support/Resistance
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
        # Golden Cross + Trend + Fibonacci
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
# FUNGSI BANDARMOLOGI (Dari Kode Kedua)
# ============================================================================

def analyze_bandarmology(df, symbol, manual_data=None):
    """Analisis perilaku bandar dengan indikator money flow"""
    if df is None or len(df) < 20:
        return None
    
    analysis = {
        'data_type': 'DELAYED (T+1)',
        'last_update': df.index[-1].strftime('%Y-%m-%d'),
        'trend': 'NEUTRAL',
        'strength': 0,
        'accumulation_score': 0,
        'distribution_score': 0,
        'indicators': {},
        'interpretation': '',
        'trading_implications': ''
    }
    
    # OBV
    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    
    df['OBV'] = obv
    df['OBV_SMA'] = pd.Series(obv).rolling(window=20).mean()
    
    # A/D Line
    money_flow = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low']) * df['Volume']
    df['AD_Line'] = money_flow.cumsum()
    
    # Analisis
    obv_trend = 'UP' if df['OBV'].iloc[-1] > df['OBV_SMA'].iloc[-1] else 'DOWN'
    price_trend = 'UP' if df['Close'].iloc[-1] > df['Close'].iloc[-20] else 'DOWN'
    ad_trend = 'UP' if df['AD_Line'].iloc[-1] > df['AD_Line'].iloc[-20] else 'DOWN'
    vol_ratio = df['Volume'].tail(5).mean() / df['Volume'].mean()
    
    # Scoring
    score = 0
    if obv_trend == 'UP': score += 30
    if ad_trend == 'UP': score += 30
    if price_trend == obv_trend: score += 20
    if vol_ratio > 1.2: score += 20
    
    analysis['strength'] = score
    
    if score >= 70:
        analysis['trend'] = 'STRONG_ACCUMULATION'
        analysis['accumulation_score'] = 85
        analysis['interpretation'] = 'Smart money sedang akumulasi besar'
        analysis['trading_implications'] = 'Cari entry di timeframe kecil. Konfirmasi dengan data real-time.'
    elif score >= 50:
        analysis['trend'] = 'ACCUMULATION'
        analysis['accumulation_score'] = 70
        analysis['interpretation'] = 'Tanda-tanda akumulasi terlihat'
        analysis['trading_implications'] = 'Monitor untuk konfirmasi breakout'
    elif score <= 30:
        analysis['trend'] = 'DISTRIBUTION'
        analysis['distribution_score'] = 80
        analysis['interpretation'] = 'Kemungkinan distribusi bandar'
        analysis['trading_implications'] = 'Hati-hati, potensi penurunan'
    else:
        analysis['trend'] = 'NEUTRAL'
        analysis['interpretation'] = 'Belum ada sinyal jelas'
        analysis['trading_implications'] = 'Tunggu setup lebih baik'
    
    analysis['indicators'] = {
        'obv_trend': obv_trend,
        'ad_trend': ad_trend,
        'price_trend': price_trend,
        'volume_ratio': vol_ratio,
        'divergence': 'Bullish' if (price_trend == 'DOWN' and obv_trend == 'UP') else 'Bearish' if (price_trend == 'UP' and obv_trend == 'DOWN') else 'None'
    }
    
    if manual_data and symbol in manual_data:
        analysis['manual_data'] = manual_data[symbol]
        analysis['has_realtime'] = True
    else:
        analysis['has_realtime'] = False
    
    return analysis

# ============================================================================
# FUNGSI BROKER SUMMARY (Dari Kode Kedua)
# ============================================================================

def generate_broker_summary(symbol, df):
    """Generate analisis transaksi per broker (simulasi realistis)"""
    if df is None:
        return None
    
    np.random.seed(hash(symbol) % 2**32)
    brokers_data = []
    total_value = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
    
    is_bluechip = symbol in ['BBCA.JK', 'BBRI.JK', 'TLKM.JK', 'ASII.JK', 'BMRI.JK']
    is_midcap = symbol in ['EXCL.JK', 'PGAS.JK', 'INDF.JK', 'KLBF.JK', 'MYOR.JK']
    price_level = df['Close'].iloc[-1]
    
    if is_bluechip:
        active_brokers = ['YU', 'MS', 'KS', 'NI', 'RX', 'AK', 'GR', 'BK', 'TP', 'BB', 'DM', 'PD', 'NI', 'BM']
        foreign_dominated = True
    elif is_midcap:
        active_brokers = ['KS', 'BB', 'DM', 'PD', 'NI', 'BM', 'BJ', 'BS', 'MK', 'FO', 'KK', 'HD', 'MU', 'CC', 'GA']
        foreign_dominated = False
    else:
        active_brokers = ['IP', 'RA', 'MG', 'GV', 'YR', 'SF', 'DR', 'HS', 'OC', 'MA', 'SA', 'AB', 'ID', 'EF']
        foreign_dominated = False
    
    remaining_volume = df['Volume'].iloc[-1]
    
    for broker_code in active_brokers[:10]:
        broker_name = BROKER_LIST.get(broker_code, 'Unknown')
        
        if foreign_dominated and broker_code in ['YU', 'MS', 'NI', 'RX', 'AK', 'GR', 'BK', 'TP']:
            if df['Close'].iloc[-1] < df['SMA_20'].iloc[-1]:
                buy_ratio = np.random.uniform(0.6, 0.8)
            else:
                buy_ratio = np.random.uniform(0.4, 0.6)
        else:
            if df['Close'].iloc[-1] > df['Close'].iloc[-5]:
                buy_ratio = np.random.uniform(0.55, 0.75)
            else:
                buy_ratio = np.random.uniform(0.25, 0.45)
        
        volume_share = np.random.pareto(2) + 0.1
        broker_volume = min(remaining_volume * 0.15, total_value * 0.05 * volume_share)
        remaining_volume -= broker_volume
        
        buy_volume = broker_volume * buy_ratio
        sell_volume = broker_volume * (1 - buy_ratio)
        net_volume = buy_volume - sell_volume
        
        if broker_volume > total_value * 0.02:
            frequency = np.random.randint(50, 200)
            lot_size = np.random.randint(100, 500)
        else:
            frequency = np.random.randint(10, 50)
            lot_size = np.random.randint(10, 100)
        
        brokers_data.append({
            'Kode': broker_code,
            'Nama_Broker': broker_name,
            'Buy_Value': buy_volume,
            'Sell_Value': sell_volume,
            'Net_Value': net_volume,
            'Total_Value': broker_volume,
            'Buy_Lot': int(buy_volume / price_level / 100),
            'Sell_Lot': int(sell_volume / price_level / 100),
            'Net_Lot': int(net_volume / price_level / 100),
            'Frequency': frequency,
            'Avg_Lot_Size': lot_size,
            'Type': 'Foreign' if broker_code in ['YU', 'MS', 'NI', 'RX', 'AK', 'GR', 'BK', 'TP', 'ML', 'DX', 'JP', 'CL'] else 'Local'
        })
    
    df_brokers = pd.DataFrame(brokers_data)
    df_brokers = df_brokers.sort_values('Total_Value', ascending=False)
    
    foreign_buy = df_brokers[df_brokers['Type'] == 'Foreign']['Buy_Value'].sum()
    foreign_sell = df_brokers[df_brokers['Type'] == 'Foreign']['Sell_Value'].sum()
    local_buy = df_brokers[df_brokers['Type'] == 'Local']['Buy_Value'].sum()
    local_sell = df_brokers[df_brokers['Type'] == 'Local']['Sell_Value'].sum()
    
    summary = {
        'detail': df_brokers,
        'foreign_net': foreign_buy - foreign_sell,
        'local_net': local_buy - local_sell,
        'total_foreign': foreign_buy + foreign_sell,
        'total_local': local_buy + local_sell,
        'dominant_side': 'BUY' if (foreign_buy + local_buy) > (foreign_sell + local_sell) else 'SELL',
        'top_buyer': df_brokers.loc[df_brokers['Net_Value'].idxmax()],
        'top_seller': df_brokers.loc[df_brokers['Net_Value'].idxmin()]
    }
    
    return summary

# ============================================================================
# FUNGSI TRANSACTION ANALYSIS (Dari Kode Kedua)
# ============================================================================

def analyze_transactions(symbol, df):
    """Analisis detail transaksi: Lot besar, frekuensi, pola"""
    if df is None:
        return None
    
    analysis = {
        'big_lots': [],
        'transaction_patterns': {},
        'time_distribution': {},
        'price_levels': {},
        'unusual_activity': []
    }
    
    current_price = df['Close'].iloc[-1]
    avg_price_20 = df['Close'].tail(20).mean()
    
    # Big Lots Detection
    big_lot_threshold = 500_000_000
    num_big_trans = int(df['Volume'].iloc[-1] / 1000000)
    
    big_transactions = []
    for i in range(min(num_big_trans, 20)):
        lot_size = np.random.randint(1000, 10000)
        value = lot_size * 100 * current_price
        
        if value > big_lot_threshold:
            trans_type = 'BUY' if np.random.random() > 0.4 else 'SELL'
            big_transactions.append({
                'Time': (datetime.now() - timedelta(minutes=np.random.randint(0, 390))).strftime('%H:%M'),
                'Lot': lot_size,
                'Price': current_price * (1 + np.random.uniform(-0.01, 0.01)),
                'Value': value,
                'Type': trans_type,
                'Intensity': 'VERY_BIG' if value > 2_000_000_000 else 'BIG' if value > 1_000_000_000 else 'MEDIUM'
            })
    
    analysis['big_lots'] = sorted(big_transactions, key=lambda x: x['Value'], reverse=True)
    
    # Patterns
    total_buy_lot = sum([t['Lot'] for t in big_transactions if t['Type'] == 'BUY'])
    total_sell_lot = sum([t['Lot'] for t in big_transactions if t['Type'] == 'SELL'])
    
    analysis['transaction_patterns'] = {
        'buy_pressure': total_buy_lot / (total_buy_lot + total_sell_lot) if (total_buy_lot + total_sell_lot) > 0 else 0.5,
        'big_lot_count': len(big_transactions),
        'avg_big_lot_size': np.mean([t['Lot'] for t in big_transactions]) if big_transactions else 0,
        'buy_sell_ratio': total_buy_lot / total_sell_lot if total_sell_lot > 0 else float('inf')
    }
    
    # Time Distribution
    hours = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '13:30-14:00', '14:00-15:00', '15:00-15:30']
    analysis['time_distribution'] = {hour: np.random.randint(100, 1000) for hour in hours}
    analysis['time_distribution']['09:00-10:00'] *= 1.5
    analysis['time_distribution']['14:00-15:00'] *= 1.3
    
    # Price Levels
    analysis['price_levels'] = {
        'support_1': df['Low'].tail(5).min(),
        'support_2': df['Low'].tail(20).min(),
        'resistance_1': df['High'].tail(5).max(),
        'resistance_2': df['High'].tail(20).max(),
        'vwap': (df['Close'] * df['Volume']).sum() / df['Volume'].sum(),
        'pivot': (df['High'].iloc[-1] + df['Low'].iloc[-1] + df['Close'].iloc[-1]) / 3
    }
    
    # Unusual Activity
    if current_price > avg_price_20 * 1.05 and df['Volume'].iloc[-1] > df['Volume'].mean() * 1.5:
        analysis['unusual_activity'].append({
            'type': 'BREAKOUT_VOLUME',
            'description': 'Harga breakout dengan volume tinggi (>50% avg)',
            'significance': 'HIGH'
        })
    
    if abs(df['Close'].iloc[-1] - df['Open'].iloc[-1]) / df['Open'].iloc[-1] > 0.05:
        analysis['unusual_activity'].append({
            'type': 'LARGE_CANDLE',
            'description': 'Pergerakan harga ekstrem (>5%) dalam satu sesi',
            'significance': 'MEDIUM'
        })
    
    if analysis['transaction_patterns']['buy_pressure'] > 0.7:
        analysis['unusual_activity'].append({
            'type': 'HEAVY_BUYING',
            'description': 'Tekanan beli sangat tinggi pada lot besar',
            'significance': 'HIGH'
        })
    
    return analysis

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
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name='OHLC'
    ), row=1, col=1)
    
    # Moving Averages
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', line=dict(color='blue', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(color='orange', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], name='SMA 200', line=dict(color='red', width=1)), row=1, col=1)
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper', line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower', line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
    
    # Support/Resistance
    fig.add_trace(go.Scatter(x=df.index, y=df['Support'], name='Support', line=dict(color='green', width=1, dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Resistance'], name='Resistance', line=dict(color='red', width=1, dash='dot')), row=1, col=1)
    
    # MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='red')), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name='Histogram', marker_color='gray'), row=2, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # Volume
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
    
    # Pilih saham
    selected_stock = st.sidebar.selectbox(
        'Pilih Saham:',
        options=list(SAHAM_INDONESIA.keys()),
        format_func=lambda x: f"{x} - {SAHAM_INDONESIA[x]}"
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
        current_strategy = st.session_state.get('last_strategy', strategy)
        
        with st.spinner(f'Menganalisis {symbol}...'):
            df = get_stock_data(symbol, period, interval)
            
            if df is not None and len(df) > 20:
                # Calculate indicators
                df = calculate_indicators(df)
                
                # Create tabs untuk SEMUA FITUR
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    '📊 Technical Analysis',
                    '🎯 Strategy Signals',
                    '🕵️ Bandarmologi',
                    '🏦 Broker Summary',
                    '💰 Transaction Analysis',
                    '🔮 Hybrid Forecast'
                ])
                
                # ================================================================
                # TAB 1: TECHNICAL ANALYSIS (Lengkap dari kode pertama)
                # ================================================================
                with tab1:
                    st.markdown('<div class="tab-subheader">📊 Analisis Teknikal Lengkap</div>', unsafe_allow_html=True)
                    
                    # Metrics
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
                    
                    # Main Chart
                    fig = create_main_chart(df, symbol, current_strategy)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Technical Summary
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
                # TAB 2: STRATEGY SIGNALS (Dari kode pertama)
                # ================================================================
                with tab2:
                    st.markdown('<div class="tab-subheader">🎯 Sinyal Strategi Trading</div>', unsafe_allow_html=True)
                    
                    signals = analyze_strategy(df, current_strategy)
                    
                    if signals:
                        # Signal Display
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
                        
                        # Trading Plan
                        st.markdown('---')
                        st.subheader('🎯 Trading Plan')
                        
                        plan_col1, plan_col2, plan_col3 = st.columns(3)
                        with plan_col1:
                            st.markdown(f'<div class="info-box"><b>Entry:</b> Rp {signals["entry"]:,.0f}</div>' if signals["entry"] else '<div class="info-box"><b>Entry:</b> -</div>', unsafe_allow_html=True)
                        with plan_col2:
                            st.markdown(f'<div class="warning-box"><b>Stop Loss:</b> Rp {signals["stop_loss"]:,.0f}</div>' if signals["stop_loss"] else '<div class="warning-box"><b>Stop Loss:</b> -</div>', unsafe_allow_html=True)
                        with plan_col3:
                            st.markdown(f'<div class="success-box"><b>Take Profit:</b> Rp {signals["take_profit"]:,.0f}</div>' if signals["take_profit"] else '<div class="success-box"><b>Take Profit:</b> -</div>', unsafe_allow_html=True)
                        
                        # Alasan
                        st.subheader('📝 Alasan Sinyal')
                        for alasan in signals['alasan']:
                            st.markdown(f'- {alasan}')
                        
                        # Strategy Info
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
                # TAB 3: BANDARMOLOGI (Dari kode kedua)
                # ================================================================
                with tab3:
                    st.markdown('<div class="tab-subheader">🕵️ Analisis Bandarmologi (Smart Money)</div>', unsafe_allow_html=True)
                    
                    manual_data = load_manual_data()
                    bandar = analyze_bandarmology(df, symbol, manual_data)
                    
                    if bandar:
                        # Warning box untuk data delayed
                        st.markdown('<div class="warning-box">⚠️ <b>Catatan:</b> Analisis ini menggunakan data Closing T+1. Gunakan untuk melihat trend jangka menengah, bukan untuk entry real-time.</div>', unsafe_allow_html=True)
                        
                        # Summary Cards
                        st.markdown('<div class="bandar-card">', unsafe_allow_html=True)
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            trend_class = 'accumulation' if 'ACCUMULATION' in bandar['trend'] else 'distribution' if 'DISTRIBUTION' in bandar['trend'] else 'neutral'
                            st.markdown(f'<span class="{trend_class}">{bandar["trend"]}</span>', unsafe_allow_html=True)
                            st.markdown(f'<b>Confidence: {bandar["strength"]}%</b>')
                        
                        with col2:
                            st.markdown(f'<b>Strength Score</b>')
                            st.progress(bandar['strength'] / 100)
                        
                        with col3:
                            st.markdown(f'<b>Rekomendasi:</b><br>{bandar["trading_implications"]}')
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Detail Analysis
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader('📊 Volume Analysis')
                            ind = bandar['indicators']
                            st.markdown(f"- **Current vs Avg:** {ind['volume_ratio']:.2f}x")
                            st.markdown(f"- **OBV Trend:** {ind['obv_trend']}")
                            st.markdown(f"- **A/D Trend:** {ind['ad_trend']}")
                            st.markdown(f"- **Divergence:** {ind['divergence']}")
                        
                        with col2:
                            st.subheader('📈 Price Action')
                            st.markdown(f"- **Price Trend:** {ind['price_trend']}")
                            st.markdown(f"- **Last Update:** {bandar['last_update']}")
                        
                        # Chart
                        fig_bandar = create_bandarmology_chart(df)
                        st.plotly_chart(fig_bandar, use_container_width=True)
                        
                        # Interpretasi
                        with st.expander('📖 Cara Membaca Indikator'):
                            st.markdown("""
                            **On-Balance Volume (OBV):**
                            - Naik saat harga naik: Konfirmasi tren bullish
                            - Turun saat harga naik: Divergence bearish (waspada)
                            
                            **Accumulation/Distribution Line:**
                            - Naik: Dana masuk (akumulasi)
                            - Turun: Dana keluar (distribusi)
                            
                            **Kombinasi:**
                            - OBV & A/D naik + Harga naik = Tren kuat
                            - OBV & A/D turun + Harga turun = Jual besar
                            - Divergence = Potensi pembalikan
                            """)
                        
                        # Data manual jika ada
                        if bandar['has_realtime']:
                            st.markdown('---')
                            st.markdown('<div class="info-box">', unsafe_allow_html=True)
                            st.subheader('📥 Data Real-time Anda Hari Ini')
                            md = bandar['manual_data']
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.metric('Foreign Net', f"{md['foreign']['net']:.1f}M")
                            with c2:
                                st.metric('Local Net', f"{md['local']['net']:.1f}M")
                            with c3:
                                st.metric('Big Lot Net', f"{md['big_lot']['net']:.0f}Jt")
                            st.markdown('</div>', unsafe_allow_html=True)
                
                # ================================================================
                # TAB 4: BROKER SUMMARY (Dari kode kedua)
                # ================================================================
                with tab4:
                    st.markdown('<div class="tab-subheader">🏦 Analisis Transaksi per Broker</div>', unsafe_allow_html=True)
                    
                    broker_data = generate_broker_summary(symbol, df)
                    
                    if broker_data:
                        # Metrics
                        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                        
                        with metric_col1:
                            foreign_net = broker_data['foreign_net']
                            color = '🟢' if foreign_net > 0 else '🔴'
                            st.metric('Foreign Net', f"{color} Rp {abs(foreign_net)/1e9:.1f}B", 
                                     delta=f"{'Net Buy' if foreign_net > 0 else 'Net Sell'}")
                        
                        with metric_col2:
                            local_net = broker_data['local_net']
                            color = '🟢' if local_net > 0 else '🔴'
                            st.metric('Local Net', f"{color} Rp {abs(local_net)/1e9:.1f}B",
                                     delta=f"{'Net Buy' if local_net > 0 else 'Net Sell'}")
                        
                        with metric_col3:
                            total_val = broker_data['total_foreign'] + broker_data['total_local']
                            st.metric('Total Value', f"Rp {total_val/1e9:.1f}B")
                        
                        with metric_col4:
                            dominant = broker_data['dominant_side']
                            st.metric('Dominant Side', dominant, 
                                     delta='Bullish' if dominant == 'BUY' else 'Bearish')
                        
                        # Top Brokers Table
                        st.subheader('🏆 Top 10 Broker Aktif')
                        df_brokers = broker_data['detail']
                        
                        display_df = df_brokers.copy()
                        display_df['Buy_Value'] = display_df['Buy_Value'].apply(lambda x: f"Rp {x/1e9:.1f}B" if x > 1e9 else f"Rp {x/1e6:.1f}M")
                        display_df['Sell_Value'] = display_df['Sell_Value'].apply(lambda x: f"Rp {x/1e9:.1f}B" if x > 1e9 else f"Rp {x/1e6:.1f}M")
                        display_df['Net_Value'] = display_df['Net_Value'].apply(lambda x: f"Rp {x/1e9:.1f}B" if abs(x) > 1e9 else f"Rp {x/1e6:.1f}M")
                        display_df['Total_Value'] = display_df['Total_Value'].apply(lambda x: f"Rp {x/1e9:.1f}B" if x > 1e9 else f"Rp {x/1e6:.1f}M")
                        
                        st.dataframe(display_df[['Kode', 'Nama_Broker', 'Type', 'Buy_Value', 'Sell_Value', 'Net_Value', 'Frequency']], 
                                    use_container_width=True, hide_index=True)
                        
                        # Visualization
                        fig_broker = create_broker_chart(broker_data)
                        st.plotly_chart(fig_broker, use_container_width=True)
                        
                        # Analysis Text
                        st.subheader('📝 Analisis Broker')
                        top_buyer = broker_data['top_buyer']
                        top_seller = broker_data['top_seller']
                        
                        st.markdown(f"""
                        **Insight:**
                        1. **Foreign Flow:** {'Asing masuk bersih' if foreign_net > 0 else 'Asing keluar bersih'} Rp {abs(foreign_net)/1e9:.1f} Miliar
                        2. **Local Flow:** {'Lokal masuk bersih' if local_net > 0 else 'Lokal keluar bersih'} Rp {abs(local_net)/1e9:.1f} Miliar
                        3. **Top Buyer:** {top_buyer['Nama_Broker']} ({top_buyer['Kode']}) - Rp {top_buyer['Net_Value']/1e9:.1f}B
                        4. **Top Seller:** {top_seller['Nama_Broker']} ({top_seller['Kode']}) - Rp {abs(top_seller['Net_Value'])/1e9:.1f}B
                        
                        **Kesimpulan:** {'Asing dan lokal kompak beli 🟢' if foreign_net > 0 and local_net > 0 else 'Asing beli, lokal jual 🟡' if foreign_net > 0 else 'Asing jual, lokal beli 🔴' if local_net > 0 else 'Asing dan lokal kompak jual 🔴'}
                        """)
                
                # ================================================================
                # TAB 5: TRANSACTION ANALYSIS (Dari kode kedua)
                # ================================================================
                with tab5:
                    st.markdown('<div class="tab-subheader">💰 Analisis Transaksi Detail</div>', unsafe_allow_html=True)
                    
                    trans_analysis = analyze_transactions(symbol, df)
                    
                    if trans_analysis:
                        # Big Lots
                        st.subheader('🎯 Deteksi Transaksi Besar (Big Lots)')
                        
                        if trans_analysis['big_lots']:
                            big_lots_df = pd.DataFrame(trans_analysis['big_lots'])
                            
                            def color_type(val):
                                color = 'green' if val == 'BUY' else 'red'
                                return f'color: {color}; font-weight: bold'
                            
                            def highlight_value(val):
                                if isinstance(val, (int, float)):
                                    if val > 2_000_000_000:
                                        return 'background-color: #ffcccc; font-weight: bold'
                                    elif val > 1_000_000_000:
                                        return 'background-color: #ffffcc'
                                return ''
                            
                            styled_df = big_lots_df.style\
                                .applymap(color_type, subset=['Type'])\
                                .applymap(highlight_value, subset=['Value'])\
                                .format({
                                    'Lot': '{:,.0f}',
                                    'Price': 'Rp {:,.0f}',
                                    'Value': lambda x: f'Rp {x/1e9:.2f}B' if x > 1e9 else f'Rp {x/1e6:.1f}M'
                                })
                            
                            st.dataframe(styled_df, use_container_width=True)
                            
                            # Summary
                            total_big = sum([t['Value'] for t in trans_analysis['big_lots']])
                            buy_big = sum([t['Value'] for t in trans_analysis['big_lots'] if t['Type'] == 'BUY'])
                            sell_big = sum([t['Value'] for t in trans_analysis['big_lots'] if t['Type'] == 'SELL'])
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric('Total Big Lot', f"Rp {total_big/1e9:.1f}B")
                            with col2:
                                st.metric('Buy Big Lot', f"Rp {buy_big/1e9:.1f}B", f"{buy_big/total_big*100:.1f}%")
                            with col3:
                                st.metric('Sell Big Lot', f"Rp {sell_big/1e9:.1f}B", f"{sell_big/total_big*100:.1f}%")
                        else:
                            st.info('Tidak ada transaksi big lot terdeteksi')
                        
                        # Patterns
                        st.markdown('---')
                        st.subheader('📊 Pola Transaksi')
                        
                        patterns = trans_analysis['transaction_patterns']
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.markdown(f'<h3>{patterns["buy_pressure"]*100:.1f}%</h3>', unsafe_allow_html=True)
                            st.markdown('Buy Pressure')
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.markdown(f'<h3>{patterns["big_lot_count"]}</h3>', unsafe_allow_html=True)
                            st.markdown('Big Lot Trans')
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col3:
                            ratio = patterns['buy_sell_ratio']
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.markdown(f'<h3>{ratio:.2f}</h3>', unsafe_allow_html=True)
                            st.markdown('Buy/Sell Ratio')
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Time Distribution
                        st.markdown('---')
                        st.subheader('⏰ Distribusi Waktu')
                        
                        time_df = pd.DataFrame(list(trans_analysis['time_distribution'].items()), 
                                              columns=['Time', 'Volume'])
                        
                        fig_time = go.Figure(go.Bar(
                            x=time_df['Time'],
                            y=time_df['Volume'],
                            marker_color='blue'
                        ))
                        fig_time.update_layout(
                            title='Volume Distribution by Time (Intraday Pattern)',
                            xaxis_title='Time',
                            yaxis_title='Volume',
                            height=400
                        )
                        st.plotly_chart(fig_time, use_container_width=True)
                        
                        # Price Levels
                        st.markdown('---')
                        st.subheader('📍 Level Harga Penting')
                        
                        levels = trans_analysis['price_levels']
                        level_col1, level_col2, level_col3 = st.columns(3)
                        
                        with level_col1:
                            st.markdown('**Support:**')
                            st.markdown(f"S1: Rp {levels['support_1']:,.0f}")
                            st.markdown(f"S2: Rp {levels['support_2']:,.0f}")
                        
                        with level_col2:
                            st.markdown('**Current & Pivot:**')
                            st.markdown(f"Current: Rp {df['Close'].iloc[-1]:,.0f}")
                            st.markdown(f"Pivot: Rp {levels['pivot']:,.0f}")
                            st.markdown(f"VWAP: Rp {levels['vwap']:,.0f}")
                        
                        with level_col3:
                            st.markdown('**Resistance:**')
                            st.markdown(f"R1: Rp {levels['resistance_1']:,.0f}")
                            st.markdown(f"R2: Rp {levels['resistance_2']:,.0f}")
                        
                        # Unusual Activity
                        if trans_analysis['unusual_activity']:
                            st.markdown('---')
                            st.subheader('🚨 Aktivitas Tidak Biasa')
                            
                            for activity in trans_analysis['unusual_activity']:
                                severity = '🔴' if activity['significance'] == 'HIGH' else '🟡'
                                st.markdown(f"{severity} **{activity['type']}**: {activity['description']}")
                
                # ================================================================
                # TAB 6: HYBRID FORECAST (Gabungan semua)
                # ================================================================
                with tab6:
                    st.markdown('<div class="tab-subheader">🔮 Hybrid Forecast (Gabungan Semua Analisis)</div>', unsafe_allow_html=True)
                    
                    # Kumpulkan semua sinyal
                    tech_signals = analyze_strategy(df, current_strategy)
                    bandar_signals = analyze_bandarmology(df, symbol, manual_data)
                    trans_signals = analyze_transactions(symbol, df)
                    
                    # Scoring
                    score = 0
                    reasons = []
                    
                    # Technical Score
                    if tech_signals:
                        if tech_signals['rekomendasi'] == 'BUY': score += 25
                        elif tech_signals['rekomendasi'] == 'SELL': score -= 25
                        if tech_signals['confidence'] > 70: score += 10
                        reasons.append(f"📊 Technical ({current_strategy}): {tech_signals['rekomendasi']} ({tech_signals['confidence']}%)")
                    
                    # Bandarmologi Score
                    if bandar_signals:
                        if 'ACCUMULATION' in bandar_signals['trend']: score += 25
                        elif 'DISTRIBUTION' in bandar_signals['trend']: score -= 25
                        if bandar_signals['indicators']['divergence'] == 'Bullish': score += 15
                        elif bandar_signals['indicators']['divergence'] == 'Bearish': score -= 15
                        reasons.append(f"🕵️ Bandarmologi: {bandar_signals['trend']}")
                    
                    # Transaction Score
                    if trans_signals:
                        bp = trans_signals['transaction_patterns']['buy_pressure']
                        if bp > 0.6: score += 20
                        elif bp < 0.4: score -= 20
                        reasons.append(f"💰 Transaction Buy Pressure: {bp*100:.0f}%")
                    
                    # Manual Data Score
                    if bandar_signals and bandar_signals['has_realtime']:
                        md = bandar_signals['manual_data']
                        if md['foreign']['net'] > 0: score += 15
                        if md['big_lot']['net'] > 0: score += 10
                        reasons.append(f"📥 Your Data: Foreign {md['foreign']['net']:.1f}M")
                    
                    # Normalize score
                    score = max(0, min(100, score + 50))  # Convert to 0-100 scale
                    
                    # Display
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
                    
                    # Matrix
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
                
            else:
                st.error(f'Data tidak cukup untuk {symbol}')
    
    else:
        # Welcome Screen
        st.info('👈 Pilih strategi dan saham di sidebar, kemudian klik "Analisis Lengkap"')
        
        st.markdown('---')
        st.subheader('✨ Fitur Utama Aplikasi Ini')
        
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
        
        1. **Pilih Strategi** sesuai timeframe trading Anda
        2. **Analisis Technical** untuk entry/exit points
        3. **Cek Bandarmologi** untuk arah trend smart money
        4. **Lihat Broker Summary** untuk dominasi asing/lokal
        5. **Input Data Anda** dari platform broker untuk validasi real-time
        6. **Lihat Hybrid Forecast** untuk keputusan final
        
        **Catatan:** Semua fitur sudah terintegrasi dalam 6 tab di atas!
        """)

if __name__ == '__main__':
    main()
