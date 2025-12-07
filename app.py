import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="200 DMA Cross-Down Alert", layout="centered")

st.title("🔴 200 DMA Cross-Down Checker")

st.write(
    "Enter NSE symbol (e.g. `RELIANCE.NS`, `^NSEI`, `NIFTYBEES.NS`). "
    "Checks if **today's close crossed below yesterday's 200 DMA**."
)

symbol = st.text_input("Symbol", placeholder="RELIANCE.NS").upper().strip()

@st.cache_data
def check_200dma_cross(symbol: str):
    try:
        # Fetch 1.5 years to ensure 250+ trading days
        data = yf.download(symbol, period="1y", interval="1d", progress=False)
        
        if data.empty or len(data) < 210:
            return {"error": f"No data for {symbol}. Try RELIANCE.NS or ^NSEI"}
        
        data["200dma"] = data["Close"].rolling(window=200).mean()
        
        # Ensure we have at least 2 full rows with valid 200DMA
        if len(data) < 202 or data["200dma"].tail(2).isna().any():
            return {"error": f"Insufficient history for {symbol} (need 200+ days)"}
        
        last_two = data[["Close", "200dma"]].tail(2)
        
        y_close, t_close = last_two["Close"].values
        y_dma, t_dma = last_two["200dma"].values
        
        cross_down = (y_close > y_dma) and (t_close < t_dma)
        
        return {
            "success": True,
            "symbol": symbol,
            "cross_down": cross_down,
            "y_close": float(y_close),
            "t_close": float(t_close),
            "y_dma": float(y_dma),
            "t_dma": float(t_dma),
            "data": data.tail(250),
        }
    except Exception as e:
        return {"error": f"Error fetching {symbol}: {str(e)}"}

if symbol:
    with st.spinner(f"Fetching {symbol} data..."):
        result = check_200dma_cross(symbol)

    if "error" in result:
        st.error(result["error"])
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📉 Yesterday", f"₹{result['y_close']:.2f}")
            st.metric("200 DMA (Y)", f"₹{result['y_dma']:.2f}")
        with col2:
            st.metric("📊 Today", f"₹{result['t_close']:.2f}")
            st.metric("200 DMA (T)", f"₹{result['t_dma']:.2f}")

        if result["cross_down"]:
            st.error("🚨 **ALERT**: Price crossed BELOW 200 DMA today!")
            st.balloons()  # 🎉 visual alert
        else:
            st.success("✅ No downside cross today.")

        st.subheader("Recent Chart")
        chart_data = result["data"][["Close", "200dma"]]
        st.line_chart(chart_data, use_container_width=True)
