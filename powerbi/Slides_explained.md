# Power BI Report — Slide Explanations (Business Friendly, B2 English)

This document explains the content of the **4 main report pages** in simple language, so marketing and sales teams can use the insights directly.

---

## 1. Executive Summary — “The Health Check”
**Goal:** A quick overview of how clean and reliable the supplier database is.

**What it shows:**
- **Matched %** – how many records are clearly linked to real companies.  
- **Needs Review %** – how many require manual check.  
- **Unmatched %** – how many could not be linked at all.  
- **Clean %** – how many records are free of quality problems.  
- **Decision Split (Donut Chart)** – the share of Matched / Needs Review / Unmatched.  
- **Quality Split (100% stacked bar)** – Clean vs. Has Flags.  
- **Extra KPIs** – distinct matched companies, average match score, average name similarity, average freshness.

**Why it matters:**  
- **Marketing:** a clean list gives better targeting and campaign results.  
- **Sales:** know if the pipeline is based on trustworthy data.  
- **Leadership:** fast signal of where to invest in enrichment or cleanup.

---

## 2. Match Quality & Features — “Why it matches or not”
**Goal:** Show what helps or blocks record matching.

**What it shows:**
- **Website Present %, Country Match %, City Match %** – coverage of basic signals.  
- **Score Distribution (Histogram)** – how confidence scores are spread.  
- **Name Similarity Distribution (Histogram)** – how close the names are on average.  
- **Feature Presence by Decision** – compare feature coverage (website, country, city) for Matched, Needs Review, Unmatched.

**Why it matters:**  
- **Marketing:** better digital presence = easier campaign reach.  
- **Sales:** focus on areas where matches fail due to missing info.  
- **Data teams:** know which enrichment fields (website, address) bring the biggest gains.

---

## 3. Data Quality Flags — “Where the problems are”
**Goal:** Make data issues visible and measurable.

**What it shows:**
- **Top QC Flags (bar chart)** – most common problems: missing postcode, missing street, no website/social, old data, missing company type.  
- **Flags vs. Decision (100% stacked bar)** – how quality issues impact each category of decision.  
- **Flagged Records Table** – detailed view with name, country, city, flags, score, and decision.

**Why it matters:**  
- **Marketing:** know what fields are missing before building campaign lists.  
- **Sales:** see if missing info (like no website) blocks outreach.  
- **Operations:** flags act as a to-do list for enrichment priorities.

---

## 4. Review Queue — “What to check now”
**Goal:** A working list of records that need human validation.

**What it shows:**
- **Filters:** country, city, pre-set to only “Needs Review”.  
- **Review Table:** input name, matched company name, match score (sorted), similarity, flags, website, decision notes.  
- **Bookmark “Top 100 to Review”** – quick access to the most promising cases.

**Why it matters:**  
- **Sales:** focus first on the easiest wins (high score, small gaps).  
- **Marketing:** make sure campaign lists are validated before launch.  
- **Operations:** no random checking, but a clear, prioritized queue.

---

# Summary
Together, these 4 slides tell a clear story:  
1. **How healthy is our data?** (Executive Summary)  
2. **Why do matches succeed or fail?** (Match Quality & Features)  
3. **Where are the problems?** (Data Quality Flags)  
4. **What should we fix first?** (Review Queue)