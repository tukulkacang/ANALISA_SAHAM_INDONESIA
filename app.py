"""
HYBRID STOCK ANALYSIS APP
Real-time Technical + Delayed Bandarmologi + Manual Input Real-time Data
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

st.set_page_config(page_title="Hybrid Stock Analysis Pro", layout="wide")

# CSS
st.markdown("""
<style>
    .realtime-box {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .delayed-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
        opacity: 0.9;
    }
    .manual-input {
        background-color: #e3f2fd;
        padding: 15px;
        border-left: 5px solid #2196f3;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Database sederhana untuk menyimpan data manual
DATA_FILE = "manual_broker_data.json"

def load_manual_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_manual_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Fungsi analisis bandarmologi (sama seperti sebelumnya, tapi dengan penjelasan keterbatasan)
def analyze_bandarmology_hybrid(df, symbol, manual_data=None):
    """
    Analisis bandarmologi dengan penandaan data delayed
    """
    if df is None or len(df) < 20:
        return None
    
    analysis = {
        'data_type': 'DELAYED (T+1)',
        'last_update': df.index[-1].strftime('%Y-%m-%d'),
        'trend': 'NEUTRAL',
        'confidence': 0,
        'indicators': {},
        'interpretation': '',
        'trading_implications': ''
    }
    
    # Hitung OBV
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
    
    # Analisis trend
    obv_trend = 'UP' if df['OBV'].iloc[-1] > df['OBV_SMA'].iloc[-1] else 'DOWN'
    price_trend = 'UP' if df['Close'].iloc[-1] > df['Close'].iloc[-20] else 'DOWN'
    ad_trend = 'UP' if df['AD_Line'].iloc[-1] > df['AD_Line'].iloc[-20] else 'DOWN'
    
    # Scoring
    score = 0
    if obv_trend == 'UP': score += 30
    if ad_trend == 'UP': score += 30
    if price_trend == obv_trend: score += 20
    
    # Volume analysis
    vol_ratio = df['Volume'].tail(5).mean() / df['Volume'].mean()
    if vol_ratio > 1.2: score += 20
    
    analysis['confidence'] = score
    
    if score >= 70:
        analysis['trend'] = 'STRONG_ACCUMULATION'
        analysis['interpretation'] = 'Smart money sedang akumulasi (Berdasarkan data T+1)'
        analysis['trading_implications'] = 'Cari entry di timeframe lebih kecil. Konfirmasi dengan data real-time hari ini.'
    elif score >= 50:
        analysis['trend'] = 'ACCUMULATION'
        analysis['interpretation'] = 'Tanda-tanda akumulasi terlihat'
        analysis['trading_implications'] = 'Monitor untuk konfirmasi breakout'
    elif score <= 30:
        analysis['trend'] = 'DISTRIBUTION'
        analysis['interpretation'] = 'Kemungkinan distribusi'
        analysis['trading_implications'] = 'Hati-hati, potensi penurunan'
    else:
        analysis['trend'] = 'NEUTRAL'
        analysis['interpretation'] = 'Belum ada sinyal jelas'
        analysis['trading_implications'] = 'Tunggu setup yang lebih baik'
    
    analysis['indicators'] = {
        'obv_trend': obv_trend,
        'ad_trend': ad_trend,
        'price_trend': price_trend,
        'volume_ratio': vol_ratio,
        'obv_divergence': 'Bullish' if (price_trend == 'DOWN' and obv_trend == 'UP') else 'Bearish' if (price_trend == 'UP' and obv_trend == 'DOWN') else 'None'
    }
    
    # Gabungkan dengan data manual jika ada
    if manual_data and symbol in manual_data:
        analysis['manual_data'] = manual_data[symbol]
        analysis['has_realtime'] = True
    else:
        analysis['has_realtime'] = False
    
    return analysis

# Fungsi untuk analisis real-time sederhana
def get_realtime_signals(df):
    """Sinyal trading real-time berdasarkan data Yahoo (delayed 15-20 menit)"""
    if df is None or len(df) < 5:
        return None
    
    latest = df.iloc[-1]
    
    signals = {
        'timestamp': df.index[-1],
        'price': latest['Close'],
        'sma_20': latest.get('SMA_20', df['Close'].rolling(20).mean().iloc[-1]),
        'rsi': ta.momentum.rsi(df['Close'], window=14).iloc[-1],
        'trend': 'UP' if latest['Close'] > df['Close'].iloc[-20] else 'DOWN',
        'volatility': df['Close'].pct_change().std() * 100
    }
    
    # Generate sinyal
    if signals['rsi'] < 30 and signals['trend'] == 'UP':
        signals['signal'] = 'BUY'
        signals['strength'] = 'STRONG'
    elif signals['rsi'] > 70 and signals['trend'] == 'DOWN':
        signals['signal'] = 'SELL'
        signals['strength'] = 'STRONG'
    elif latest['Close'] > signals['sma_20']:
        signals['signal'] = 'BUY'
        signals['strength'] = 'MODERATE'
    else:
        signals['signal'] = 'NEUTRAL'
        signals['strength'] = 'WEAK'
    
    return signals

# Main App
def main():
    st.title("🎯 HYBRID STOCK ANALYSIS PRO")
    st.markdown("*Menggabungkan Data Real-time, Delayed, dan Manual Input*")
    
    # Sidebar - Pilih Saham
    st.sidebar.header("⚙️ Konfigurasi")
    
    symbol = st.sidebar.text_input("Kode Saham (contoh: BBCA.JK)", "BBCA.JK").upper()
    if not symbol.endswith('.JK'):
        symbol += '.JK'
    
    # Input Data Manual (Real-time dari broker Anda)
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Input Data Real-time")
    
    with st.sidebar.expander("➕ Input Data Broker Hari Ini"):
        col1, col2 = st.columns(2)
        with col1:
            foreign_buy = st.number_input("Foreign Buy (Miliar)", min_value=0.0, value=0.0, step=0.1)
            local_buy = st.number_input("Local Buy (Miliar)", min_value=0.0, value=0.0, step=0.1)
        with col2:
            foreign_sell = st.number_input("Foreign Sell (Miliar)", min_value=0.0, value=0.0, step=0.1)
            local_sell = st.number_input("Local Sell (Miliar)", min_value=0.0, value=0.0, step=0.1)
        
        big_lot_buy = st.number_input("Big Lot Buy (Juta)", min_value=0, value=0, step=100)
        big_lot_sell = st.number_input("Big Lot Sell (Juta)", min_value=0, value=0, step=100)
        
        if st.button("💾 Simpan Data"):
            manual_data = load_manual_data()
            manual_data[symbol] = {
                'timestamp': datetime.now().isoformat(),
                'foreign': {'buy': foreign_buy, 'sell': foreign_sell, 'net': foreign_buy - foreign_sell},
                'local': {'buy': local_buy, 'sell': local_sell, 'net': local_buy - local_sell},
                'big_lot': {'buy': big_lot_buy, 'sell': big_lot_sell, 'net': big_lot_buy - big_lot_sell}
            }
            save_manual_data(manual_data)
            st.success("Data tersimpan!")
    
    # Load data
    if st.sidebar.button("🔍 Analisis"):
        with st.spinner("Mengambil data..."):
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            
            if not df.empty:
                df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
                
                # Flatten multi-index jika ada
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # Tabs
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 Real-time Technical", 
                    "🕵️ Bandarmologi (T+1)", 
                    "📈 Hybrid Analysis", 
                    "💡 Panduan Penggunaan"
                ])
                
                # Tab 1: Real-time Technical (Data paling update dari Yahoo)
                with tab1:
                    st.markdown('<div class="realtime-box">', unsafe_allow_html=True)
                    st.markdown("### ⏱️ REAL-TIME TECHNICAL ANALYSIS")
                    st.markdown(f"**Data terakhir:** {df.index[-1]} (Delayed ~15-20 menit dari bursa)")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    signals = get_realtime_signals(df)
                    
                    if signals:
                        cols = st.columns(4)
                        with cols[0]:
                            st.metric("Current Price", f"Rp {signals['price']:,.0f}")
                        with cols[1]:
                            st.metric("RSI (14)", f"{signals['rsi']:.1f}")
                        with cols[2]:
                            st.metric("Trend", signals['trend'])
                        with cols[3]:
                            color = "green" if signals['signal'] == 'BUY' else "red" if signals['signal'] == 'SELL' else "gray"
                            st.markdown(f"<h3 style='color: {color}; text-align: center;'>{signals['signal']}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align: center;'>{signals['strength']}</p>", unsafe_allow_html=True)
                        
                        # Chart
                        fig = go.Figure()
                        fig.add_trace(go.Candlestick(
                            x=df.index, open=df['Open'], high=df['High'],
                            low=df['Low'], close=df['Close'], name="Price"
                        ))
                        
                        # Add SMA
                        df['SMA_20'] = df['Close'].rolling(20).mean()
                        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name="SMA 20", line=dict(color='orange')))
                        
                        fig.update_layout(title=f"{symbol} - Real-time Chart", xaxis_rangeslider_visible=False, height=500)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Tab 2: Bandarmologi (Data T+1)
                with tab2:
                    st.markdown('<div class="delayed-box">', unsafe_allow_html=True)
                    st.markdown("### 📅 BANDARMOLOGI ANALYSIS (T+1)")
                    st.markdown("**⚠️ Data Delayed:** Analisis ini menggunakan data closing kemarin. Gunakan untuk melihat trend jangka menengah, bukan untuk entry hari ini.")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    manual_data = load_manual_data()
                    bandar = analyze_bandarmology_hybrid(df, symbol, manual_data)
                    
                    if bandar:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Trend", bandar['trend'])
                        with col2:
                            st.metric("Confidence", f"{bandar['confidence']}%")
                        with col3:
                            st.metric("Data Date", bandar['last_update'])
                        
                        st.markdown("---")
                        st.subheader("🎯 Interpretasi")
                        st.info(bandar['interpretation'])
                        
                        st.subheader("📋 Trading Implications")
                        st.success(bandar['trading_implications'])
                        
                        # Indicators Detail
                        with st.expander("📊 Detail Indicators"):
                            ind = bandar['indicators']
                            st.markdown(f"- **OBV Trend:** {ind['obv_trend']}")
                            st.markdown(f"- **A/D Trend:** {ind['ad_trend']}")
                            st.markdown(f"- **Price Trend:** {ind['price_trend']}")
                            st.markdown(f"- **Volume Ratio:** {ind['volume_ratio']:.2f}x")
                            st.markdown(f"- **Divergence:** {ind['obv_divergence']}")
                        
                        # Jika ada data manual
                        if bandar['has_realtime']:
                            st.markdown("---")
                            st.markdown('<div class="manual-input">', unsafe_allow_html=True)
                            st.markdown("### 📥 Data Real-time Anda Hari Ini:")
                            md = bandar['manual_data']
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.markdown(f"**Foreign Net:** {md['foreign']['net']:.1f}M")
                            with c2:
                                st.markdown(f"**Local Net:** {md['local']['net']:.1f}M")
                            with c3:
                                st.markdown(f"**Big Lot Net:** {md['big_lot']['net']:.0f}Jt")
                            st.markdown('</div>', unsafe_allow_html=True)
                
                # Tab 3: Hybrid Analysis (Gabungan)
                with tab3:
                    st.subheader("🔮 HYBRID ANALYSIS")
                    st.markdown("Menggabungkan sinyal dari berbagai sumber data")
                    
                    # Kombinasi sinyal
                    realtime_sig = get_realtime_signals(df) if 'signals' in locals() else None
                    bandar_sig = analyze_bandarmology_hybrid(df, symbol, load_manual_data())
                    
                    # Scoring
                    score = 0
                    reasons = []
                    
                    if realtime_sig:
                        if realtime_sig['signal'] == 'BUY': score += 30
                        if realtime_sig['strength'] == 'STRONG': score += 10
                        reasons.append(f"Technical: {realtime_sig['signal']} ({realtime_sig['strength']})")
                    
                    if bandar_sig:
                        if bandar_sig['trend'] == 'STRONG_ACCUMULATION': score += 30
                        elif bandar_sig['trend'] == 'ACCUMULATION': score += 20
                        if bandar_sig['indicators']['obv_divergence'] == 'Bullish': score += 15
                        reasons.append(f"Bandarmologi: {bandar_sig['trend']}")
                        
                        if bandar_sig['has_realtime']:
                            md = bandar_sig['manual_data']
                            if md['foreign']['net'] > 0: score += 15
                            if md['big_lot']['net'] > 0: score += 10
                            reasons.append(f"Foreign Flow: {'Positive' if md['foreign']['net'] > 0 else 'Negative'}")
                    
                    # Display
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown(f"<h1>{score}/100</h1>", unsafe_allow_html=True)
                        st.markdown("Hybrid Score")
                        
                        if score >= 80:
                            rec = "STRONG BUY"
                            color = "#00c853"
                        elif score >= 60:
                            rec = "BUY"
                            color = "#64dd17"
                        elif score >= 40:
                            rec = "NEUTRAL"
                            color = "#ffd600"
                        elif score >= 20:
                            rec = "REDUCE"
                            color = "#ff6d00"
                        else:
                            rec = "SELL"
                            color = "#dd2c00"
                        
                        st.markdown(f"<h2 style='color: {color};'>{rec}</h2>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("### 📝 Alasan:")
                        for reason in reasons:
                            st.markdown(f"- {reason}")
                        
                        st.markdown("### ⚖️ Confidence Level:")
                        if bandar_sig and bandar_sig['has_realtime']:
                            st.success("HIGH - Ada data real-time")
                        else:
                            st.warning("MEDIUM - Hanya data delayed")
                    
                    # Decision Matrix
                    st.markdown("---")
                    st.subheader("🎲 Decision Matrix")
                    
                    matrix_data = {
                        'Sumber Data': ['Technical (Real-time)', 'Bandarmologi (T+1)', 'Manual Input (Anda)', 'Kombinasi'],
                        'Kepentingan': ['Entry/Timing', 'Trend Direction', 'Konfirmasi Broker', 'Final Decision'],
                        'Keterbatasan': ['Delayed 15-20 menit', 'Delayed 1 hari', 'Manual input', 'Bergantung input'],
                        'Gunakan Untuk': ['Timing entry/exit', 'Filter saham', 'Validasi sinyal', 'Risk management']
                    }
                    st.table(pd.DataFrame(matrix_data))
                
                # Tab 4: Panduan
                with tab4:
                    st.subheader("💡 CARA MAKSIMALKAN APLIKASI INI")
                    
                    st.markdown("""
                    ### 🎯 Strategi Hybrid yang Efektif
                    
                    **1. SCREENING (Gunakan Tab Bandarmologi - T+1)**
                    ```
                    - Cari saham dengan score > 70 (Strong Accumulation)
                    - Filter yang OBV naik + Harga stabil/menurun (divergence bullish)
                    - Buat watchlist 5-10 saham kandidat
                    - Lakukan ini di malam hari setelah market close
                    ```
                    
                    **2. PREPARATION (Pagi sebelum market open)**
                    ```
                    - Buka watchlist kemarin
                    - Cek berita fundamental (corporate action, dll)
                    - Tentukan level entry berdasarkan support/resistance
                    - Siapkan data broker untuk di-input saat market open
                    ```
                    
                    **3. EXECUTION (Intraday - Real-time)**
                    ```
                    - Input data foreign/local flow dari platform broker Anda
                    - Lihat Technical Real-time untuk timing
                    - Jika Hybrid Score > 80 + Data broker konfirmasi = EXECUTE
                    - Gunakan Bandarmologi untuk validasi arah trend
                    ```
                    
                    **4. MANAGEMENT (Posisi terbuka)**
                    ```
                    - Bandarmologi T+1 tetap berguna untuk melihat apakah akumulasi berlanjut
                    - Jika OBV turun tapi harga naik (divergence bearish) = Pertimbangkan take profit
                    - Update data manual setiap jam jika perlu
                    ```
                    
                    ### ⚠️ Catatan Penting
                    
                    **Kenapa Delayed Data masih berguna:**
                    1. **Trend tidak berubah dalam 1 hari** - Akumulasi bandar butuh waktu minggu/bulan
                    2. **Konfirmasi** - Data T+1 memvalidasi apakah "smart money" masih di posisi
                    3. **Avoid noise** - Data real-time terlalu banyak noise, T+1 lebih "bersih"
                    
                    **Kapan Delayed Data TIDAK berguna:**
                    1. Untuk scalping (hold < 1 jam)
                    2. Saat ada news besar (earnings, aksi korporasi)
                    3. Market crash/panic sell (semua analisis teknikal gagal)
                    
                    ### 🔧 Tools Tambahan yang Perlu Anda Miliki
                    
                    Untuk data real-time yang lebih baik, pertimbangkan:
                    1. **RTI Business** (Berlangganan) - Data broker real-time
                    2. **IDX Mobile** - Data dasar real-time gratis
                    3. **Platform Broker** (Most Mandiri, BNI Sekuritas, dll) - Data nasabah broker tersebut
                    4. **TradingView** (Premium) - Data real-time dengan delay minimal
                    """)
                    
                    st.markdown("---")
                    st.info("""
                    **Kesimpulan:** Aplikasi ini adalah **FILTER dan ALAT KONFIRMASI**, bukan sinyal utama. 
                    Gunakan untuk mengurangi daftar saham dari 800+ menjadi 10-20 kandidat berkualitas, 
                    kemudian gunakan data real-time Anda untuk entry yang presisi.
                    """)
    
    else:
        # Welcome
        st.info("👈 Masukkan kode saham dan klik 'Analisis' untuk memulai")
        
        st.markdown("""
        ### 🚀 Selamat Datang di Hybrid Stock Analysis
        
        Aplikasi ini menggabungkan 3 sumber data:
        1. **📊 Real-time Technical** - Dari Yahoo Finance (delay 15-20 menit)
        2. **🕵️ Bandarmologi** - Analisis trend T+1 (berguna untuk screening)
        3. **📥 Manual Input** - Data broker real-time dari platform Anda
        
        ### 🎯 Gunakan Aplikasi Ini Jika:
        - Anda ingin **screening saham** di malam hari untuk persiapan besok
        - Anda punya akses ke **data broker dasar** (foreign flow) tapi ingin analisis otomatis
        - Anda ingin **belajar membaca perilaku bandar** tanpa berlangganan mahal
        - Anda butuh **konfirmasi multi-sumber** sebelum entry
        
        ### ❌ Jangan Gunakan Jika:
        - Anda **scalper** yang butuh data tick-by-tick real-time
        - Anda **tidak punya waktu** input data manual sama sekali
        - Anda **hanya mengandalkan** sinyal tanpa paham logikanya
        """)

if __name__ == '__main__':
    main()
