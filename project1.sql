DROP DATABASE IF EXISTS credit_risk_project;
CREATE DATABASE credit_risk_project;
USE credit_risk_project;
create table customers(
customer_id int primary key,
name varchar(50),
age int,
income decimal(10,2),
employment_type Varchar(20),
region varchar(20)
);
CREATE TABLE loans (
    loan_id INT PRIMARY KEY,
    customer_id INT,
    loan_amount DECIMAL(12,2),
    interest_rate DECIMAL(5,2),
    loan_purpose VARCHAR(20),
    tenure_months INT,
    loan_start_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
CREATE TABLE repayments (
    repayment_id INT PRIMARY KEY,
    loan_id INT,
    repayment_date DATE,
    amount_paid DECIMAL(10,2),
    due_date DATE,
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
);
select * from customers;
select * from loans;
select * from repayments;

select count(*) from customers;
select count(*) from loans;
select count(*) from repayments;  
select count(distinct repayment_id) from repayments;



CREATE OR REPLACE VIEW customer_features AS
SELECT
    c.customer_id,
    c.age,
    c.income,
    c.employment_type,
    c.region,

    COALESCE(l.num_loans, 0) AS num_loans,
    l.loan_amount_total,
    l.avg_interest_rate,
    l.avg_tenure_months,

    COALESCE(r.num_repayments, 0) AS num_repayments,
    r.total_paid_amount,
    r.late_payment_ratio

FROM customers c

LEFT JOIN (
    SELECT
        customer_id,
        COUNT(*) AS num_loans,
        SUM(loan_amount) AS loan_amount_total,
        AVG(interest_rate) AS avg_interest_rate,
        AVG(tenure_months) AS avg_tenure_months
    FROM loans
    GROUP BY customer_id
) l ON c.customer_id = l.customer_id

LEFT JOIN (
    SELECT
        l.customer_id,
        COUNT(r.repayment_id) AS num_repayments,
        SUM(r.amount_paid) AS total_paid_amount,
        AVG(
            CASE
                WHEN r.repayment_date > r.due_date THEN 1.0
                ELSE 0.0
            END
        ) AS late_payment_ratio
    FROM loans l
    LEFT JOIN repayments r ON l.loan_id = r.loan_id
    GROUP BY l.customer_id
) r ON c.customer_id = r.customer_id;

SELECT *
FROM customer_features
LIMIT 10;





CREATE TABLE IF NOT EXISTS credit_scores (
    customer_id INT,
    credit_risk_score DECIMAL(5,4),
    risk_label INT,
    prediction_date DATE,
    PRIMARY KEY (customer_id)
);
select * from credit_scores




