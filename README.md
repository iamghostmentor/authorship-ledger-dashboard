# Authorship Ledger: Interactive Dashboard

Bonus deliverable for the BUS 440 Final Assessment. Authorship Ledger is a
process-provenance system for verifying human-AI collaborative academic and
creative work. This dashboard turns the analytics workbook into something you
can interact with. All figures are fictional, modeled for the assignment.

## Sections

- **Overview**: four KPI cards (status quo cost, ledger cost from Year 2, annual
  savings, break-even) that follow whatever assumptions are set in the model.
- **Expected Value Model**: a live calculator. Six sliders drive seven outputs,
  a Year 1 to Year 4 cost chart with the break-even year marked, and a callout
  that rewrites itself as assumptions change. Only this section reruns when a
  slider moves (`st.fragment`), so the page does not reload.
- **Build vs. Buy**: radar chart of the two options. Hover any vertex for its
  score and the reason behind it.
- **Dataset Explorer**: 55 fictional case records with department, flag status
  and Submission ID filters, plus detector flag rate by department (rate, not
  raw count).

## Data

`data/authorship_ledger_cases.csv` holds the 55 fictional case records
(AL-1001 to AL-1055), exported from the `Fictional Dataset` sheet of the
assignment workbook so the dashboard and workbook use identical rows. Everything
in the Dataset Explorer is computed from this file at runtime and cached with
`@st.cache_data`.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io) with GitHub.
2. Click **Create app**, then **Deploy a public app from GitHub**.
3. Choose this repository, branch `main`, and set **Main file path** to `app.py`.
4. Optionally set a custom subdomain under **Advanced settings**.
5. Click **Deploy**. Dependencies install from `requirements.txt` automatically.

---

BUS 440 Final Assessment | Ephren Taylor | Dr. Ryan Wheaton
