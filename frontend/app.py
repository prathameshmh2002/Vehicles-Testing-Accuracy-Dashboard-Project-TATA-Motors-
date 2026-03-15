import io
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Vehicle Testing Trend Analysis", layout="wide")
st.title("📊 Vehicle Testing Trend Analysis")
    # ----------------- BACKEND API CONFIG -----------------
API_URL = "http://127.0.0.1:8000"  # FastAPI server

@st.cache_data(show_spinner=False, ttl=60)
def fetch_data(limit: int = 5000) -> pd.DataFrame:
    url = f"{API_URL}/data?limit={limit}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    records = r.json()
    if not isinstance(records, list):
        records = []
    df = pd.DataFrame(records)

    # normalize column names to lowercase
    df.columns = [c.lower() for c in df.columns]

    # reorder columns to match DB structure
    col_order = [
        "record_id", "engine_no", "vc_no", "vin_no", "ecu_type",
        "time_toflash", "flashing_remark", "writing_remark", "pairing_remark", "static_remark",
        "flashing_status", "writing_status", "pairing_status", "static_status",
        "dtc_code", "station_id", "tcf_line", "plant_code",
        "prod_datetime", "tool_version", "cycle_time", "is_trial",
        "fmid", "bid", "bl_no", "bl_ver", "dts_transfer_date"
    ]
    ordered = [c for c in col_order if c in df.columns]
    rest = [c for c in df.columns if c not in ordered]
    df = df[ordered + rest]

    return df

# ----------------- EXPORT WIDGET -----------------
def export_data_menu(df: pd.DataFrame, title: str):
    with st.expander(f"📥 Export / View Options — {title}", expanded=False):
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            csv_bytes,
            file_name=f"{title.replace(' ', '_')}.csv",
            mime="text/csv",
        )
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
        st.download_button(
            "⬇️ Download Excel (.xlsx)",
            excel_buffer.getvalue(),
            file_name=f"{title.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        json_text = df.to_json(orient="records", indent=2)
        st.download_button(
            "⬇️ Download JSON",
            json_text,
            file_name=f"{title.replace(' ', '_')}.json",
            mime="application/json",
        )
        if st.checkbox(f"👁 View Data Table — {title}", key=f"view_{title}"):
            st.dataframe(df, use_container_width=True)

# ----------------- LOAD FROM API -----------------
with st.sidebar:
    st.header("🔌 Data Source")
    limit = st.number_input("Max records to fetch", 100, 100000, 5000, step=100)
    reload_clicked = st.button("🔄 Reload from API")

if reload_clicked:
    fetch_data.clear()

try:
    df_raw = fetch_data(limit=limit)
    if df_raw.empty:
        st.warning("No data returned from API.")
    else:
        st.success(f"✅ Loaded {len(df_raw):,} rows from API")
        st.write("### 🔍 Preview", df_raw.head())
except Exception as e:
    st.error(f"❌ Failed to load data from API: {e}")
    st.stop()

full_df = df_raw.copy()

# ----------------- FILTERS -----------------
st.sidebar.header("Filters")

# Dates
if "prod_datetime" in full_df.columns:
    full_df["prod_datetime"] = pd.to_datetime(full_df["prod_datetime"], errors="coerce")
    min_date = full_df["prod_datetime"].min()
    max_date = full_df["prod_datetime"].max()
    if pd.isna(min_date) or pd.isna(max_date):
        date_range = None
    else:
        date_range = st.sidebar.date_input("Select Date Range", [min_date.date(), max_date.date()])
else:
    date_range = None

# Plant
plant_filter = st.sidebar.multiselect(
    "Select Plant", sorted(full_df["plant_code"].dropna().unique())
) if "plant_code" in full_df.columns else None

# ECU
ecu_filter = st.sidebar.multiselect(
    "Select ECU Type", sorted(full_df["ecu_type"].dropna().unique())
) if "ecu_type" in full_df.columns else None

# ----------------- STATUS + RETEST LOGIC -----------------
status_cols = ["flashing_status", "writing_status", "static_status", "pairing_status"]

def determine_status(row):
    if any(row.get(col) == 0 for col in status_cols if col in row):
        return "NOT_EXECUTED"
    if any(row.get(col) == -1 for col in status_cols if col in row):
        return "NOK"
    if all(row.get(col) == 1 for col in status_cols if col in row):
        return "OK"
    return "UNKNOWN"

def apply_status_logic(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()
    for col in status_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["initial_status"] = df.apply(determine_status, axis=1)

    final_labels = []
    key_cols = [c for c in ["vc_no", "ecu_type", "station_id"] if c in df.columns]
    if not key_cols:
        df["final_category"] = df["initial_status"].astype(str).str.upper().str.strip()
        return df

    for keys, group in df.groupby(key_cols, sort=False):
        group = group.sort_values("prod_datetime", na_position="last")
        statuses = list(group["initial_status"])
        labels = []
        if not statuses:
            labels = ["UNKNOWN"] * len(group)
        else:
            first, *later = statuses
            if first == "OK":
                labels = ["OK"] * len(group)
            elif first == "NOT_EXECUTED":
                labels = ["NOT_EXECUTED"] * len(group)
            elif first == "NOK":
                labels = ["NOK"]
                for s in later:
                    if s == "OK":
                        labels.append("RETEST_OK")
                    elif s == "NOK":
                        labels.append("RETEST_NOK")
                    elif s == "NOT_EXECUTED":
                        labels.append("NOT_EXECUTED")
                    else:
                        labels.append("UNKNOWN")
            else:
                labels = [first] * len(group)
        final_labels.extend(labels)

    df["final_category"] = pd.Series(final_labels, index=df.index).astype(str).str.upper().str.strip()
    return df

# ----------------- APPLY LOGIC & FILTERS -----------------
filtered_df = apply_status_logic(full_df)

if date_range and "prod_datetime" in filtered_df.columns and len(date_range) == 2:
    start = pd.to_datetime(date_range[0])
    end = pd.to_datetime(date_range[1])
    filtered_df = filtered_df[
        (filtered_df["prod_datetime"] >= start) &
        (filtered_df["prod_datetime"] <= end)
    ]

if plant_filter:
    filtered_df = filtered_df[filtered_df["plant_code"].isin(plant_filter)]

if ecu_filter:
    filtered_df = filtered_df[filtered_df["ecu_type"].isin(ecu_filter)]

# ----------------- KPIs -----------------
total_tests = len(filtered_df)
ok_count = (filtered_df["final_category"] == "OK").sum()
nok_count = (filtered_df["final_category"] == "NOK").sum()
retest_ok_count = (filtered_df["final_category"] == "RETEST_OK").sum()
retest_nok_count = (filtered_df["final_category"] == "RETEST_NOK").sum()
not_executed_count = (filtered_df["final_category"] == "NOT_EXECUTED").sum()

valid_tests = ok_count + nok_count + retest_ok_count + retest_nok_count
yield_percent = ((ok_count + retest_ok_count) / valid_tests * 100) if valid_tests > 0 else 0

col0, col1, col2, col3, col4, col5 = st.columns(6)
col0.metric("📋 Total Tests", total_tests)
col1.metric("✅ OK", ok_count)
col2.metric("🔁 Retest OK", retest_ok_count)
col3.metric("🔁 Retest NOK", retest_nok_count)
col4.metric("❌ NOK", nok_count)
col5.metric("⚪ Not Executed", not_executed_count)
st.metric("🏆 Yield %", f"{yield_percent:.2f}%")

# ----------------- NOK ALERTS BY PLANT -----------------
st.subheader("🚨 Plant-wise NOK / Retest NOK Monitoring")

def get_nok_reason(row):
    reasons = []
    if row.get("flashing_status") == -1: reasons.append("Flashing")
    if row.get("writing_status") == -1: reasons.append("Writing")
    if row.get("static_status") == -1: reasons.append("Static")
    if row.get("pairing_status") == -1: reasons.append("Pairing")
    return ", ".join(reasons) if reasons else "Unknown"

if "plant_code" in filtered_df.columns:
    for plant in sorted(filtered_df["plant_code"].dropna().unique()):
        nok_df = filtered_df[
            (filtered_df["plant_code"] == plant) &
            (filtered_df["final_category"].isin(["NOK", "RETEST_NOK"]))
        ]
        if not nok_df.empty:
            st.error(f"⚠️ {len(nok_df)} NOK / Retest NOK detected in {plant}")
            view = nok_df.assign(nok_reason=nok_df.apply(get_nok_reason, axis=1))[
                ["vc_no", "ecu_type", "station_id", "plant_code",
                 "prod_datetime", "final_category", "nok_reason"]
            ]
            st.dataframe(view, use_container_width=True)
            export_data_menu(view, f"NOK_Details_{plant}")
        else:
            st.success(f"✅ No NOKs found for {plant}")

# ----------------- PIE CHART -----------------
st.subheader("📊 Status Distribution (Filtered)")
pie_df = filtered_df["final_category"].value_counts().reindex(
    ["OK", "RETEST_OK", "RETEST_NOK", "NOK", "NOT_EXECUTED"], fill_value=0
).reset_index()
pie_df.columns = ["Category", "Count"]

fig = px.pie(
    pie_df,
    names="Category",
    values="Count",
    color="Category",
    color_discrete_map={
        "OK": "green",
        "RETEST_OK": "lightgreen",
        "RETEST_NOK": "orange",
        "NOK": "red",
        "NOT_EXECUTED": "gray",
    },
    title="Filtered Status Distribution",
)
fig.update_traces(textinfo="percent+label", pull=[0.05] * len(pie_df))
st.plotly_chart(fig, use_container_width=True)
export_data_menu(pie_df, "Status_Distribution_Filtered")

# ----------------- ECU vs STATUS (Date & Plant filters only) -----------------
st.subheader("📊 ECU-wise Results by Plant (Ignoring ECU Filter)")
if {"ecu_type", "plant_code"}.issubset(full_df.columns):
    ecu_df = apply_status_logic(full_df)
    if date_range and "prod_datetime" in ecu_df.columns and len(date_range) == 2:
        start = pd.to_datetime(date_range[0]); end = pd.to_datetime(date_range[1])
        ecu_df["prod_datetime"] = pd.to_datetime(ecu_df["prod_datetime"], errors="coerce")
        ecu_df = ecu_df[(ecu_df["prod_datetime"] >= start) & (ecu_df["prod_datetime"] <= end)]
    if plant_filter:
        ecu_df = ecu_df[ecu_df["plant_code"].isin(plant_filter)]

    ecu_chart_data = ecu_df.groupby(["ecu_type", "final_category"]).size().reset_index(name="count")
    fig = px.bar(
        ecu_chart_data,
        x="ecu_type",
        y="count",
        color="final_category",
        barmode="stack",
        category_orders={"final_category": ["OK", "RETEST_OK", "RETEST_NOK", "NOK", "NOT_EXECUTED"]},
        title="ECU Type vs Status (Filtered by Date & Plant Only)",
    )
    fig.update_yaxes(dtick=1)
    fig.update_layout(xaxis_title="ECU Type", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)
    export_data_menu(ecu_chart_data, "ECU_Type_vs_Status_Filtered_by_Date_and_Plant")

# ----------------- TOP DTC CODES -----------------
if "dtc_code" in filtered_df.columns:
    st.subheader("🔧 Top 10 DTC Codes (Filtered)")
    top = filtered_df["dtc_code"].value_counts().head(10)
    st.bar_chart(top)
    top_export = top.reset_index()

# Ensure unique names
if "index" in top_export.columns:
    top_export.rename(columns={"index": "DTC_Code"}, inplace=True)
if "dtc_code" in top_export.columns:
    top_export.rename(columns={"dtc_code": "Count"}, inplace=True)

export_data_menu(top_export, "Top_10_DTC_Codes_Filtered")


# ----------------- HEATMAPS -----------------
st.sidebar.header("Heatmap Metric")
metric_choice = st.sidebar.radio(
    "Select Metric for Heatmap",
    ("Accuracy (%)", "Failure Rate (%)", "Test Volume"),
    index=0,
    key="ecu_heatmap_metric",
)

if "prod_datetime" in filtered_df.columns and "ecu_type" in filtered_df.columns:
    hm = filtered_df.copy()
    hm["Date"] = pd.to_datetime(hm["prod_datetime"], errors="coerce").dt.date
    grouped = hm.groupby(["Date", "ecu_type"], as_index=False).agg(
        total_tests=("vc_no", "count"),
        nok_tests=("final_category", lambda x: (x.isin(["NOK", "RETEST_NOK"])).sum()),
        ok_tests=("final_category", lambda x: (x.isin(["OK", "RETEST_OK"])).sum()),
    )
    grouped["failure_rate"] = (grouped["nok_tests"] / grouped["total_tests"] * 100).round(2)
    grouped["accuracy"] = (grouped["ok_tests"] / grouped["total_tests"] * 100).round(2)

    all_dates = sorted(hm["Date"].dropna().unique())
    ecu_list = sorted(hm["ecu_type"].dropna().unique())
    grid = pd.MultiIndex.from_product([all_dates, ecu_list], names=["Date", "ecu_type"])
    heatmap_df = pd.DataFrame(index=grid).reset_index().merge(grouped, how="left", on=["Date", "ecu_type"])
    heatmap_df["total_tests"] = heatmap_df["total_tests"].fillna(0)
    heatmap_df.rename(columns={"ecu_type": "ECU Type"}, inplace=True)

    metric_to_col = {
        "Accuracy (%)": "accuracy",
        "Failure Rate (%)": "failure_rate",
        "Test Volume": "total_tests",
    }
    chosen_col = metric_to_col[metric_choice]
    z_values = heatmap_df[chosen_col]

    # Bubble "heatmap"
    fig = px.scatter(
        heatmap_df,
        x="Date",
        y="ECU Type",
        size="total_tests",
        color=chosen_col,
        color_continuous_scale="RdYlGn_r",
        hover_data={
            "total_tests": True,
            "nok_tests": True,
            "ok_tests": True,
            "failure_rate": True,
            "accuracy": True,
        },
        title="📊 ECU Performance Over Time",
        size_max=20,
    )
    fig.update_traces(marker=dict(symbol="square"))
    st.plotly_chart(fig, use_container_width=True)
    export_data_menu(grouped, "ECU_Heatmap_Data")

    # True heatmap
    colorscale = "Greens" if metric_choice == "Accuracy (%)" else "Reds" if metric_choice == "Failure Rate (%)" else "Blues"
    colorbar_title = "%" if metric_choice in ("Accuracy (%)", "Failure Rate (%)") else "Count"
    hover_text = [
        f"<b>Date:</b> {d}<br><b>ECU:</b> {ecu}<br>"
        f"<b>Total Tests:</b> {vol or 0}<br>"
        f"<b>Failure Rate:</b> {fail if pd.notna(fail) else 0:.2f}%<br>"
        f"<b>Accuracy:</b> {acc if pd.notna(acc) else 0:.2f}%"
        for d, ecu, vol, fail, acc in zip(
            heatmap_df["Date"],
            heatmap_df["ECU Type"],
            heatmap_df["total_tests"],
            heatmap_df["failure_rate"],
            heatmap_df["accuracy"],
        )
    ]
    fig2 = go.Figure(data=go.Heatmap(
        z=z_values,
        x=heatmap_df["Date"],
        y=heatmap_df["ECU Type"],
        colorscale=colorscale,
        colorbar=dict(title=colorbar_title, thickness=20, tickfont=dict(size=12)),
        text=hover_text,
        hoverinfo="text",
        xgap=1, ygap=1,
    ))
    fig2.update_layout(
        title=f"{metric_choice} Heatmap (ECU Type)",
        xaxis=dict(
            title="Date",
            tickangle=45,
            tickmode="array",
            tickvals=all_dates,
            ticktext=[pd.to_datetime(d).strftime("%b %d") for d in all_dates],
            showgrid=False,
            automargin=True,
        ),
        yaxis=dict(title="ECU Type", automargin=True),
        height=600,
        margin=dict(l=150, r=50, t=80, b=150),
    )
    st.plotly_chart(fig2, use_container_width=True)
    export_data_menu(heatmap_df, "ECU_Heatmap_Grid_Data")

# ----------------- HIERARCHY + DAILY TRENDS -----------------
st.subheader("🌐 Station → TCF Line → ECU Type → Status Trends")
required_cols = {
    "station_id", "tcf_line", "ecu_type", "flashing_status", "writing_status",
    "pairing_status", "static_status", "prod_datetime", "record_id", "plant_code"
}

if required_cols.issubset(filtered_df.columns):
    hierarchy_df = filtered_df.copy()
    hierarchy_df["prod_date"] = pd.to_datetime(hierarchy_df["prod_datetime"], errors="coerce").dt.date

    fig_sunburst = px.sunburst(
        hierarchy_df,
        path=["station_id", "tcf_line", "ecu_type", "final_category"],
        values="record_id",
        color="final_category",
        color_discrete_map={
            "OK": "green",
            "RETEST_OK": "blue",
            "RETEST_NOK": "orange",
            "NOK": "red",
            "NOT_EXECUTED": "gray",
        },
    )
    st.plotly_chart(fig_sunburst, use_container_width=True)

    st.markdown("#### 📈 Daily ECU Status Trends (Stacked Area)")
    trend_summary = (
        hierarchy_df.groupby(["prod_date", "final_category"]).size().reset_index(name="count")
    )
    fig_area = px.area(
        trend_summary,
        x="prod_date",
        y="count",
        color="final_category",
        category_orders={"final_category": ["OK", "RETEST_OK", "RETEST_NOK", "NOK", "NOT_EXECUTED"]},
        color_discrete_map={
            "OK": "green",
            "RETEST_OK": "blue",
            "RETEST_NOK": "orange",
            "NOK": "red",
            "NOT_EXECUTED": "gray",
        },
        title="Daily ECU Status Trends (Stacked)",
    )
    fig_area.update_layout(xaxis_title="Date", yaxis_title="Number of Tests", hovermode="x unified")
    st.plotly_chart(fig_area, use_container_width=True)
    export_data_menu(trend_summary, "Daily_ECU_Status_Trends")

# ----------------- DTC CODE CATEGORIES -----------------
def split_dtc_codes(code):
    code = str(code).strip()
    if code.upper() == "NO ERRORS":
        return "NO_ERRORS"
    if code.upper().startswith("NO ERRORS|"):
        return "NO_ERRORS_MASKED"
    if "|" in code:
        return "UNMASKED_MASKED"
    return "UNKNOWN"

if "dtc_code" in df_raw.columns:
    df_raw["dtc_category"] = df_raw["dtc_code"].apply(split_dtc_codes)

    st.subheader("🔧 DTC Code Categories Summary")
    dtc_summary = df_raw["dtc_category"].value_counts().reset_index()
    dtc_summary.columns = ["Category", "Count"]
    st.bar_chart(dtc_summary.set_index("Category"))
    export_data_menu(dtc_summary, "DTC_Code_Categories_Summary")

    st.subheader("📋 DTC Category Mapping with ECU Info")
    columns_needed = ["vc_no", "ecu_type", "station_id", "tcf_line", "plant_code", "dtc_category"]
    if all(col in df_raw.columns for col in columns_needed[:-1]):
        dtc_table = df_raw[columns_needed]
        st.dataframe(dtc_table, use_container_width=True)
        export_data_menu(dtc_table, "DTC_Category_Mapping_ECU_Info")

# ----------------- STYLING -----------------
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f9f9f9, #eef2f7); font-family: 'Segoe UI', sans-serif; }
h1, h2, h3 { color: #2E86C1; font-weight: 800; text-align: center; }
div[data-testid="stMetric"] { background: white; padding: 20px; border-radius: 15px; box-shadow: 2px 4px 12px rgba(0,0,0,0.1); text-align: center; margin: 5px; }
section[data-testid="stSidebar"] { background-color: #2E86C1; color: white; }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] label { color: white; }
.js-plotly-plot .plotly .main-svg { border-radius: 15px !important; }
.stDataFrame { border: 2px solid #2E86C1; border-radius: 10px; }
.section-divider { border-top: 3px solid #2E86C1; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)
