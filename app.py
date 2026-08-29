import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(
    page_title="個人財務數據分析平台",
    page_icon="💰",
    layout="wide"
)

DATA_FILE = Path("pft_demo_monthly_2025_2026.csv")
INVESTMENT_FILE = Path("pft_demo_investments.csv")

@st.cache_data
def load_base_data():
    df = pd.read_csv(DATA_FILE)
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    return df.sort_values("month").reset_index(drop=True)

def get_demo_data():
    if "pft_demo_monthly_df" not in st.session_state:
        st.session_state.pft_demo_monthly_df = load_base_data().copy(deep=True)
    return st.session_state.pft_demo_monthly_df.copy(deep=True)

def save_data(df):
    st.session_state.pft_demo_monthly_df = (
        df.copy(deep=True).sort_values("month").reset_index(drop=True)
    )

def calculate_record(month, bank_total, stock_total, forex_total, credit_card,
                     salary, dividend, other_income, current_df):
    total_assets = bank_total + stock_total + forex_total
    net_worth = total_assets - credit_card

    previous_df = current_df[current_df["month"] < pd.to_datetime(month)]
    if len(previous_df) > 0:
        previous_net_worth = previous_df.iloc[-1]["net_worth"]
        asset_change = net_worth - previous_net_worth
        growth_rate = (
            asset_change / previous_net_worth * 100
            if previous_net_worth != 0 else 0
        )
    else:
        asset_change = 0
        growth_rate = 0

    return {
        "month": pd.to_datetime(month),
        "bank_total": float(bank_total),
        "stock_total": float(stock_total),
        "forex_total": float(forex_total),
        "credit_card": float(credit_card),
        "total_assets": float(total_assets),
        "net_worth": float(net_worth),
        "asset_change": float(asset_change),
        "growth_rate": float(growth_rate),
        "salary": float(salary),
        "dividend": float(dividend),
        "other_income": float(other_income)
    }


INVESTMENT_COLUMNS = [
    "date",
    "symbol",
    "transaction_type",
    "shares",
    "price",
    "transaction_amount",
    "fees_tax",
    "dividend_interest",
    "note"
]

@st.cache_data
def load_base_investments():
    if INVESTMENT_FILE.exists():
        investment_df = pd.read_csv(INVESTMENT_FILE)
        if not investment_df.empty:
            investment_df["date"] = pd.to_datetime(investment_df["date"])
        return investment_df

    return pd.DataFrame(columns=INVESTMENT_COLUMNS)

def load_investments():
    if "pft_demo_investment_df" not in st.session_state:
        st.session_state.pft_demo_investment_df = load_base_investments().copy(deep=True)
    return st.session_state.pft_demo_investment_df.copy(deep=True)

def save_investments(investment_df):
    st.session_state.pft_demo_investment_df = (
        investment_df.copy(deep=True).sort_values("date", ascending=False).reset_index(drop=True)
    )

df = get_demo_data()

# ==============================
# Sidebar
# ==============================
st.sidebar.title("💰 PFT Demo")
page = st.sidebar.radio(
    "功能選單",
    ["📊 財務分析 Dashboard", "📝 月度財務紀錄", "💹 投資紀錄", "⚙️ 財務設定"]
)

st.sidebar.divider()
st.sidebar.caption("作品集 Demo")
st.sidebar.caption("所有資料皆為模擬資料")

if st.sidebar.button("↺ 重設 Demo 資料", use_container_width=True):
    st.session_state.pft_demo_monthly_df = load_base_data().copy(deep=True)
    st.session_state.pft_demo_investment_df = load_base_investments().copy(deep=True)
    st.session_state.pft_demo_monthly_expense = 40000
    st.session_state.pft_demo_withdrawal_rate = 4.0
    st.session_state.pft_demo_bank_target = 30.0
    st.session_state.pft_demo_stock_target = 60.0
    st.session_state.pft_demo_forex_target = 10.0
    st.session_state.pft_demo_emergency_months = 6
    st.success("✅ Demo 資料與設定已恢復為預設模擬狀態。")
    st.rerun()

# ==============================
# 月度財務紀錄
# ==============================

# ==============================
# Demo 財務設定
# ==============================
if "pft_demo_monthly_expense" not in st.session_state:
    st.session_state.pft_demo_monthly_expense = 40000
if "pft_demo_withdrawal_rate" not in st.session_state:
    st.session_state.pft_demo_withdrawal_rate = 4.0
if "pft_demo_bank_target" not in st.session_state:
    st.session_state.pft_demo_bank_target = 30.0
if "pft_demo_stock_target" not in st.session_state:
    st.session_state.pft_demo_stock_target = 60.0
if "pft_demo_forex_target" not in st.session_state:
    st.session_state.pft_demo_forex_target = 10.0
if "pft_demo_emergency_months" not in st.session_state:
    st.session_state.pft_demo_emergency_months = 6

if page == "📝 月度財務紀錄":
    st.title("📝 月度財務紀錄")
    st.caption("新增模擬月度資產與收入資料，儲存後 Dashboard 將依資料重新計算。")
    st.info("此頁僅操作目前瀏覽工作階段的模擬資料，不會寫回共用 CSV，也不會連接私人 SQLite、Turso 或任何真實財務資料。")

    st.subheader("新增月度紀錄")

    with st.form("monthly_record_form"):
        st.markdown("#### 📅 紀錄月份")
        d1, d2 = st.columns(2)

        with d1:
            year = st.selectbox(
                "年份",
                options=list(range(2024, 2036)),
                index=3
            )

        with d2:
            month_num = st.selectbox(
                "月份",
                options=list(range(1, 13)),
                index=0,
                format_func=lambda x: f"{x} 月"
            )

        st.markdown("#### 💼 資產與負債")
        a1, a2 = st.columns(2)

        with a1:
            bank_total = st.number_input(
                "銀行資產（NT$）",
                min_value=0,
                value=650000,
                step=10000,
                format="%d"
            )

            forex_total = st.number_input(
                "外匯資產（NT$）",
                min_value=0,
                value=128000,
                step=1000,
                format="%d"
            )

        with a2:
            stock_total = st.number_input(
                "股票資產（NT$）",
                min_value=0,
                value=1020000,
                step=10000,
                format="%d"
            )

            credit_card = st.number_input(
                "信用卡未繳金額（NT$）",
                min_value=0,
                value=40000,
                step=1000,
                format="%d"
            )

        st.markdown("#### 💵 本月收入")
        i1, i2, i3 = st.columns(3)

        with i1:
            salary = st.number_input(
                "薪資收入（NT$）",
                min_value=0,
                value=56000,
                step=1000,
                format="%d"
            )

        with i2:
            dividend = st.number_input(
                "股息／利息（NT$）",
                min_value=0,
                value=0,
                step=500,
                format="%d"
            )

        with i3:
            other_income = st.number_input(
                "其他收入（NT$）",
                min_value=0,
                value=0,
                step=500,
                format="%d"
            )

        preview_total_assets = bank_total + stock_total + forex_total
        preview_net_worth = preview_total_assets - credit_card

        st.markdown("#### 🧮 儲存前試算")
        p1, p2 = st.columns(2)

        p1.metric(
            "本月總資產",
            f"NT$ {preview_total_assets:,.0f}"
        )

        p2.metric(
            "預估淨資產",
            f"NT$ {preview_net_worth:,.0f}"
        )

        submitted = st.form_submit_button(
            "➕ 新增模擬紀錄",
            width="stretch"
        )

    if submitted:
        month_string = f"{int(year):04d}-{int(month_num):02d}"
        month_date = pd.to_datetime(month_string)

        if (df["month"] == month_date).any():
            st.error(
                f"{month_string} 已經存在。"
                "Demo 第一版先避免覆蓋既有月份，請選擇其他月份。"
            )
        else:
            new_record = calculate_record(
                month_string,
                bank_total,
                stock_total,
                forex_total,
                credit_card,
                salary,
                dividend,
                other_income,
                df
            )

            updated_df = pd.concat(
                [df, pd.DataFrame([new_record])],
                ignore_index=True
            ).sort_values("month").reset_index(drop=True)

            updated_df["asset_change"] = updated_df["net_worth"].diff()
            updated_df["growth_rate"] = (
                updated_df["net_worth"].pct_change() * 100
            )

            save_data(updated_df)
            st.success(
                f"✅ 已新增 {month_string} 模擬紀錄。"
                "切換到「財務分析 Dashboard」即可查看更新結果。"
            )
            st.rerun()

    st.divider()
    st.subheader("目前 Demo 月度資料")

    display_df = df.copy()
    display_df["月份"] = display_df["month"].dt.strftime("%Y-%m")

    display_df = display_df[
        [
            "月份",
            "bank_total",
            "stock_total",
            "forex_total",
            "credit_card",
            "net_worth",
            "salary",
            "dividend",
            "other_income"
        ]
    ].rename(columns={
        "bank_total": "銀行",
        "stock_total": "股票",
        "forex_total": "外匯",
        "credit_card": "信用卡",
        "net_worth": "淨資產",
        "salary": "薪資",
        "dividend": "股息／利息",
        "other_income": "其他收入"
    })

    st.dataframe(
        display_df.style.format({
            "銀行": "NT$ {:,.0f}",
            "股票": "NT$ {:,.0f}",
            "外匯": "NT$ {:,.0f}",
            "信用卡": "NT$ {:,.0f}",
            "淨資產": "NT$ {:,.0f}",
            "薪資": "NT$ {:,.0f}",
            "股息／利息": "NT$ {:,.0f}",
            "其他收入": "NT$ {:,.0f}"
        }),
        width="stretch",
        hide_index=True
    )

# ==============================
# 投資紀錄
# ==============================
elif page == "💹 投資紀錄":
    st.title("💹 投資紀錄")
    st.caption("新增與查看模擬投資交易，展示投資資料的結構化紀錄與基本分析。")
    st.info("此頁僅使用作品集 Demo 資料，不會連接私人投資紀錄或任何真實帳戶。")

    investment_df = load_investments()

    # ------------------------------
    # 投資摘要
    # ------------------------------
    st.subheader("投資摘要")

    if investment_df.empty:
        transaction_count = 0
        buy_total = 0
        sell_total = 0
        dividend_total = 0
    else:
        transaction_count = len(investment_df)
        buy_total = investment_df.loc[
            investment_df["transaction_type"] == "買入",
            "transaction_amount"
        ].sum()
        sell_total = investment_df.loc[
            investment_df["transaction_type"] == "賣出",
            "transaction_amount"
        ].sum()
        dividend_total = investment_df["dividend_interest"].sum()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("交易筆數", f"{transaction_count} 筆")
    k2.metric("累計買入金額", f"NT$ {buy_total:,.0f}")
    k3.metric("累計賣出金額", f"NT$ {sell_total:,.0f}")
    k4.metric("累計股息／利息", f"NT$ {dividend_total:,.0f}")

    st.divider()

    # ------------------------------
    # 新增投資紀錄
    # ------------------------------
    st.subheader("新增模擬交易")

    st.markdown("#### 📅 交易資訊")
    transaction_type = st.selectbox(
        "交易類型",
        ["買入", "賣出", "股息"],
        key="investment_transaction_type"
    )

    with st.form("investment_form"):
        t1, t2 = st.columns(2)

        with t1:
            trade_date = st.date_input(
                "交易日期",
                value=pd.Timestamp("2027-01-15").date()
            )

        with t2:
            symbol = st.text_input(
                "投資標的",
                value="DEMO ETF",
                placeholder="例如：DEMO ETF"
            )

        st.markdown("#### 💰 交易金額")

        if transaction_type in ["買入", "賣出"]:
            m1, m2 = st.columns(2)

            with m1:
                shares = st.number_input(
                    "股數",
                    min_value=0,
                    value=100,
                    step=1,
                    format="%d"
                )

                price = st.number_input(
                    "單價（NT$）",
                    min_value=0,
                    value=50,
                    step=1,
                    format="%d"
                )

            with m2:
                fees_tax = st.number_input(
                    "手續費／稅（NT$）",
                    min_value=0,
                    value=20,
                    step=10,
                    format="%d"
                )

            dividend_interest = 0
            transaction_amount = shares * price

            st.markdown("#### 🧮 儲存前試算")
            p1, p2 = st.columns(2)
            p1.metric("成交金額", f"NT$ {transaction_amount:,.0f}")
            p2.metric("手續費／稅", f"NT$ {fees_tax:,.0f}")

        else:
            shares = 0
            price = 0
            fees_tax = 0

            dividend_interest = st.number_input(
                "股息／利息（NT$）",
                min_value=0,
                value=1000,
                step=100,
                format="%d"
            )

            transaction_amount = 0

            st.markdown("#### 🧮 儲存前試算")
            st.metric("本次股息／利息", f"NT$ {dividend_interest:,.0f}")

        note = st.text_input(
            "備註（Demo）",
            value="作品集模擬交易"
        )

        investment_submitted = st.form_submit_button(
            "➕ 新增模擬交易",
            width="stretch"
        )

    if investment_submitted:
        if not symbol.strip():
            st.error("請輸入投資標的。")
        elif transaction_type in ["買入", "賣出"] and shares <= 0:
            st.error("買入或賣出交易的股數必須大於 0。")
        elif transaction_type in ["買入", "賣出"] and price <= 0:
            st.error("買入或賣出交易的單價必須大於 0。")
        elif transaction_type == "股息" and dividend_interest <= 0:
            st.error("股息交易請輸入大於 0 的股息／利息金額。")
        else:
            new_investment = pd.DataFrame([{
                "date": pd.to_datetime(trade_date),
                "symbol": symbol.strip(),
                "transaction_type": transaction_type,
                "shares": float(shares),
                "price": float(price),
                "transaction_amount": float(transaction_amount),
                "fees_tax": float(fees_tax),
                "dividend_interest": float(dividend_interest),
                "note": note.strip()
            }])

            updated_investments = pd.concat(
                [investment_df, new_investment],
                ignore_index=True
            ).sort_values(
                "date",
                ascending=False
            ).reset_index(drop=True)

            save_investments(updated_investments)
            st.success("✅ 已新增模擬投資紀錄。")
            st.rerun()

    st.divider()

    # ------------------------------
    # 投資交易歷史
    # ------------------------------
    st.subheader("投資交易歷史")

    if investment_df.empty:
        st.warning("目前尚無投資交易紀錄。新增第一筆模擬交易後會顯示在這裡。")
    else:
        display_investments = investment_df.copy()
        display_investments["交易日期"] = pd.to_datetime(
            display_investments["date"]
        ).dt.strftime("%Y-%m-%d")

        display_investments = display_investments[
            [
                "交易日期",
                "symbol",
                "transaction_type",
                "shares",
                "price",
                "transaction_amount",
                "fees_tax",
                "dividend_interest",
                "note"
            ]
        ].rename(columns={
            "symbol": "投資標的",
            "transaction_type": "交易類型",
            "shares": "股數",
            "price": "單價",
            "transaction_amount": "成交金額",
            "fees_tax": "手續費／稅",
            "dividend_interest": "股息／利息",
            "note": "備註"
        })

        st.dataframe(
            display_investments.style.format({
                "股數": "{:,.0f}",
                "單價": "NT$ {:,.0f}",
                "成交金額": "NT$ {:,.0f}",
                "手續費／稅": "NT$ {:,.0f}",
                "股息／利息": "NT$ {:,.0f}"
            }),
            width="stretch",
            hide_index=True
        )

# ==============================
# 財務設定
# ==============================
elif page == "⚙️ 財務設定":
    st.title("⚙️ 財務設定")
    st.caption("調整 Demo 的財務分析假設，Dashboard 會依設定重新計算。")
    st.info("此頁僅修改目前 Demo 工作階段的模擬設定，不會連接私人 PFT 或任何真實財務資料。")

    st.subheader("🎯 財務自由設定")
    c1, c2 = st.columns(2)

    with c1:
        demo_monthly_expense = st.number_input(
            "每月生活支出（NT$）",
            min_value=0,
            value=int(st.session_state.pft_demo_monthly_expense),
            step=1000,
            format="%d"
        )

    with c2:
        demo_withdrawal_rate = st.number_input(
            "提領率（%）",
            min_value=0.1,
            max_value=20.0,
            value=float(st.session_state.pft_demo_withdrawal_rate),
            step=0.1,
            format="%.1f"
        )

    annual_expense_preview = demo_monthly_expense * 12
    freedom_target_preview = (
        annual_expense_preview / (demo_withdrawal_rate / 100)
        if demo_withdrawal_rate > 0 else 0
    )

    p1, p2 = st.columns(2)
    p1.metric("預估年度生活支出", f"NT$ {annual_expense_preview:,.0f}")
    p2.metric("財務自由目標", f"NT$ {freedom_target_preview:,.0f}")

    st.divider()
    st.subheader("📊 目標資產配置")

    a1, a2, a3 = st.columns(3)
    with a1:
        demo_bank_target = st.number_input(
            "銀行目標（%）",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.pft_demo_bank_target),
            step=1.0,
            format="%.0f"
        )
    with a2:
        demo_stock_target = st.number_input(
            "股票目標（%）",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.pft_demo_stock_target),
            step=1.0,
            format="%.0f"
        )
    with a3:
        demo_forex_target = st.number_input(
            "外匯目標（%）",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.pft_demo_forex_target),
            step=1.0,
            format="%.0f"
        )

    allocation_total = demo_bank_target + demo_stock_target + demo_forex_target
    if abs(allocation_total - 100) < 0.001:
        st.success(f"✅ 目標配置合計：{allocation_total:.0f}%")
    else:
        st.warning(f"⚠️ 目標配置目前合計 {allocation_total:.0f}%，儲存前請調整為 100%。")

    st.divider()
    st.subheader("🛟 緊急預備金")

    demo_emergency_months = st.number_input(
        "緊急預備金目標（月）",
        min_value=1,
        max_value=24,
        value=int(st.session_state.pft_demo_emergency_months),
        step=1,
        format="%d"
    )

    emergency_target_preview = demo_monthly_expense * demo_emergency_months
    st.metric("緊急預備金目標", f"NT$ {emergency_target_preview:,.0f}")

    st.divider()

    if st.button("💾 儲存 Demo 財務設定", use_container_width=True):
        if abs(allocation_total - 100) >= 0.001:
            st.error("銀行、股票與外匯的目標配置合計必須等於 100%。")
        else:
            st.session_state.pft_demo_monthly_expense = int(demo_monthly_expense)
            st.session_state.pft_demo_withdrawal_rate = float(demo_withdrawal_rate)
            st.session_state.pft_demo_bank_target = float(demo_bank_target)
            st.session_state.pft_demo_stock_target = float(demo_stock_target)
            st.session_state.pft_demo_forex_target = float(demo_forex_target)
            st.session_state.pft_demo_emergency_months = int(demo_emergency_months)
            st.success("✅ Demo 財務設定已更新。切回 Dashboard 即可查看重新計算後的結果。")

# ==============================
# Dashboard
# ==============================
else:
    latest = df.iloc[-1]
    start = df.iloc[0]

    monthly_expense = st.session_state.pft_demo_monthly_expense
    withdrawal_rate = st.session_state.pft_demo_withdrawal_rate / 100
    emergency_target_months = st.session_state.pft_demo_emergency_months

    bank_target = st.session_state.pft_demo_bank_target
    stock_target = st.session_state.pft_demo_stock_target
    forex_target = st.session_state.pft_demo_forex_target

    fi_target = monthly_expense * 12 / withdrawal_rate
    fi_progress = latest["net_worth"] / fi_target * 100
    fi_gap = max(fi_target - latest["net_worth"], 0)

    total_period_growth = (
        (latest["net_worth"] / start["net_worth"] - 1) * 100
    )

    allocation_total = (
        latest["bank_total"]
        + latest["stock_total"]
        + latest["forex_total"]
    )

    bank_ratio = latest["bank_total"] / allocation_total * 100
    stock_ratio = latest["stock_total"] / allocation_total * 100
    forex_ratio = latest["forex_total"] / allocation_total * 100

    bank_diff = bank_ratio - bank_target
    stock_diff = stock_ratio - stock_target
    forex_diff = forex_ratio - forex_target

    emergency_months = latest["bank_total"] / monthly_expense

    income_df = df.copy()
    income_df["year"] = income_df["month"].dt.year

    annual_income = (
        income_df.groupby("year")[["salary", "dividend", "other_income"]]
        .sum()
    )
    annual_income["total_income"] = annual_income.sum(axis=1)

    years = annual_income.index.tolist()
    latest_year = years[-1]
    latest_data_month = int(df["month"].max().month)
    latest_month_label = df["month"].max().strftime("%Y-%m")

    # 最新年度若尚未滿 12 個月，收入比較採同月份 YTD，避免拿部分年度與前一年全年比較。
    latest_ytd = income_df[
        (income_df["year"] == latest_year)
        & (income_df["month"].dt.month <= latest_data_month)
    ]
    latest_dividend = latest_ytd["dividend"].sum()
    latest_total_income = (
        latest_ytd[["salary", "dividend", "other_income"]]
        .sum()
        .sum()
    )

    if len(years) >= 2:
        previous_year = years[-2]
        previous_ytd = income_df[
            (income_df["year"] == previous_year)
            & (income_df["month"].dt.month <= latest_data_month)
        ]
        previous_dividend = previous_ytd["dividend"].sum()

        if previous_dividend > 0:
            passive_yoy = (latest_dividend / previous_dividend - 1) * 100
            passive_yoy_display = f"{passive_yoy:+.1f}%"
        elif latest_dividend == 0:
            passive_yoy_display = "—"
        else:
            passive_yoy_display = "N/A"
    else:
        previous_year = None
        passive_yoy_display = "—"

    q3_2025 = df[
        (df["month"] >= "2025-07-01")
        & (df["month"] <= "2025-09-30")
    ]

    if len(q3_2025) > 0:
        stock_drawdown = (
            q3_2025["stock_total"].min()
            / q3_2025["stock_total"].iloc[0]
            - 1
        ) * 100
    else:
        stock_drawdown = 0

    st.title("💰 個人財務數據分析平台")
    st.caption("Personal Finance Analytics Portfolio Demo")
    st.info("本儀表板使用 100% 模擬資料，不包含任何真實個人財務資訊。")

    st.header("🎯 財務自由進度")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("財務自由目標", f"NT$ {fi_target:,.0f}")
    f2.metric("目前淨資產", f"NT$ {latest['net_worth']:,.0f}")
    f3.metric("目前達成率", f"{fi_progress:.1f}%")
    f4.metric("尚差金額", f"NT$ {fi_gap:,.0f}")
    st.progress(min(fi_progress / 100, 1.0))
    st.caption(f"Demo 假設：每月生活支出 NT$ {monthly_expense:,.0f}，以 {st.session_state.pft_demo_withdrawal_rate:.1f}% 提領率估算財務自由目標。")
    st.divider()

    st.header("💼 目前資產概況")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "目前淨資產",
        f"NT$ {latest['net_worth']:,.0f}",
        f"{latest['asset_change']:+,.0f} 本月"
    )
    c2.metric("本月成長率", f"{latest['growth_rate']:.2f}%")
    c3.metric("期間累計成長率", f"{total_period_growth:.1f}%")
    c4.metric("總資產", f"NT$ {latest['total_assets']:,.0f}")

    st.header("📈 淨資產趨勢")
    trend_chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "month:T",
                title="月份",
                axis=alt.Axis(format="%Y-%m", labelAngle=-45, tickCount=8)
            ),
            y=alt.Y(
                "net_worth:Q",
                title="淨資產（NT$）",
                scale=alt.Scale(zero=False)
            ),
            tooltip=[
                alt.Tooltip("month:T", title="月份", format="%Y-%m"),
                alt.Tooltip("net_worth:Q", title="淨資產", format=",.0f")
            ]
        )
        .properties(height=360)
    )
    st.altair_chart(trend_chart, use_container_width=True)
    st.caption("呈現 Demo 期間淨資產變化，用於觀察長期資產累積、市場波動與恢復趨勢。")
    st.divider()

    st.header("📊 資產配置分析")
    st.caption("比較目前資產配置與設定的目標配置。")

    allocation_df = pd.DataFrame({
        "資產類別": ["銀行", "股票", "外匯"],
        "目前配置": [bank_ratio, stock_ratio, forex_ratio],
        "目標配置": [bank_target, stock_target, forex_target],
        "配置差異": [bank_diff, stock_diff, forex_diff]
    })

    a1, a2, a3 = st.columns(3)
    a1.metric("銀行", f"{bank_ratio:.1f}%", f"{bank_diff:+.1f} 個百分點 vs 目標")
    a2.metric("股票", f"{stock_ratio:.1f}%", f"{stock_diff:+.1f} 個百分點 vs 目標")
    a3.metric("外匯", f"{forex_ratio:.1f}%", f"{forex_diff:+.1f} 個百分點 vs 目標")

    allocation_long = allocation_df.melt(
        id_vars="資產類別",
        value_vars=["目前配置", "目標配置"],
        var_name="配置類型",
        value_name="比例"
    )

    allocation_chart = (
        alt.Chart(allocation_long)
        .mark_bar()
        .encode(
            x=alt.X("資產類別:N", title=None),
            xOffset="配置類型:N",
            y=alt.Y(
                "比例:Q",
                title="配置比例（%）",
                scale=alt.Scale(domain=[0, 70])
            ),
            color=alt.Color("配置類型:N", title=None),
            tooltip=[
                alt.Tooltip("資產類別:N", title="資產類別"),
                alt.Tooltip("配置類型:N", title=""),
                alt.Tooltip("比例:Q", title="比例", format=".1f")
            ]
        )
        .properties(height=330)
    )
    st.altair_chart(allocation_chart, use_container_width=True)

    display_allocation = allocation_df.rename(columns={
        "目前配置": "目前配置 (%)",
        "目標配置": "目標配置 (%)",
        "配置差異": "配置差異 (%pt)"
    })

    st.dataframe(
        display_allocation.style.format({
            "目前配置 (%)": "{:.1f}%",
            "目標配置 (%)": "{:.1f}%",
            "配置差異 (%pt)": "{:+.1f}"
        }),
        width="stretch",
        hide_index=True
    )

    st.header("💡 財務洞察")
    i1, i2 = st.columns(2)

    with i1:
        st.subheader("資產成長")
        st.write(
            f"Demo 期間淨資產由 NT$ {start['net_worth']:,.0f} "
            f"增加至 NT$ {latest['net_worth']:,.0f}，"
            f"累計成長 **{total_period_growth:.1f}%**。"
        )

        st.subheader("資產配置")
        st.write(
            f"目前股票占總資產 **{stock_ratio:.1f}%**，"
            f"相較 {stock_target:.0f}% 目標"
            f"{'高' if stock_diff > 0 else '低'} "
            f"**{abs(stock_diff):.1f} 個百分點**。"
        )

    with i2:
        st.subheader("市場波動與恢復")
        st.write(
            f"2025 年 Q3 股票資產曾回落約 **{abs(stock_drawdown):.1f}%**，"
            "之後於 Q4 恢復成長。"
        )

        st.subheader("資金流動性")
        st.write(
            f"目前銀行資產約可支應 **{emergency_months:.1f} 個月**生活支出，"
            f"高於設定的 **{emergency_target_months} 個月**緊急預備金目標。"
        )

    st.divider()

    st.header("💵 收入與被動收入分析")

    income_plot = annual_income.reset_index().rename(columns={
        "year": "年度",
        "salary": "薪資收入",
        "dividend": "股息／利息",
        "other_income": "其他收入"
    })
    income_plot["年度"] = income_plot["年度"].astype(str)
    if latest_data_month < 12:
        income_plot.loc[
            income_plot["年度"] == str(latest_year),
            "年度"
        ] = f"{latest_year} YTD"

    income_long = income_plot.melt(
        id_vars="年度",
        value_vars=["薪資收入", "股息／利息", "其他收入"],
        var_name="收入類型",
        value_name="金額"
    )

    income_chart = (
        alt.Chart(income_long)
        .mark_bar()
        .encode(
            x=alt.X("年度:O", title="年度"),
            xOffset="收入類型:N",
            y=alt.Y("金額:Q", title="年度收入（NT$）"),
            color=alt.Color("收入類型:N", title="收入類型"),
            tooltip=[
                alt.Tooltip("年度:O", title="年度"),
                alt.Tooltip("收入類型:N", title="收入類型"),
                alt.Tooltip("金額:Q", title="金額", format=",.0f")
            ]
        )
        .properties(height=360)
    )

    st.altair_chart(income_chart, use_container_width=True)

    st.caption(f"最新資料月份：{latest_month_label}；最新年度指標採截至 {latest_data_month} 月的 YTD 口徑。")

    p1, p2, p3 = st.columns(3)
    p1.metric(f"{latest_year} YTD 股息／利息", f"NT$ {latest_dividend:,.0f}")
    p2.metric("被動收入 YTD YoY", passive_yoy_display)
    p3.metric(
        f"{latest_year} YTD 總收入",
        f"NT$ {latest_total_income:,.0f}"
    )

    st.header("📅 年度資產分析")

    annual_rows = []
    for year, group in df.groupby(df["month"].dt.year):
        first = group.iloc[0]["net_worth"]
        last = group.iloc[-1]["net_worth"]

        annual_rows.append({
            "年度": int(year),
            "年初／首月淨資產": first,
            "年末淨資產": last,
            "年度淨資產增加": last - first,
            "年度期間成長率 (%)": (last / first - 1) * 100,
            "股息／利息收入": group["dividend"].sum(),
            "年度總收入": (
                group["salary"]
                + group["dividend"]
                + group["other_income"]
            ).sum()
        })

    annual_summary = pd.DataFrame(annual_rows)

    st.dataframe(
        annual_summary.style.format({
            "年初／首月淨資產": "NT$ {:,.0f}",
            "年末淨資產": "NT$ {:,.0f}",
            "年度淨資產增加": "NT$ {:+,.0f}",
            "年度期間成長率 (%)": "{:.2f}%",
            "股息／利息收入": "NT$ {:,.0f}",
            "年度總收入": "NT$ {:,.0f}"
        }),
        width="stretch",
        hide_index=True
    )

    st.divider()

    st.header("🛟 緊急預備金")
    e1, e2, e3 = st.columns(3)
    e1.metric("目前可支應月份", f"{emergency_months:.1f} 個月")
    e2.metric("目標", f"{emergency_target_months} 個月")
    e3.metric(
        "超出目標",
        f"{max(emergency_months - emergency_target_months, 0):.1f} 個月"
    )

    st.progress(min(emergency_months / emergency_target_months, 1.0))
    st.caption(
        "Demo 中以銀行資產作為可快速動用的流動資產，"
        f"並以每月 NT$ {monthly_expense:,.0f} 模擬生活支出。"
    )

    st.divider()
    st.caption(
        "作品集 Demo｜Python · Pandas · Streamlit · Altair"
    )
