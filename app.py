import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="200 DMA Cross-Down Alert", layout="centered")

st.title("200 DMA Cross-Down Checker")

st.write(
    "Enter a stock symbol. The app will check whether today's close has just "
    "crossed **below** the 200-day moving average compared to yesterday."
)

symbol = st.text_input("Symbol (e.g. RELIANCE.NS, NIFTYBEES.NS, ^NSEI)").upper().strip()

def check_200dma_cross(symbol: str):
    data = yf.download(symbol, period="1y", interval="1d", auto_adjust=True)

    if data.shape[0] < 210:
        return {"symbol": symbol, "enough_data": False, "cross_down": False, "msg": "Not enough history"}

    data["200dma"] = data["Close"].rolling(window=200).mean()

    last_two = data.tail(2)
    if last_two["200dma"].isna().any():
        return {"symbol": symbol, "enough_data": False, "cross_down": False, "msg": "200DMA not ready"}

    y_close = last_two["Close"].iloc[0]
    t_close = last_two["Close"].iloc[1]
    y_dma = last_two["200dma"].iloc[0]
    t_dma = last_two["200dma"].iloc[1]

    cross_down = (y_close > y_dma) and (t_close < t_dma)

    return {
        "symbol": symbol,
        "enough_data": True,
        "cross_down": cross_down,
        "y_close": float(y_close),
        "t_close": float(t_close),
        "y_dma": float(y_dma),
        "t_dma": float(t_dma),
        "data": data,
    }

if symbol:
    with st.spinner("Checking 200 DMA cross..."):
        result = check_200dma_cross(symbol)

    if not result["enough_data"]:
        st.error(result["msg"])
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Yesterday Close", f"{result['y_close']:.2f}")
            st.metric("Yesterday 200DMA", f"{result['y_dma']:.2f}")
        with col2:
            st.metric("Today Close", f"{result['t_close']:.2f}")
            st.metric("Today 200DMA", f"{result['t_dma']:.2f}")

        if result["cross_down"]:
            st.error("❗ Price has just crossed BELOW 200DMA today.")
        else:
            st.success("No downside 200DMA cross today.")

        # optional: show recent chart with 200DMA
        data = result["data"].tail(250)
        st.line_chart(data[["Close", "200dma"]])
