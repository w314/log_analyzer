#!/usr/bin/env python3
import psycopg2
import sys

# Connect to database
try:
    conn = psycopg2.connect('dbname=news')
except psycopg2.Error as error:
    print('Unable to connect to database.')
    print(error.pgerror)
    print(error.diag.message_detail)
    sys.exit(1)

cur = conn.cursor()

# Create views.

# Create daily summary by auther and article view.
author_article_daily_summary_query = '''
    SELECT
        DATE(log.time) AS day,
        authors.id as author_id,
        articles.id as article_id,
        authors.name,
        articles.title,
        count(*) as num
    FROM log, articles, authors
    WHERE
        log.path != '/'
        AND
        articles.slug = REGEXP_REPLACE(log.path,'/article/','')
        AND
        articles.author = authors.id
        AND
        log.method = 'GET'
        AND
        log.status = '200 OK'
    GROUP BY
        day,
        author_id,
        article_id,
        log.method,
        log.status,
        articles.title,
        authors.name
'''
query = 'CREATE VIEW daily_summary AS' + author_article_daily_summary_query
cur.execute(query)


# Create daily status summary view
daily_status_summary_query = '''
SELECT DATE(time) as day, status, count(status) as num
FROM log
GROUP BY day, status
ORDER BY day, status
'''
query = 'CREATE VIEW daily_status_summary AS' + daily_status_summary_query
cur.execute(query)


# Run queries.

# List the most popular three articles of all time.
query = '''
    SELECT title, sum(num) as article_total
    FROM daily_summary
    GROUP BY title
    ORDER BY article_total DESC
    LIMIT 3
'''
cur.execute(query)
results = cur.fetchall()
print('\n1. The three most popular articles of all time:\n')
for row in results:
    print(row[0] + ' - ' + str(row[1]) + ' views')


# List the most popular article authors of all time.
query = '''
    SELECT name, sum(num) as author_total
    FROM daily_summary
    GROUP BY name
    ORDER BY author_total DESC
'''
cur.execute(query)
results = cur.fetchall()
print('\n\n\n2. The most popular article authors of all time:\n')
for row in results:
    print(row[0] + ' - ' + str(row[1]) + ' views')


# List days when more than 1% of requests lead to errors.
query = '''
    SELECT a.day, b.num*1.0/a.num * 100
    FROM daily_status_summary AS a, daily_status_summary AS b
    WHERE
        a.day = b.day
        AND
        a.status < b.status
        AND
        b.num * 1.0/a.num * 100 > 1
'''
cur.execute(query)
results = cur.fetchall()
print('\n\n\n3. Days when more than 1% of requests lead to errors:\n')
for row in results:
    print(row[0].strftime('%B %d, %Y') + ' - %3.1f%%' % row[1])


conn.close()
