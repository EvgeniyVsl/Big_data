import psycopg2
import csv
import sys
from datetime import datetime

def main(start_date, end_date):
    conn = psycopg2.connect(
        dbname='forum_logs',
        user='admin',
        password='secret',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()

    query = query = """
        WITH daily_stats AS (
            SELECT 
                DATE(timestamp) AS day,
                COUNT(*) FILTER (WHERE action_type = 'registration' AND server_response = 'success') AS new_accounts,
                COUNT(*) FILTER (WHERE action_type = 'create_message' AND server_response = 'success') AS total_messages,
                COUNT(*) FILTER (WHERE action_type = 'create_message' AND server_response = 'success' AND user_id IS NULL) AS anonymous_messages,
                COUNT(*) FILTER (WHERE action_type = 'create_topic' AND server_response = 'success') AS created_topics,
                COUNT(*) FILTER (WHERE action_type = 'delete_topic' AND server_response = 'success') AS deleted_topics
            FROM 
                logs
            WHERE 
                timestamp BETWEEN %s AND %s
            GROUP BY 
                DATE(timestamp)
        ),
        daily_topic_counts AS (
            SELECT
                day,
                new_accounts,
                total_messages,
                anonymous_messages,
                created_topics - deleted_topics AS daily_net_topics
            FROM
                daily_stats
        ),
        cumulative_topics AS (
            SELECT
                day,
                new_accounts,
                total_messages,
                anonymous_messages,
                daily_net_topics,
                SUM(daily_net_topics) OVER (ORDER BY day) AS running_total_topics
            FROM
                daily_topic_counts
        ),
        with_previous AS (
            SELECT
                *,
                LAG(running_total_topics, 1) OVER (ORDER BY day) AS previous_total
            FROM
                cumulative_topics
        )
        SELECT 
            day,
            new_accounts,
            CASE 
                WHEN total_messages > 0 THEN ROUND((anonymous_messages::numeric / total_messages::numeric) * 100, 2)
                ELSE 0 
            END AS percent_anonymous,
            total_messages,
            CASE 
                WHEN previous_total > 0 THEN ROUND(((running_total_topics - previous_total) / previous_total::numeric) * 100, 2)
                WHEN previous_total = 0 AND running_total_topics > 0 THEN 100.00
                ELSE NULL 
            END AS topic_change_percent
        FROM 
            with_previous
        ORDER BY 
            day;
        """

    cur.execute(query, (start_date, end_date))
    rows = cur.fetchall()

    with open('report.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['day', 'new_accounts', 'percent_anonymous', 'total_messages', 'topic_change_percent'])
        for row in rows:
            writer.writerow(row)

    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python aggregate.py <start_date> <end_date>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])