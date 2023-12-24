-- SELECT fromDate , toDate , status FROM Organization_leaverequest 
-- where Organization_id = 2 AND TeamId_id = 45;

-- SELECT fromDate , toDate , status , createdBy_id FROM Organization_leaverequest 
-- where Organization_id = 2  AND createdBy_id = 3 AND "2023-12-11" BETWEEN fromDate AND toDate;

SELECT
                            count(*) as total,
                            count(LeaveType) as count,
                            LeaveType,
                            id
                        FROM
                            Organization_leaverequest
                        where
                            Organization_id = 2  AND
                            TeamId_id = 46 AND
                            status = "ACCEPTED" AND
                            '2023-12-27' BETWEEN fromDate AND toDate
                        GROUP BY status;