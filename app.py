import os
import io
import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# 1. PAGE CONFIGURATION & CUSTOM AESTHETICS
# ==============================================================================
st.set_page_config(
    page_title="Library Transactions Intelligence Hub",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern glassmorphism, gradient accents, and styled components
st.markdown("""
<style>
    /* Global polish */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Main container background glow */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(16, 185, 129, 0.06) 0%, transparent 40%),
                    #0F172A;
    }
    
    /* Hero Banner */
    .hero-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 18px;
        padding: 24px 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FFFFFF 0%, #E2E8F0 50%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.02rem;
        font-weight: 400;
        margin-bottom: 14px;
        line-height: 1.5;
    }
    
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.35);
        color: #C7D2FE;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .badge-pill-green {
        background: rgba(16, 185, 129, 0.15);
        border-color: rgba(16, 185, 129, 0.35);
        color: #A7F3D0;
    }

    /* KPI Metric Cards */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin-bottom: 25px;
    }
    
    .metric-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 14px;
        padding: 16px 18px;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-box:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 8px 20px -6px rgba(99, 102, 241, 0.2);
    }
    
    .metric-icon {
        font-size: 1.4rem;
        margin-bottom: 8px;
        display: inline-block;
    }
    
    .metric-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .metric-val {
        font-size: 1.7rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.1;
    }
    
    .metric-sub {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 4px;
    }

    /* Custom Section Headers */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F1F5F9;
        margin-top: 10px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Tab enhancements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(30, 41, 59, 0.5);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        padding: 0 16px;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
    }

    /* Report Card */
    .report-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 16px;
        font-family: monospace;
        color: #CBD5E1;
        font-size: 0.85rem;
        line-height: 1.6;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATA PROCESSING ENGINE (FAITHFUL EXTENSION OF lp.py)
# ==============================================================================
@st.cache_data(show_spinner=False)
def load_transaction_dataset(file_source=None):
    """
    Loads and cleans transaction data matching the logic of lp.py:
    - Resolves file path
    - Parses dates to datetime with errors='coerce'
    - Parses Borrowing duration(days) to numeric with errors='coerce'
    - Drops missing values via dropna()
    """
    if file_source is not None:
        df = pd.read_csv(file_source)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(base_dir, "library_transactions.csv")
        if not os.path.exists(default_path):
            return None, "File 'library_transactions.csv' not found in workspace."
        df = pd.read_csv(default_path)

    raw_count = len(df)
    
    # Clean and parse columns as in lp.py
    date_col = "Date(yyyy-mm-dd)"
    dur_col = "Borrowing duration(days)"

    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    else:
        # Fallback if column names differ
        for col in df.columns:
            if "date" in col.lower():
                df[date_col] = pd.to_datetime(df[col], errors="coerce")
                break

    if dur_col in df.columns:
        df[dur_col] = pd.to_numeric(df[dur_col], errors="coerce")
    else:
        for col in df.columns:
            if "duration" in col.lower() or "days" in col.lower():
                df[dur_col] = pd.to_numeric(df[col], errors="coerce")
                break

    # Missing values check & cleanup (matching lp.py dropna)
    missing_count = df.isnull().sum().sum()
    df = df.dropna().reset_index(drop=True)
    
    # Add helper features for analytics
    if date_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df["Month_Name"] = df[date_col].dt.strftime("%B")
        df["Month_Period"] = df[date_col].dt.to_period("M").astype(str)
        df["Day_Name"] = df[date_col].dt.day_name()
        df["Year"] = df[date_col].dt.year
    
    meta = {
        "raw_count": raw_count,
        "clean_count": len(df),
        "dropped_count": raw_count - len(df),
        "missing_count": missing_count
    }
    return df, meta


def compute_statistics(df):
    """
    Computes summary metrics as implemented in librarydashboard.calculate_statistics()
    and librarydashboard.generate_report() in lp.py.
    """
    if df is None or df.empty:
        return {}
    
    transactions = df["Transaction id"] if "Transaction id" in df.columns else df.iloc[:, 0]
    userid = df["User id"] if "User id" in df.columns else df.iloc[:, 2]
    booktitle = df["Book title"] if "Book title" in df.columns else df.iloc[:, 3]
    genre = df["Genre"] if "Genre" in df.columns else df.iloc[:, 4]
    duration = df["Borrowing duration(days)"] if "Borrowing duration(days)" in df.columns else df.iloc[:, 5]

    total_transactions = len(transactions)
    unique_users = userid.nunique()
    unique_books = booktitle.nunique()
    unique_genres = genre.nunique()
    avg_duration = float(np.mean(duration))
    max_duration = float(np.max(duration))
    min_duration = float(np.min(duration))

    date_col = "Date(yyyy-mm-dd)"
    if date_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[date_col]):
        day_counts = df[date_col].dt.day_name().value_counts()
        busiest_day = day_counts.idxmax() if not day_counts.empty else "N/A"
        busiest_day_count = day_counts.max() if not day_counts.empty else 0
    else:
        busiest_day = "N/A"
        busiest_day_count = 0

    top_books = booktitle.value_counts().head(10)
    top_book_name = top_books.index[0] if len(top_books) > 0 else "N/A"
    top_book_count = int(top_books.values[0]) if len(top_books) > 0 else 0

    top_genre = genre.value_counts().index[0] if genre.nunique() > 0 else "N/A"

    return {
        "total_transactions": total_transactions,
        "unique_users": unique_users,
        "unique_books": unique_books,
        "unique_genres": unique_genres,
        "avg_duration": avg_duration,
        "max_duration": max_duration,
        "min_duration": min_duration,
        "busiest_day": busiest_day,
        "busiest_day_count": busiest_day_count,
        "top_books": top_books,
        "top_book_name": top_book_name,
        "top_book_count": top_book_count,
        "top_genre": top_genre
    }


def compute_dac_aggregations(df):
    """
    Computes aggregations matching lp.py's dac() method:
    - Grouping by Genre: [count, mean]
    - Grouping by User id: [count, mean]
    """
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    dur_col = "Borrowing duration(days)"
    
    # Genre aggregation
    genre_grp = df.groupby("Genre")[dur_col].agg(["count", "mean"]).reset_index()
    genre_grp.columns = ["Genre", "Total_Borrowings", "Avg_Duration_Days"]
    genre_grp["Avg_Duration_Days"] = genre_grp["Avg_Duration_Days"].round(2)
    genre_grp = genre_grp.sort_values(by="Total_Borrowings", ascending=False).reset_index(drop=True)

    # User aggregation
    user_grp = df.groupby("User id")[dur_col].agg(["count", "mean"]).reset_index()
    user_grp.columns = ["User_ID", "Total_Borrowings", "Avg_Duration_Days"]
    user_grp["Avg_Duration_Days"] = user_grp["Avg_Duration_Days"].round(2)
    user_grp = user_grp.sort_values(by="Total_Borrowings", ascending=False).reset_index(drop=True)

    return genre_grp, user_grp


# ==============================================================================
# 3. SIDEBAR CONTROLS & DYNAMIC FILTERING (lp.py filter_transactions)
# ==============================================================================
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            <span style="font-size: 2rem;">📚</span>
            <div>
                <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">Library Analytics</h3>
                <span style="font-size: 0.75rem; color: #818CF8; font-weight: 600;">Powered by lp.py Engine</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # Data Source Selection
    st.markdown("##### 📁 Data Source")
    data_source_mode = st.radio(
        "Source Mode",
        options=["Default (library_transactions.csv)", "Upload Custom CSV"],
        label_visibility="collapsed"
    )

    uploaded_file = None
    if data_source_mode == "Upload Custom CSV":
        uploaded_file = st.file_uploader("Upload CSV transaction file", type=["csv"])

    # Load dataset
    raw_df, meta_info = load_transaction_dataset(uploaded_file)

    if raw_df is None:
        st.error(meta_info)
        st.stop()

    st.markdown("---")
    st.markdown("##### 🔍 Interactive Filters")
    st.caption("Filters update all charts, statistics, and reports in real time.")

    # 1. Date Range Filter
    date_col = "Date(yyyy-mm-dd)"
    min_date = raw_df[date_col].min().date()
    max_date = raw_df[date_col].max().date()

    date_selection = st.date_input(
        "📅 Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filter transactions by date range (lp.py filter option 2)"
    )

    if isinstance(date_selection, (tuple, list)) and len(date_selection) == 2:
        start_date, end_date = date_selection
    elif isinstance(date_selection, (tuple, list)) and len(date_selection) == 1:
        start_date, end_date = date_selection[0], date_selection[0]
    else:
        start_date, end_date = min_date, max_date

    # 2. Genre Multi-Select Filter (lp.py filter option 1)
    all_genres = sorted(raw_df["Genre"].unique().tolist())
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        select_all_genres = st.button("Select All", use_container_width=True, key="btn_sel_all")
    with col_g2:
        clear_all_genres = st.button("Clear All", use_container_width=True, key="btn_clr_all")

    if "selected_genres" not in st.session_state:
        st.session_state.selected_genres = all_genres

    if select_all_genres:
        st.session_state.selected_genres = all_genres
    elif clear_all_genres:
        st.session_state.selected_genres = []

    selected_genres = st.multiselect(
        "🏷️ Book Genres",
        options=all_genres,
        default=st.session_state.selected_genres if set(st.session_state.selected_genres).issubset(set(all_genres)) else all_genres,
        help="Filter transactions by specific book genres"
    )

    # 3. Borrowing Duration Slider
    min_dur = int(raw_df["Borrowing duration(days)"].min())
    max_dur = int(raw_df["Borrowing duration(days)"].max())

    selected_duration = st.slider(
        "⏳ Borrow Duration (Days)",
        min_value=min_dur,
        max_value=max_dur,
        value=(min_dur, max_dur),
        step=1,
        help="Filter transactions by loan period range"
    )

    # 4. Keyword Search Filter (Book Title or User ID)
    search_keyword = st.text_input(
        "🔎 Search Book or Member ID",
        value="",
        placeholder="e.g. Gatsby, Dune, U1046...",
        help="Quickly search across book titles and user identifiers"
    )

    # Reset Filter Button
    if st.button("🔄 Reset All Filters", use_container_width=True):
        st.session_state.selected_genres = all_genres
        st.rerun()

    st.markdown("---")
    # Dataset health badge
    st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08); font-size: 0.78rem;">
            <div style="color: #94A3B8; font-weight: 600; margin-bottom: 4px;">DATASET HEALTH</div>
            <div style="color: #E2E8F0;">• Clean records: <b style="color: #34D399;">{meta_info['clean_count']}</b> / {meta_info['raw_count']}</div>
            <div style="color: #E2E8F0;">• Date Span: <b style="color: #818CF8;">{min_date.strftime('%b %Y')}</b> to <b style="color: #818CF8;">{max_date.strftime('%b %Y')}</b></div>
        </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. APPLY ACTIVE FILTERS TO DATASET
# ==============================================================================
filtered_df = raw_df.copy()

# Date mask
filtered_df = filtered_df[
    (filtered_df[date_col].dt.date >= start_date) & 
    (filtered_df[date_col].dt.date <= end_date)
]

# Genre mask
if selected_genres:
    filtered_df = filtered_df[filtered_df["Genre"].isin(selected_genres)]
else:
    # If nothing selected, empty dataframe
    filtered_df = filtered_df.iloc[0:0]

# Duration mask
filtered_df = filtered_df[
    (filtered_df["Borrowing duration(days)"] >= selected_duration[0]) & 
    (filtered_df["Borrowing duration(days)"] <= selected_duration[1])
]

# Search keyword mask
if search_keyword.strip():
    kw = search_keyword.strip().lower()
    filtered_df = filtered_df[
        filtered_df["Book title"].str.lower().str.contains(kw) |
        filtered_df["User id"].str.lower().str.contains(kw) |
        filtered_df["Genre"].str.lower().str.contains(kw)
    ]

# Compute stats on filtered subset
stats = compute_statistics(filtered_df)
genre_summary, user_summary = compute_dac_aggregations(filtered_df)

# ==============================================================================
# 5. HERO BANNER & KPI CARDS (calculate_statistics() & generate_report())
# ==============================================================================
st.markdown(f"""
    <div class="hero-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div class="hero-title">📚 Library Transactions Intelligence Hub</div>
                <div class="hero-subtitle">
                    Interactive data explorer, circulation trends, reader behavior & catalog performance
                    built directly on the analysis logic of <code>lp.py</code>.
                </div>
                <div>
                    <span class="badge-pill">⚡ Active Engine: Python & Streamlit</span>
                    <span class="badge-pill badge-pill-green">🟢 Filtered Records: {len(filtered_df)} of {len(raw_df)} ({round(len(filtered_df)/len(raw_df)*100, 1) if len(raw_df)>0 else 0}%)</span>
                    <span class="badge-pill">📅 Range: {start_date.strftime('%d %b %Y')} → {end_date.strftime('%d %b %Y')}</span>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("⚠️ No records match your selected filter criteria. Please adjust your filters in the sidebar.")
    st.stop()

# 6 Metric KPI Boxes
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
        <div class="metric-box">
            <span class="metric-icon">📖</span>
            <div class="metric-label">Total Loans</div>
            <div class="metric-val">{stats.get('total_transactions', 0):,}</div>
            <div class="metric-sub">Active checkouts</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-box">
            <span class="metric-icon">👥</span>
            <div class="metric-label">Active Readers</div>
            <div class="metric-val">{stats.get('unique_users', 0)}</div>
            <div class="metric-sub">Unique library members</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-box">
            <span class="metric-icon">📕</span>
            <div class="metric-label">Book Titles</div>
            <div class="metric-val">{stats.get('unique_books', 0)}</div>
            <div class="metric-sub">Titles in circulation</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-box">
            <span class="metric-icon">🏷️</span>
            <div class="metric-label">Active Genres</div>
            <div class="metric-val">{stats.get('unique_genres', 0)}</div>
            <div class="metric-sub">Categories analyzed</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div class="metric-box">
            <span class="metric-icon">⏱️</span>
            <div class="metric-label">Avg Duration</div>
            <div class="metric-val">{stats.get('avg_duration', 0):.1f} <span style="font-size: 0.9rem; font-weight: 500; color: #94A3B8;">days</span></div>
            <div class="metric-sub">Min {int(stats.get('min_duration', 0))}d • Max {int(stats.get('max_duration', 0))}d</div>
        </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
        <div class="metric-box">
            <span class="metric-icon">⚡</span>
            <div class="metric-label">Busiest Day</div>
            <div class="metric-val" style="font-size: 1.35rem; color: #38BDF8;">{stats.get('busiest_day', 'N/A')}</div>
            <div class="metric-sub">{stats.get('busiest_day_count', 0)} checkouts</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 6. TABBED NAVIGATION
# ==============================================================================
tab_visuals, tab_catalog, tab_readers, tab_calc, tab_explorer = st.tabs([
    "📊 Core Visualizations (lp.py)",
    "📚 Catalog & Genre Deep Dive",
    "👥 Reader & Member Habits",
    "⏱️ Loan Return & Due Date Tool",
    "📋 Transaction Explorer & Export"
])

# ------------------------------------------------------------------------------
# TAB 1: CORE VISUALIZATIONS (Direct, enhanced representation of lp.py charts)
# ------------------------------------------------------------------------------
with tab_visuals:
    st.markdown("### 📊 Visual Analytics & Circulation Insights")
    st.caption("Includes all 4 visualization methods from `lp.py`: Top 10 Bar Chart, Monthly Trend Line, Genre Pie Chart, and Month vs Day Activity Heatmap.")
    
    # Toggle between Interactive Plotly and Matplotlib/Seaborn
    plot_engine = st.radio(
        "Chart Rendering Engine:",
        options=["Interactive Plotly (Hover, Zoom, Download)", "Matplotlib & Seaborn (Classic lp.py Style)"],
        horizontal=True
    )
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if plot_engine == "Interactive Plotly (Hover, Zoom, Download)":
        # Row 1: Bar Chart & Pie Chart
        row1_col1, row1_col2 = st.columns([1.2, 0.8])
        
        with row1_col1:
            st.markdown("##### 🏆 Top 10 Most Borrowed Books (`bar_chart`)")
            top10_books = filtered_df["Book title"].value_counts().head(10).reset_index()
            top10_books.columns = ["Book Title", "Borrow Count"]
            
            fig_bar = px.bar(
                top10_books,
                x="Borrow Count",
                y="Book Title",
                orientation="h",
                text="Borrow Count",
                color="Borrow Count",
                color_continuous_scale="Purples",
                title="Top 10 Most Borrowed Books"
            )
            fig_bar.update_layout(
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                margin=dict(l=20, r=20, t=40, b=20),
                coloraxis_showscale=False,
                height=380
            )
            fig_bar.update_traces(
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Borrow Count: %{x}<extra></extra>"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with row1_col2:
            st.markdown("##### 🥧 Genre Distribution (`pie_chart`)")
            genre_dist = filtered_df["Genre"].value_counts().reset_index()
            genre_dist.columns = ["Genre", "Transactions"]
            
            fig_pie = px.pie(
                genre_dist,
                names="Genre",
                values="Transactions",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title="Circulation Share by Genre"
            )
            fig_pie.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                height=380
            )
            fig_pie.update_traces(
                textposition="inside",
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Loans: %{value}<br>Share: %{percent}<extra></extra>"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Row 2: Monthly Trend Line & Activity Heatmap
        row2_col1, row2_col2 = st.columns([1.1, 0.9])
        
        with row2_col1:
            st.markdown("##### 📈 Monthly Borrowing Trend (`line_graph`)")
            trend_df = filtered_df.groupby("Month_Period").size().reset_index(name="Borrow Count")
            trend_df = trend_df.sort_values(by="Month_Period")

            fig_line = px.area(
                trend_df,
                x="Month_Period",
                y="Borrow Count",
                markers=True,
                title="Monthly Borrowing Trajectory",
                color_discrete_sequence=["#818CF8"]
            )
            fig_line.update_layout(
                plot_bgcolor="rgba(15, 23, 42, 0.4)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                xaxis_title="Month Period (YYYY-MM)",
                yaxis_title="Total Checkouts",
                margin=dict(l=20, r=20, t=40, b=20),
                height=380
            )
            fig_line.update_traces(
                line=dict(width=3, color="#6366F1"),
                marker=dict(size=8, color="#A5B4FC"),
                hovertemplate="<b>%{x}</b><br>Total Loans: %{y}<extra></extra>"
            )
            st.plotly_chart(fig_line, use_container_width=True)

        with row2_col2:
            st.markdown("##### 🗓️ Month vs Weekday Activity Heatmap (`heatmap`)")
            # Build pivot matrix as in lp.py
            temp_heat = filtered_df.copy()
            weekdays_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            # Group by Month and Day
            heat_pivot = temp_heat.groupby(["Month_Name", "Day_Name"]).size().unstack().fillna(0).astype(int)
            # Reindex weekdays that exist
            active_weekdays = [d for d in weekdays_order if d in heat_pivot.columns]
            heat_pivot = heat_pivot[active_weekdays]

            fig_heat = px.imshow(
                heat_pivot,
                labels=dict(x="Day of Week", y="Month", color="Loans"),
                x=heat_pivot.columns,
                y=heat_pivot.index,
                text_auto=True,
                color_continuous_scale="Purples",
                title="Borrowing Activity Density"
            )
            fig_heat.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                margin=dict(l=20, r=20, t=40, b=20),
                height=380
            )
            st.plotly_chart(fig_heat, use_container_width=True)

    else:
        # Classic Matplotlib & Seaborn rendering matching lp.py exactly
        st.info("Rendering charts with **Matplotlib** and **Seaborn** exactly as defined in `lp.py`.")
        
        m_col1, m_col2 = st.columns(2)
        
        with m_col1:
            st.markdown("##### 1. Top 10 Borrowed Books (Matplotlib)")
            topbooks = filtered_df["Book title"].value_counts().head(10)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor('#0F172A')
            ax.set_facecolor('#1E293B')
            bars = ax.bar(topbooks.index, topbooks.values, color='#6366F1', edgecolor='#818CF8')
            ax.set_title("Top 10 Borrowed Books", color='#F8FAFC', fontsize=14, pad=12)
            ax.set_xlabel("Book title", color='#94A3B8', fontsize=11)
            ax.set_ylabel("borrow number", color='#94A3B8', fontsize=11)
            ax.tick_params(colors='#CBD5E1', rotation=30)
            for spine in ax.spines.values():
                spine.set_color('#334155')
            ax.bar_label(bars, color='#F8FAFC', padding=3)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with m_col2:
            st.markdown("##### 2. Genre Distribution (Matplotlib)")
            genres = filtered_df["Genre"].value_counts()
            
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#0F172A')
            ax.set_facecolor('#0F172A')
            colors = plt.cm.Set3(np.linspace(0, 1, len(genres)))
            wedges, texts, autotexts = ax.pie(
                genres.values,
                labels=genres.index,
                autopct="%1.1f%%",
                startangle=90,
                colors=colors,
                textprops=dict(color="#F8FAFC")
            )
            ax.set_title("genre distribution", color='#F8FAFC', fontsize=14, pad=12)
            for at in autotexts:
                at.set_color('#0F172A')
                at.set_weight('bold')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        m_col3, m_col4 = st.columns(2)
        
        with m_col3:
            st.markdown("##### 3. Monthly Borrowing Trend (Matplotlib)")
            monthly = filtered_df.copy()
            trend = monthly.groupby(monthly[date_col].dt.to_period("M")).size()
            trend = trend.reset_index(name="count")
            trend["month"] = trend[date_col].astype(str)

            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor('#0F172A')
            ax.set_facecolor('#1E293B')
            ax.plot(trend["month"], trend["count"], marker='o', color='#38BDF8', linewidth=2.5)
            ax.set_title("monthly borrowing trend", color='#F8FAFC', fontsize=14, pad=12)
            ax.set_xlabel("month", color='#94A3B8', fontsize=11)
            ax.set_ylabel("borrow number", color='#94A3B8', fontsize=11)
            ax.tick_params(colors='#CBD5E1', rotation=30)
            for spine in ax.spines.values():
                spine.set_color('#334155')
            ax.grid(True, linestyle='--', alpha=0.2, color='#94A3B8')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with m_col4:
            st.markdown("##### 4. Correlation Heatmap (Seaborn)")
            temp = filtered_df.copy()
            temp["Month"] = temp[date_col].dt.strftime("%B")
            temp["Day"] = temp[date_col].dt.day_name()
            heat_data = temp.groupby(["Month", "Day"]).size().unstack().fillna(0).astype(int)

            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor('#0F172A')
            ax.set_facecolor('#1E293B')
            sns.heatmap(
                heat_data,
                cmap="coolwarm",
                annot=True,
                fmt="d",
                ax=ax,
                cbar_kws={'label': 'Borrowings'}
            )
            ax.set_title("correlation heatmap", color='#F8FAFC', fontsize=14, pad=12)
            ax.set_xlabel("day", color='#94A3B8', fontsize=11)
            ax.set_ylabel("month", color='#94A3B8', fontsize=11)
            ax.tick_params(colors='#CBD5E1')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

# ------------------------------------------------------------------------------
# TAB 2: CATALOG & GENRE DEEP DIVE (dac() grouping by Genre)
# ------------------------------------------------------------------------------
with tab_catalog:
    st.markdown("### 📚 Catalog & Genre Deep Dive")
    st.caption("Granular breakdown of borrowing patterns and average rental durations by genre and title (as computed in `lp.py.dac()`).")

    col_g1, col_g2 = st.columns([1.1, 0.9])
    
    with col_g1:
        st.markdown("##### 📊 Borrowing Duration & Volume by Genre (`dac`)")
        if not genre_summary.empty:
            fig_g = px.bar(
                genre_summary,
                x="Genre",
                y="Total_Borrowings",
                color="Avg_Duration_Days",
                color_continuous_scale="Viridis",
                text="Total_Borrowings",
                title="Loans per Genre (Colored by Avg Borrow Duration)"
            )
            fig_g.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                margin=dict(l=20, r=20, t=40, b=20),
                coloraxis_colorbar=dict(title="Avg Days"),
                height=360
            )
            fig_g.update_traces(
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Total Loans: %{y}<br>Avg Duration: %{marker.color} days<extra></extra>"
            )
            st.plotly_chart(fig_g, use_container_width=True)

    with col_g2:
        st.markdown("##### 📦 Borrow Duration Spread by Genre")
        fig_box = px.box(
            filtered_df,
            x="Genre",
            y="Borrowing duration(days)",
            color="Genre",
            points="all",
            title="Loan Length Dispersion (Days)"
        )
        fig_box.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
            height=360
        )
        fig_box.update_xaxes(tickangle=30)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")
    
    # Book Performance Leaderboard
    st.markdown("##### 🏆 Complete Book Performance Leaderboard")
    book_stats = filtered_df.groupby(["Book title", "Genre"]).agg(
        Total_Checkouts=("Transaction id", "count"),
        Avg_Duration_Days=("Borrowing duration(days)", "mean"),
        Min_Days=("Borrowing duration(days)", "min"),
        Max_Days=("Borrowing duration(days)", "max")
    ).reset_index()
    
    book_stats["Avg_Duration_Days"] = book_stats["Avg_Duration_Days"].round(1)
    book_stats["Share (%)"] = ((book_stats["Total_Checkouts"] / len(filtered_df)) * 100).round(1)
    book_stats = book_stats.sort_values(by="Total_Checkouts", ascending=False).reset_index(drop=True)
    book_stats.insert(0, "Rank", range(1, len(book_stats) + 1))

    st.dataframe(
        book_stats,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", format="#%d"),
            "Book title": st.column_config.TextColumn("Book Title", width="large"),
            "Genre": st.column_config.TextColumn("Genre"),
            "Total_Checkouts": st.column_config.ProgressColumn(
                "Total Loans",
                format="%d",
                min_value=0,
                max_value=int(book_stats["Total_Checkouts"].max()) if not book_stats.empty else 10
            ),
            "Share (%)": st.column_config.NumberColumn("Catalog Share", format="%.1f%%"),
            "Avg_Duration_Days": st.column_config.NumberColumn("Avg Duration", format="%.1f days"),
            "Min_Days": st.column_config.NumberColumn("Min (d)", format="%d"),
            "Max_Days": st.column_config.NumberColumn("Max (d)", format="%d")
        }
    )

# ------------------------------------------------------------------------------
# TAB 3: READER & MEMBER HABITS (dac() grouping by User id)
# ------------------------------------------------------------------------------
with tab_readers:
    st.markdown("### 👥 Reader & Member Habits Analysis")
    st.caption("Insights into library members, checkout frequencies, and loan durations (from `lp.py.dac()` user aggregation).")

    r_col1, r_col2 = st.columns([1.1, 0.9])
    
    with r_col1:
        st.markdown("##### 🥇 Top 10 Most Active Readers (`dac() User Aggregation`)")
        top_readers = user_summary.head(10)
        
        fig_users = px.bar(
            top_readers,
            x="User_ID",
            y="Total_Borrowings",
            color="Avg_Duration_Days",
            color_continuous_scale="Teal",
            text="Total_Borrowings",
            title="Top Active Library Members"
        )
        fig_users.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
            margin=dict(l=20, r=20, t=40, b=20),
            coloraxis_colorbar=dict(title="Avg Days"),
            height=360
        )
        fig_users.update_traces(
            textposition="outside",
            hovertemplate="<b>Member: %{x}</b><br>Loans: %{y}<br>Avg Loan Duration: %{marker.color} days<extra></extra>"
        )
        st.plotly_chart(fig_users, use_container_width=True)

    with r_col2:
        st.markdown("##### ⏱️ Overall Borrowing Duration Distribution")
        fig_hist = px.histogram(
            filtered_df,
            x="Borrowing duration(days)",
            nbins=12,
            title="Frequency of Borrowing Durations",
            color_discrete_sequence=["#38BDF8"]
        )
        fig_hist.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="Duration (Days)",
            yaxis_title="Count of Loans",
            height=360
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")
    
    # Reader Segmentation Summary
    st.markdown("##### 📋 Member Activity Summary")
    sub_col1, sub_col2, sub_col3 = st.columns(3)
    
    total_users_count = len(user_summary)
    multi_borrowers = len(user_summary[user_summary["Total_Borrowings"] > 1])
    single_borrowers = len(user_summary[user_summary["Total_Borrowings"] == 1])
    
    with sub_col1:
        st.metric(
            label="Total Active Members",
            value=total_users_count,
            delta="In filtered period"
        )
    with sub_col2:
        st.metric(
            label="Repeat Readers (>1 loan)",
            value=f"{multi_borrowers} ({round(multi_borrowers/total_users_count*100, 1) if total_users_count>0 else 0}%)",
            delta="High Engagement"
        )
    with sub_col3:
        st.metric(
            label="Single-Loan Readers",
            value=f"{single_borrowers} ({round(single_borrowers/total_users_count*100, 1) if total_users_count>0 else 0}%)",
            delta="Potential retention target",
            delta_color="inverse"
        )

# ------------------------------------------------------------------------------
# TAB 4: LOAN DUE DATE & RETURN RISK CALCULATOR
# ------------------------------------------------------------------------------
with tab_calc:
    st.markdown("### ⏱️ Interactive Loan Return & Due Date Calculator")
    st.caption("A dynamic utility tool for library desks and readers to estimate due dates, schedule returns, and mitigate overdue risks.")

    calc_col1, calc_col2 = st.columns([1, 1.2])

    with calc_col1:
        st.markdown("##### 📝 Loan Checkout Setup")
        
        available_books = sorted(raw_df["Book title"].unique().tolist())
        selected_calc_book = st.selectbox("Select Book Title", options=available_books)
        
        # Get book's genre and typical stats
        book_info = raw_df[raw_df["Book title"] == selected_calc_book]
        book_genre = book_info["Genre"].iloc[0] if not book_info.empty else "General"
        book_typical_duration = round(book_info["Borrowing duration(days)"].mean(), 1) if not book_info.empty else 14.0

        checkout_date = st.date_input("Checkout Date", value=datetime.date.today())
        
        duration_policy = st.radio(
            "Borrow Duration Policy",
            options=["Standard 7 Days", "Standard 14 Days", "Extended 21 Days", "Monthly 30 Days", "Custom Days"],
            index=1,
            horizontal=True
        )

        if duration_policy == "Standard 7 Days":
            loan_days = 7
        elif duration_policy == "Standard 14 Days":
            loan_days = 14
        elif duration_policy == "Extended 21 Days":
            loan_days = 21
        elif duration_policy == "Monthly 30 Days":
            loan_days = 30
        else:
            loan_days = st.slider("Select Custom Days", min_value=1, max_value=60, value=int(book_typical_duration))

        due_date = checkout_date + datetime.timedelta(days=loan_days)
        due_day_name = due_date.strftime("%A")

    with calc_col2:
        st.markdown("##### 🎯 Projected Return Analysis")
        
        is_weekend = due_day_name in ["Saturday", "Sunday"]
        is_busiest = due_day_name == stats.get("busiest_day", "")

        status_color = "#10B981"
        if is_weekend or is_busiest:
            status_color = "#F59E0B"

        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 14px; padding: 20px; margin-bottom: 16px;">
                <div style="color: #94A3B8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Due Date Summary</div>
                <div style="font-size: 2rem; font-weight: 800; color: #F8FAFC; margin-top: 4px;">
                    {due_date.strftime('%A, %d %B %Y')}
                </div>
                <div style="color: #CBD5E1; margin-top: 6px; font-size: 0.95rem;">
                    • Book: <b style="color: #A5B4FC;">{selected_calc_book}</b> ({book_genre})<br>
                    • Checkout: <b>{checkout_date.strftime('%d %b %Y')}</b> | Duration: <b>{loan_days} days</b><br>
                    • Typical historical loan for this title: <b>{book_typical_duration} days</b>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if is_busiest:
            st.warning(f"⚡ **High Footfall Advisory**: Return falls on **{due_day_name}**, which is the library's **busiest day** ({stats.get('busiest_day_count')} historical checkouts). Consider dropping off early!")
        elif is_weekend:
            st.info(f"ℹ️ **Weekend Drop-off**: Return falls on **{due_day_name}**. Please ensure weekend book return dropboxes are used if desk is closed.")
        else:
            st.success(f"✅ **Optimal Return Day**: Return falls on a regular weekday (**{due_day_name}**). Standard processing applies.")

        # Recommendations in same genre
        st.markdown(f"###### 💡 Recommended Next Reads in *{book_genre}*:")
        genre_recommendations = raw_df[
            (raw_df["Genre"] == book_genre) & 
            (raw_df["Book title"] != selected_calc_book)
        ]["Book title"].value_counts().head(3)

        if not genre_recommendations.empty:
            for rec_title, rec_count in genre_recommendations.items():
                st.markdown(f"- 📖 **{rec_title}** — Borrowed *{rec_count} times* by fellow readers")
        else:
            st.markdown(f"- 🌟 *{selected_calc_book}* is the premier standout in {book_genre}!")

# ------------------------------------------------------------------------------
# TAB 5: TRANSACTION EXPLORER & EXPORT (generate_report() & filter_transactions())
# ------------------------------------------------------------------------------
with tab_explorer:
    st.markdown("### 📋 Transaction Explorer & Data Export")
    st.caption("Inspect raw and filtered transaction logs, review the official summary report from `lp.py.generate_report()`, and export data.")

    # Executive Report Box (direct replication of lp.py.generate_report())
    st.markdown("##### 📄 Official lp.py Summary Report")
    report_text = f"""==================================================
LIBRARY TRANSACTIONS ANALYSIS REPORT (lp.py)
==================================================
Total Transactions Processed : {stats.get('total_transactions', 0)}
Unique Books in Circulation  : {stats.get('unique_books', 0)}
Unique Registered Users      : {stats.get('unique_users', 0)}
Unique Genres Represented    : {stats.get('unique_genres', 0)}
Average Borrowing Duration   : {stats.get('avg_duration', 0):.2f} days
Maximum Borrowing Duration   : {stats.get('max_duration', 0):.0f} days
Minimum Borrowing Duration   : {stats.get('min_duration', 0):.0f} days
Busiest Circulation Day      : {stats.get('busiest_day', 'N/A')} ({stats.get('busiest_day_count', 0)} checkouts)

TOP BORROWED BOOKS:
"""
    for idx, (bk, cnt) in enumerate(stats.get('top_books', pd.Series()).items(), 1):
        report_text += f"{idx:2d}. {bk:<40} : {cnt} loans\n"
    report_text += "=================================================="

    st.markdown(f'<div class="report-card">{report_text}</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Download Buttons
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        csv_buffer = io.StringIO()
        filtered_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv_buffer.getvalue(),
            file_name=f"library_transactions_filtered_{datetime.date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with exp_col2:
        st.download_button(
            label="📄 Download Summary Report (TXT)",
            data=report_text,
            file_name=f"library_report_{datetime.date.today().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown(f"##### 🔍 Filtered Records Table ({len(filtered_df)} Transactions)")

    # Display interactive data table
    display_df = filtered_df[[
        "Transaction id", "Date(yyyy-mm-dd)", "User id", "Book title", "Genre", "Borrowing duration(days)"
    ]].copy()
    display_df["Date(yyyy-mm-dd)"] = display_df["Date(yyyy-mm-dd)"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Transaction id": st.column_config.TextColumn("Transaction ID"),
            "Date(yyyy-mm-dd)": st.column_config.TextColumn("Checkout Date"),
            "User id": st.column_config.TextColumn("Member ID"),
            "Book title": st.column_config.TextColumn("Book Title", width="large"),
            "Genre": st.column_config.TextColumn("Genre"),
            "Borrowing duration(days)": st.column_config.NumberColumn(
                "Duration (Days)",
                format="%d days"
            )
        }
    )

    with st.expander("📊 Dataset Schema & Statistical Describe"):
        st.markdown("**Descriptive Statistics (`describe()`):**")
        st.dataframe(filtered_df.describe(), use_container_width=True)
