INSERT INTO customer_count_per_employee
SELECT SupportRepId, employees.FirstName, employees.LastName, COUNT(CustomerId)
FROM (customers INNER JOIN employees ON customers.SupportRepId = employees.EmployeeId)
GROUP BY SupportRepId;
