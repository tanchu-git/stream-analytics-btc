-- A uniform input rate of incoming events works best with the function 'AnomalyDetection_SpikeAndDip'.
-- The first CTE makes the rate uniform using a tumbling window of 1 second.
WITH make_incoming_rate_uniform AS
(
    SELECT
        System.TIMESTAMP AS [Trade time UTC],
        AVG(CAST([Price] AS FLOAT)) as [Price]
    FROM [bitcoin-stream] TIMESTAMP BY DATEADD(millisecond, [Trade time], '1970-01-01T00:00:00Z') 
    GROUP BY TUMBLINGWINDOW(second, 1)
),
-- 'AnomalyDetection_SpikeAndDip' detects temporary anomalies in a time series event.
-- Using a 2 minute sliding window with a history size of 120 events. A confidence level of 98%.
-- The lower the confidence, the higher the number of anomalies detected, and vice versa.
anomaly_detection AS
(
    SELECT
        [Trade time UTC],
        [Price],
        AnomalyDetection_SpikeAndDip([Price], 98, 120, 'spikesanddips') OVER(LIMIT DURATION(second, 120)) as [Anomaly Result]
    FROM make_incoming_rate_uniform
),
-- A nested record with 2 columns is returned. Here I'm flattening it.
-- The computed p-value score (float) indicating how anomalous an event is.
-- A BIGINT (0 or 1) indicating if the event was anomalous or not.
result AS
(
    SELECT
        [Trade time UTC],
        [Price],
        CAST(GetRecordPropertyValue([Anomaly Result], 'Score') AS FLOAT) As [Anomaly Score],
        CAST(GetRecordPropertyValue([Anomaly Result], 'IsAnomaly') AS BIGINT) AS [Is Anomaly]
    FROM anomaly_detection
)    
-- The machine learning model is finicky at best. 
-- Using MATCH_RECOGNIZE clause to define 4 consecutive anomalies following 1 normal event as spike or dip.
SELECT
    *
INTO [btc-anomaly]
FROM result
    MATCH_RECOGNIZE (
        LIMIT DURATION (minute, 1)
        MEASURES
            First(Anomaly.[Trade time UTC]) AS [Starting time],
            Last(Anomaly.[Trade time UTC]) AS [Ending time],
            First(Anomaly.[Price]) AS [Starting price],
            Last(Anomaly.[Price]) AS [Ending price]
        AFTER MATCH SKIP TO NEXT ROW
        PATTERN (Normal+ Anomaly{4})
        DEFINE
            Normal AS Normal.[Is Anomaly] = 0,
            Anomaly AS Anomaly.[Is Anomaly] = 1
) AS T
