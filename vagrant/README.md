# Log Analysis

## App Description

The app runs an internal reporting tool. The "news" database it analyzes contains newspaper articles, as well as the web server log for a newspaper site. The log has a database row for each time a reader loads a web page.

The reporting tool gives the answer to the following questions:
1. List of the the three most popular articles.
2. List of the most popular article authors.
3. List of days when more than 1% of requests lead to errors.

## Setup

To run the app you have to set up the database running in a virtual machine. Please follow the following steps.

1. Install **VirtualBox**.
    Virtaul Box will run your virtaul machine. [You can download it here.](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
1. Install **Vagrant**.
    Vagrant will configure the virtual machine. [You can download it here.](https://www.vagrantup.com/downloads.html.)
1. Run the virtual machine. In your terminal change directory to vagrant and run `vagrant up`.
1. Log into the virtual machine with `vagrant ssh`.
1. Change directory to /vagrant with `cd /vagrant`.
1. Download [data the for the database](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip), unzip the file and copy newsdata.sql to the vagrant directory.
1. Populate the news database by running `psql -d news -f newsdata.sql`.


## Instructions

### For the queries to run the following views are created
1. Daily Summary By Author And Article View
    `CREATE VIEW daily_summary AS
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
        authors.name`

2. Daily Status Summary View
    `CREATE VIEW daily_status_summary AS 
    SELECT DATE(time) as day, status, count(status) as num
    FROM log
    GROUP BY day, status
    ORDER BY day, status`


### How to run the report
1. To run the log analysis run `python newsstat.py`
1. You can also find the output saved in the output.txt file.

## Attribution
Udacity: news database, vagrant configuration file
