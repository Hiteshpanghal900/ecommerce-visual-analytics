# Team Work Log — E-Commerce Visual Analytics

## Hitesh Binjrawat & Hitesh (Panghal) — Orders Table & Product Table
- Cleaned and processed the master orders table
  - `data_cleaning/cleaning_master_order_table.ipynb`
  - `data-visualization/cleaned_master_order_table.csv`, `cleaned_master_order_table1.csv`, `cleaned_master_order_table2.csv`
- EDA on the orders table (split into two parts for deeper analysis)
  - `EDA/eda_orders.ipynb`
  - `EDA/eda_master_orders_table.ipynb`
- Category/product-level master table work
  - `data_cleaning/clean_category_master_table.ipynb`
  - `dashboard/data/category_summary.csv`, `category_quality.csv`
- Supporting documentation
  - `questions_ans_by_table/orders_table1.md`, `orders_table2_questions.md`, `category_table_questions.md`
- Review/sentiment-related EDA
  - `EDA/review_message_analysis.ipynb`, `EDA/business_priority.csv`, `EDA/high_risk_topics.csv`, `EDA/sentiment_summary.csv`, `EDA/topic_summary.csv`
- **Combined EDA** (joint effort by both Hiteshes): `combined_eda.ipynb`, `EDA/combined_eda.ipynb`

## Ansh Rajani — Seller Table
- Built and cleaned the seller-level master table
  - `data-visualization/data-processing-seller_master.ipynb`
  - `data-visualization/seller_level_master_table.csv`, `cleaned_seller_level_master_table.csv`
  - `data_cleaning/clean_seller_master_table.ipynb`
- EDA on seller master table
  - `EDA/eda_seller_master_table.ipynb`
  - `data-visualization/seller_product_analysis.ipynb`
- Supporting documentation
  - `questions_ans_by_table/seller_table_questions.md`
- Dashboard build-out
  - `dashboard/app.py`, `dashboard/prepare_dashboard_data.py`, `dashboard/data/seller_summary.csv`, `seller_quality.csv`, `state_seller_summary.csv`

## Pratik Dey — Customer Table
- Built and cleaned the customer-level master table
  - `data-visualization/data-processing-customer_master.ipynb`
  - `data-visualization/customer_level_master_table.csv`, `cleaned_customer_level_master_table.csv`
- EDA and findings on customer data
  - `data-visualization/customer-master-analysis.ipynb`
  - `data_cleaning/cleaning_customer_master_table.ipynb`
- Supporting documentation
  - `questions_ans_by_table/customer_table_questions.md`
- Dashboard customer summaries
  - `dashboard/data/customer_delay_repeat_summary.csv`, `customer_quadrant_summary.csv`, `customer_repeat_overview.csv`, `state_customer_summary.csv`

## Tanisha Sushil — Marketing Funnel
- Built the marketing funnel master table
  - `data-visualization/marketing-funnel.ipynb`
  - `data-visualization/marketing_funnel_master_table.csv`, `cleaned_marketing_funnel_master_table.csv`
- Cleaning and EDA
  - `data_cleaning/clean_marketing_funnel_table.ipynb`
  - `EDA/marketing-funnel-analysis.ipynb`
- Supporting documentation
  - `questions_ans_by_table/marketing_funnel_table_questions.md`
- Dashboard funnel summaries
  - `dashboard/data/funnel_overview.csv`, `funnel_business_type_share.csv`, `funnel_origin_conversion.csv`
- **Final presentation**: `Ecommerce_Visual_Analytics_Presentation.pptx`

## Cross-team Deliverables
| Deliverable | Owner(s) |
|---|---|
| Combined EDA (`combined_eda.ipynb`) | Both Hiteshes (Binjrawat & Panghal) |
| Technical report (`report/technical_report.tex`, `report/figures/`) | Ansh Rajani & Pratik Dey |
| Final presentation (`Ecommerce_Visual_Analytics_Presentation.pptx`) | Tanisha Sushil |
