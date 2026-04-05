# Brazilian E-Commerce Analytics Dashboard

A professional data analytics dashboard built with **Python**, **Streamlit**, and **Plotly**. This project transforms raw e-commerce data (Olist Dataset) into actionable business insights focused on logistics, customer satisfaction, and payment behavior.

### 🔗 [View Live Dashboard](https://ecommerce-eda-dashboard-mwsjjkaoxcyltylmtzq8gr.streamlit.app/)

---

## The Business Challenge
Analyzing over 100k orders to identify operational bottlenecks. The project addresses key questions:
* How do delivery delays impact customer satisfaction?
* Which payment methods drive the highest average ticket?
* Where are the geographical "shipping taxes" affecting competitiveness?

## Key Insights & Features
1. **Logistics vs. Satisfaction:** Quantified the correlation between late deliveries and a ~40% drop in review scores.
2. **Payment Strategy:** Analyzed spending patterns across Credit Cards, Boleto, and Vouchers.
3. **Geographical Pricing:** Identified high shipping-to-price ratios in Northern Brazilian states.
4. **Demand Planning:** Mapped peak order hours to optimize server maintenance and support staffing.

## Tech Stack
* **Language:** Python 3.13
* **Libraries:** Pandas (Data Wrangling), Plotly (Interactive Visualizations), Streamlit (Web Framework)
* **Environment:** GitHub Actions & Streamlit Cloud Deployment

## Project Structure
* `app.py`: The main dashboard application code.
* `data/`: Contains the processed and sampled dataset (`olist_sample.csv`).
* `requirements.txt`: List of dependencies for cloud deployment.

## How to Run Locally
1. Clone the repo: `git clone https://github.com/nuna-bit/ecommerce-eda-dashboard.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`

---
**Data Source:** Olist Store Dataset on Kaggle.
