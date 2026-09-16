# Resume Parser Project Report

## 1. Project Overview

The Resume Parser project explores the use of **Large Language Models (LLMs) for automated entity extraction and relationship detection from resumes**. The objective was to transform unstructured resume data into structured, queryable information that could support candidate profiling, data analysis, and future candidate-job matching applications.

The project began with a collection of **91 resume samples** stored in the `resume samples` folder. The dataset was subsequently deduplicated to remove duplicate Word documents where corresponding PDF versions of the same resumes were already available. This process resulted in a **deduplicated dataset of 51 resumes**.

Following the extraction and data-cleaning process, the resulting records produced **44 unique candidate profiles**, which were imported into a relational SQLite database for structured storage and analysis.

---

## 2. LLM-Based Entity Extraction

This phase focused on using a **Large Language Model (LLM), specifically ChatGPT, as an alternative approach for entity extraction and relationship detection from resumes**.

The model was instructed to extract structured information from each resume, including:

* Candidate name
* Target role
* Years of experience
* Phone number and email address
* LinkedIn URL and GitHub profile
* Location
* Professional skills
* Work experience
* Companies and employers
* Employment roles
* Employment dates
* Educational institutions
* Degrees and qualifications
* Graduation years

In addition to identifying individual entities, the extraction process captured relationships between them. For example, a candidate could be associated with a specific employer, job role, skill, educational institution, degree, and geographic location.

The extracted information was initially stored in **JSON format**, providing a structured representation of the information contained in the original resumes.

---

## 3. Data Transformation and Database Integration

The extracted JSON data was subsequently mapped into a relational SQLite database using the `import_to_database.py` script.

The database was designed to normalize the extracted information and preserve relationships between entities. This approach allows candidate information to be stored without unnecessarily duplicating common entities such as skills, companies, locations, institutions, and job titles.

The database contains **10 interconnected tables**:

1. `candidate`
2. `location`
3. `company`
4. `skill`
5. `candidate_skill`
6. `institution`
7. `degree`
8. `education`
9. `role`
10. `employment`

The relationships between these tables include **one-to-many, many-to-one, and many-to-many relationships**.

For example, candidates can have multiple skills, while a particular skill can belong to multiple candidates. This many-to-many relationship is implemented through the `candidate_skill` junction table.

Similarly, a candidate can have multiple employment and education records, while companies, roles, institutions, and degrees are stored as reusable entities.

---

## 4. Database Population

The extracted JSON records were mapped to the appropriate database entities and relationships.

The resulting database contains **44 unique candidate profiles**, representing the applicants retained in the final candidate dataset.

The relational structure makes it possible to query candidate information across multiple dimensions, including skills, target roles, employment history, education, companies, and geographic location.

---

## 5. Analytical Objectives

The database was developed to support exploratory analysis of the candidate dataset. The primary analytical questions were:

1. How many unique candidates were extracted?
2. What are the most popular skills among candidates?
3. Which target jobs are candidates most interested in?
4. Which locations are most represented among candidates?
5. What degrees and qualifications do candidates hold?
6. Which degree levels are most common?
7. Which companies appear most frequently across candidates' employment histories?
8. Which job titles appear most frequently in candidates' previous experience?

These questions demonstrate how the structured database can be used to move beyond extraction and into **candidate-market intelligence and workforce analysis**.

---

## 6. Key Findings

### 6.1 Candidate Population

The final database contains **44 unique candidate profiles**. These profiles represent the candidates retained after processing and deduplicating the original resume dataset.

### 6.2 Target Roles

The most frequently targeted roles were **Security Controls Assessor** and **Information Security Analyst**, with **three candidates targeting each role**.

This concentration indicates that cybersecurity and information security roles represent a significant proportion of the candidate pool and may warrant further investigation when assessing the composition of the applicant dataset.

### 6.3 Previous Job Experience

**Information Security Analyst** was the most frequently occurring previous job title among candidates, appearing in the employment history of **four candidates**. **Security Controls Assessor** followed, appearing among **three candidates**.

The concentration of these roles further demonstrates the strong representation of information security and cybersecurity-related professionals within the dataset.

### 6.4 Skills

**Excel** was the most frequently occurring skill in the extracted candidate profiles, appearing **19 times** across the dataset.

This suggests that spreadsheet-based analytical capability is widely represented among the candidates and may be a common foundational skill across the applicant pool.

### 6.5 Companies

**Dell Technologies, SAP NS2, and GDIT** were among the most frequently occurring companies in candidates' employment histories.

The presence of these organizations provides an additional dimension for understanding the professional backgrounds represented within the candidate dataset.

### 6.6 Educational Qualifications

The dataset contains a strong representation of both **master's and bachelor's degree holders**.

* **22 candidates** had master's-level qualifications.
* **20 candidates** had bachelor's-level qualifications.

The **Master of Business Administration (MBA)** was the most frequently occurring specific degree, appearing among **5 of the 44 candidates**.

---

## 7. Project Significance

The project demonstrates how LLM-based extraction can be used to convert large volumes of unstructured resume data into a **structured relational dataset** suitable for analysis.

Instead of treating resumes as standalone documents, the approach transforms them into interconnected entities representing candidates, skills, companies, roles, education, and locations. This creates a foundation for more advanced analytical applications, including:

* Candidate skills analysis
* Workforce and labour-market analysis
* Candidate-job matching
* Skills gap identification
* Talent pool segmentation
* Recruitment intelligence
* Employer and role analysis

The project therefore moves beyond simple resume parsing by demonstrating how **LLM-based extraction, relational data modelling, and SQL analysis can be combined to derive structured insights from unstructured candidate data.**

## 8. Conclusion

The Resume Parser project successfully established an end-to-end pipeline for transforming unstructured resumes into structured, queryable candidate data.

Starting with **91 resume samples**, the dataset was deduplicated to **51 resumes**, resulting in **44 unique candidate profiles** that were subsequently stored in a normalized SQLite database.

The project demonstrates the potential of LLMs to support automated information extraction while highlighting the importance of **data normalization, relationship modelling, validation, and structured database design** when converting extracted information into a reliable analytical dataset.

The resulting database provides a foundation for further evaluation of extraction accuracy and for developing more advanced candidate, skills, and labour-market analytics.
