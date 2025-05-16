import streamlit as st
import pandas as pd
import yfinance as yf
import requests_cache
from functools import lru_cache
from datetime import datetime
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
nse_path = os.path.join(DATA_DIR, "nse_equity_list.csv")
bse_path = os.path.join(DATA_DIR, "bse_equity_list.csv")
qualified_path = os.path.join(DATA_DIR, "qualified_tickers_quarters.csv")
excluded_path = os.path.join(DATA_DIR, "excluded_tickers_quarters.csv")

st.set_page_config(page_title="Quarterly Data Validator", layout="wide")
st.title("Financial Data Validator (Last-N-Quarters)")

st.markdown(
    """
    This tool reads the latest NSE and BSE equity data from the repo's `data/` directory.
    It validates which tickers have at least N quarters of available *quarterly* financials on Yahoo Finance.
    Results are saved back to the `data/` directory for downstream processing.
    """
)

min_quarters = st.number_input(
    "Minimum quarters (N) of data required",
    min_value=1, max_value=40, value=8, step=1
)

run_validation = st.button("Run Validation using repo-stored equity lists")

if run_validation:
    if not (os.path.exists(nse_path) and os.path.exists(bse_path)):
        st.error(
            "NSE or BSE input files not found in data/. Please update them."
        )
    else:
        nse_df = pd.read_csv(nse_path)
        bse_df = pd.read_csv(bse_path)
        nse_map = nse_df[['Ticker', 'ISIN']].drop_duplicates()
        nse_map['YF_Ticker'] = nse_map['Ticker'].astype(str) + '.NS'
        bse_map = (
            bse_df[['TckrSymb', 'ISIN']]
            .drop_duplicates()
            .rename(columns={'TckrSymb': 'Ticker'})
        )
        bse_map['YF_Ticker'] = bse_map['Ticker'].astype(str) + '.BO'
        combined = pd.concat([
            nse_map[['ISIN', 'YF_Ticker']],
            bse_map[['ISIN', 'YF_Ticker']]
        ]).drop_duplicates().reset_index(drop=True)
        tickers = combined['YF_Ticker'].tolist()
        st.write(f"🔎 Validating {len(tickers)} tickers…")

        requests_cache.install_cache('yf_cache_quarters', expire_after=86400)

        @lru_cache(maxsize=None)
        def get_quarter_dates(ticker):
            try:
                qfin = yf.Ticker(ticker).quarterly_financials
                if qfin is None or qfin.empty:
                    return []
                return list(qfin.columns)
            except Exception:
                return []

        qualified, excluded = [], []
        progress = st.progress(0)
        for idx, t in enumerate(tickers):
            quarters = get_quarter_dates(t)
            if len(quarters) >= min_quarters:
                qualified.append({'YF_Ticker': t, 'Quarters': [str(q) for q in quarters]})
            else:
                excluded.append({'YF_Ticker': t, 'Quarters': [str(q) for q in quarters]})
            progress.progress((idx + 1) / len(tickers))

        qual_df = pd.DataFrame(qualified)
        excl_df = pd.DataFrame(excluded)
        qual_df.to_csv(qualified_path, index=False)
        excl_df.to_csv(excluded_path, index=False)

        st.success(f"Validation complete. {len(qual_df)} tickers qualified, {len(excl_df)} excluded.")
        st.dataframe(qual_df.head())
