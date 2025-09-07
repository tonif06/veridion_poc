# Power BI — Procurement POC Frontend
# Power BI Report — Entity Resolution POC

## Objectives
This Power BI project is built on top of the **entity resolution pipeline**.  
The goal is to give business users (marketing, sales, leadership) a clear view of:
- **How clean the supplier database is** (Matched, Needs Review, Unmatched, Clean vs. Has Flags).  
- **Why records match or fail to match** (scores, similarities, feature presence).  
- **Where the main data quality issues are** (QC flags such as missing address, no website, stale data).  
- **What to check next** (a prioritized review queue for manual validation).  

## Flow
1. **Input**: supplier records are processed by the Python pipeline.  
   - Output CSV: `output/matches_decisions.csv`  
   - Contains decisions, match scores, quality flags, and attributes.  

2. **Data Model**: Power BI imports `matches_decisions.csv`.  
   - Measures are created for counts, percentages, scores, feature presence, and QC flags.  
   - Measures are organized into folders (*Counts, Percentages, Quality, Scores, Features, QC Flags*).  

3. **Report Pages**:  
   - **Executive Summary**: overall health of the database.  
   - **Match Quality & Features**: what drives good or bad matches.  
   - **Data Quality Flags**: where the data problems are.  
   - **Review Queue**: what should be checked first.  

4. **End Users**:  
   - **Marketing** → build clean campaign lists and know enrichment needs.  
   - **Sales** → focus on high-confidence prospects and understand gaps.  
   - **Leadership** → see KPIs and data quality at a glance.  

## How to Use
- Refresh the model to load the latest `matches_decisions.csv` from the pipeline.  
- Navigate through the 4 pages to understand data health and priorities.  
- Use filters (country, city, decision) to focus on the areas that matter most.  
