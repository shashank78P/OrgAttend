SELECT fromDate , leaveType , toDate from Organization_leaverequest WHERE 
Organization_id = 2  AND
TeamId_id = 38 AND
'2024-01-02' BETWEEN fromDate AND toDate;

SELECT
    count(*) as total,
    count(LeaveType) as count,
    LeaveType,
    id
FROM
    Organization_leaverequest
where
    Organization_id = 2  AND
    TeamId_id = 38 AND
    status = "ACCEPTED" AND
    '2024-01-02' BETWEEN fromDate AND toDate
GROUP BY leaveType;