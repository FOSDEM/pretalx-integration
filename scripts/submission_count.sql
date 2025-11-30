SELECT 
    count(*), 
    st.name::json->>'en' AS track_name
FROM submission_submission ss 
RIGHT JOIN submission_track st ON ss.track_id = st.id
WHERE ss.event_id = 14
GROUP BY st.name::json->>'en'
ORDER BY count DESC;
