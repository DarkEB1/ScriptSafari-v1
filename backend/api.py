"""
Graph display - return graph
Add paper - (link) scrape, reputation, add to graph, return score, individual scores, graph, store link+attributes in table
Generate summary - (link) summary
Generate citation - (link, type) check for attributes in db, citation
Fetch paper information - (title) query graph
"""

#TODO ADD TRY EXCEPT TO EACH ENDPOINT
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from article_info_scrapers import *
from reputational_score import *
from graph import *
from citation_generator import *
from summary_generator import *
from author_info_scraper import *
import urllib

app = Flask(__name__)
CORS(app)
db = mysql.connector.connect(
    host="2.tcp.eu.ngrok.io",  # ngrok host
    port=12820,                # ngrok port
    user="root",               
    password="",               
    database="scriptsafari"    
)
cursor = db.cursor()
query1 = "SELECT content FROM graph WHERE cid=1"
cursor.execute(query1)
graph_data = cursor.fetchone()
cursor.close()
cursor2 = db.cursor()
query2 = "SELECT content FROM graph WHERE cid=2"
cursor2.execute(query2)
scores_data = cursor2.fetchone()
print(graph_data[0], scores_data[0])
global maingraph
maingraph = Graph(graph=graph_data[0], scores=scores_data[0])
print(maingraph)
if db.is_connected():
    print("connected successfuly")

@app.route("/")
def home():
    return 'ScriptSafari-API-v1'

@app.route('/add-paper/<path:paper_link>')
def add_paper(paper_link):
    user = request.args.get('email')
    print(user, paper_link)
    paper_link = urllib.parse.unquote(paper_link)
    article_data = scrape(paper_link)
    print(article_data)
    if article_data["title"]:
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM `graph-entries` WHERE title = %s"
        cursor.execute(query, (article_data["title"],))
        exists = cursor.fetchone()
        cursor.close()
        if exists:
            return jsonify({"error": "Node already in graph"}), 404
        else:
            graphcursor = db.cursor()
            authors_list = article_data["authors"]
            affiliations_list = article_data["affiliations"]
            query = """
            SELECT title 
            FROM `graph-entries`
            WHERE journal_name = %s 
            OR authors LIKE %s
            OR affiliations LIKE %s
            """
            like_authors_pattern = '%' + '%'.join(authors_list) + '%'
            like_affiliations_pattern = '%' + '%'.join(affiliations_list) + '%'
            try:
                graphcursor.execute(query, (article_data["title"], like_authors_pattern, like_affiliations_pattern))
                connected_titles = [row[0] for row in graphcursor.fetchall()]
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                connected_titles = []
            graphcursor.close()
            maingraph.firstsetscore(article_data["title"])
            maingraph.add(article_data["title"], connection=None)
            for connection in connected_titles:
                maingraph.add(article_data["title"], connection)
            ucursor = db.cursor()
            uquery = "SELECT uid FROM users WHERE email = %s"
            ucursor.execute(uquery, (user,))
            uid = ucursor.fetchone()
            ucursor.close()
            uid = uid[0]
            authors_string = ', '.join(article_data["authors"])
            affiliations_string = ', '.join(article_data["affiliations"])
            cursor2 = db.cursor(dictionary=True)
            query = "INSERT INTO `graph-entries` (uid, link, title, authors, affiliations, publication_date, journal_name, journal_volume, journal_pages, doi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor2.execute(query, (uid, paper_link, article_data["title"], authors_string, affiliations_string, article_data["publication_date"], article_data["journal_name"], article_data["journal_volume"], article_data["journal_pages"], article_data["doi"]))
            db.commit()
            print(maingraph.graph())
            score = defaultscore(article_data, maingraph, db) #written to database within that program
            finalcursor = db.cursor()
            finalquery = "UPDATE graph SET content = %s WHERE cid = 1"
            finalcursor.execute(finalquery, (maingraph.graph(),))
            finalquery = "UPDATE graph SET content = %s WHERE cid = 2"
            finalcursor.execute(finalquery, (maingraph.scores(),))
            db.commit()
            finalcursor.close()
            processed = {
                "uid": uid,
                "link": paper_link,
                "title": article_data["title"],
                "title": article_data["authors"],
                "title": article_data["affiliations"],
                "title": article_data["publication_date"],
                "title": article_data["journal_name"],
                "title": article_data["journal_volume"],
                "title": article_data["journal_pages"],
                "title": article_data["doi"],
                "score": score,
            }
            idcursor = db.cursor()
            idquery = "SELECT id FROM `graph-entries` WHERE title=%s"
            idcursor.execute(idquery, (article_data["title"],))
            pid = idcursor.fetchone()
            idcursor.close()
            qcursor = db.cursor()
            qquery = "INSERT INTO queries (id) VALUES %s"
            qcursor.execute(qquery, (pid,))
            db.commit()
            qcursor.close()
            return jsonify(processed), 200
    else:
        return jsonify({"error": "Paper not found"}), 404

@app.route('/graph')
def graph_display():
    return jsonify(maingraph.graph())

@app.route("/get-node/<node_title>")
def get_node(node_title):
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM `graph-entries` WHERE title = %s"
    cursor.execute(query, (node_title,))
    node_data = cursor.fetchone()
    cursor.close()
    
    if node_data:
        return jsonify(node_data), 200
    else:
        return jsonify({"error": "Node not found"}), 404
  
@app.route("/summary/<path:paper_link>")
def get_summary(paper_link):
    paper_link = urllib.parse.unquote(paper_link)
    cursor = db.cursor(dictionary=True)
    query = "SELECT id FROM `graph-entries` WHERE link = %s"
    cursor.execute(query, (paper_link,))
    eid = cursor.fetchone()
    eid = eid['id']
    cursor.close()
    
    if eid:
        cursor2 = db.cursor(dictionary=True)
        query = "SELECT summary FROM queries WHERE id = %s"
        cursor2.execute(query, (eid,))
        summary = cursor2.fetchone()
        cursor2.close()
        if summary:
            return summary['summary'], 200
        else:
            summary = Summary_gen(paper_link)
            cursor3 = db.cursor()
            query = """
                UPDATE queries
                SET summary = %s
                WHERE id = %s
            """
            cursor3.execute(query, (summary, eid))
            db.commit()
            cursor3.close()
            return summary, 201
    else:
        return "error: Paper not in Graph", 404
    
@app.route("/citation/<path:paper_link>")
def get_citation(paper_link):
    paper_link = urllib.parse.unquote(paper_link)
    query_type = request.args.get('style')
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM `graph-entries` WHERE link = %s"
    cursor.execute(query, (paper_link,))
    eid = cursor.fetchone()
    newid = eid['id']
    cursor.close()
    
    if newid:
        cursor2 = db.cursor(dictionary=True)
        query = "SELECT %s FROM queries WHERE id = %s"
        cursor2.execute(query, (query_type, newid))
        citation = cursor2.fetchone()
        cursor2.close()
        if citation:
            return citation[query_type], 200
        else:
            paper_attributes = {
                "title": eid['title'],
                "authors": eid['authors'],
                "affiliations": eid['affiliations'],
                "publication_date": eid['publication_date'],
                "journal_name": eid['journal_name'],
                "journal_volume": eid['journal_volume'],
                "journal_pages": eid['journal_pages'],
                "doi": eid['doi']        
            }
            citation = Citation_gen(query_type, paper_link, paper_attributes)
            cursor3 = db.cursor()
            query = """
                UPDATE queries
                SET %s = %s
                WHERE id = %s
            """
            cursor3.execute(query, (query_type, citation, newid))
            db.commit()
            cursor3.close()
            return citation, 201
    else:
        return "error: Paper not in Graph", 404


@app.route("/create-user", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        pfp = data.get("pfp")

        if not all([username, email, password]):
            return jsonify({"error": "Missing required fields"}), 400
        
        cursor = db.cursor()
        query = "INSERT INTO users (username, email, password, pfp) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (username, email, password, pfp))
        db.commit()
        cursor.close()
        return jsonify({"message": "User created successfully"}), 201

    except mysql.connector.Error as dberr:
        db.rollback() 
        return jsonify({"error": str(dberr)}), 500

    except Exception as generalerror:
        return jsonify({"error": str(generalerror)}), 500

@app.route("/update-user", methods=["PUT"])
def update_user():
    try:
        data = request.get_json()
        email = data.get("email")
        username = data.get("username")
        pfp = data.get("pfp")

        cursor = db.cursor()

        update_query = """
            UPDATE users
            SET username = %s, pfp = %s
            WHERE email = %s
        """
        cursor.execute(update_query, (username, pfp, email))
        db.commit()
        cursor.close()
        return jsonify({"message": "User updated successfully"}), 200

    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"error": str(err)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    #NEED TO ADD connections.close on exit
    app.run(debug=True)
    