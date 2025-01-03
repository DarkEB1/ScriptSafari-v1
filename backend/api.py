import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from article_info_scrapers import *
from reputational_score import *
import ast
from graph import *
from citation_generator import *
from summary_generator import *
from author_info_scraper import *
import urllib

"""
Initialization function
- Connect api to database via ngrok (or other)
- Initialize graph with info from database
"""
app = Flask(__name__)
CORS(app)
global db
db = mysql.connector.connect(
    host="2.tcp.eu.ngrok.io",  # ngrok host
    port= 17711,                # ngrok port
    user="root",               
    password="",               
    database="scriptsafariv1"    
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
cursor2.close()
print(graph_data[0], scores_data[0])
gra = ast.literal_eval(graph_data[0])
sc = ast.literal_eval(scores_data[0])
global maingraph
maingraph = Graph(graph=gra, scores=sc)
print(maingraph)
if db.is_connected():
    print("connected successfuly")

"""
Root endpoint, retun app name
"""
@app.route("/")
def home():
    return 'ScriptSafari-API-v1'

"""
Function to retreive paper details from link by calling scraping bots, then generates reputational score and write to databse
Takes paper link as input
"""
@app.route('/add-paper/<path:paper_link>', methods=["POST", "GET"])
def add_paper(paper_link):
    user = request.args.get('email')
    print(user, paper_link)
    paper_link = urllib.parse.unquote(paper_link)
    article_data = scrape(paper_link)
    print(article_data)

    if article_data["title"]:
        try:
            db.start_transaction()
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
                    graphcursor.execute(query, (article_data["journal_name"], like_authors_pattern, like_affiliations_pattern))
                    connected_titles = [row[0] for row in graphcursor.fetchall()]
                except mysql.connector.Error as err:
                    print(f"Error: {err}")
                    connected_titles = []
                print(connected_titles)
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

                cursor2 = db.cursor(dictionary=True)
                query = """INSERT INTO `graph-entries` 
                           (uid, link, title, authors, affiliations, publication_date, journal_name, journal_volume, journal_pages, doi) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor2.execute(query, (uid, paper_link, article_data["title"], 
                                        str(article_data["authors"]), str(article_data["affiliations"]),
                                        article_data["publication_date"], article_data["journal_name"], 
                                        article_data["journal_volume"], article_data["journal_pages"], 
                                        article_data["doi"]))
                print(maingraph.graph())
                score = defaultscore(article_data, maingraph, db)  # written to database within that program
                print('Sc'+str(score))
                finalcursor = db.cursor()
                print("G"+str(maingraph.graph()))
                print("S"+str(maingraph.scores()))
                finalquery = "UPDATE graph SET content = %s WHERE cid = 1"
                data = str(maingraph.graph())
                finalcursor.execute(finalquery, (data,))
                finalquery = "UPDATE graph SET content = %s WHERE cid = 2"
                data2 = str(maingraph.scores())
                finalcursor.execute(finalquery, (data2,))
                finalcursor.close()
                processed = {
                    "uid": uid,
                    "link": paper_link,
                    "title": article_data["title"],
                    "authors": article_data["authors"],
                    "affiliations": article_data["affiliations"],
                    "publication_date": article_data["publication_date"],
                    "journal": article_data["journal_name"],
                    "journal_volume": article_data["journal_volume"],
                    "journal_pages": article_data["journal_pages"],
                    "doi": article_data["doi"],
                    "score": score,
                }
                idcursor = db.cursor()
                idquery = "SELECT id FROM `graph-entries` WHERE title=%s"
                idcursor.execute(idquery, (article_data["title"],))
                pid = idcursor.fetchone()
                idcursor.close()
                qcursor = db.cursor()
                qquery = "INSERT INTO queries (id) VALUES (%s)"
                qcursor.execute(qquery, (pid[0],))
                db.commit()
                qcursor.close()
                db.commit()

                return jsonify(processed), 200

        except Exception as e:
            db.rollback()
            print(f"Transaction failed: {e}")
            return jsonify({"error": "An error occurred while processing the paper"}), 500

        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception as e:
                print(e)
            if 'graphcursor' in locals():
                graphcursor.close()
            if 'ucursor' in locals():
                ucursor.close()
            if 'cursor2' in locals():
                cursor2.close()
            if 'finalcursor' in locals():
                finalcursor.close()
            if 'idcursor' in locals():
                idcursor.close()
            if 'qcursor' in locals():
                qcursor.close()
    else:
        return jsonify({"error": "Paper not found"}), 404

"""
Returns graph content, connections and score
"""
@app.route('/graph')
def graph_display():
    cursor = db.cursor(dictionary=True)
    query = "SELECT content FROM graph WHERE cid = 1"
    cursor.execute(query)
    graph_data = cursor.fetchone()
    graph_data = graph_data["content"]
    cursor.close()
    cursor2 = db.cursor(dictionary=True)
    query2 = "SELECT content FROM graph WHERE cid = 2"
    cursor2.execute(query2)
    scores = cursor2.fetchone()
    scores = scores["content"]
    cursor2.close()
    return jsonify({"graph": graph_data, "scores": scores})

"""
Retrieve node information from graph, return this as a json object
"""
@app.route("/get-node/<node_title>")
def get_node(node_title):
    try:
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM `graph-entries` WHERE title = %s"
        cursor.execute(query, (node_title,))
        node_data = cursor.fetchone()
        cursor.close()
        
        if node_data:
            return jsonify(node_data), 200
        else:
            return jsonify({"error": "Node not found"}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred while processing the paper"}), 500

"""
Retrieve profile info for currently logged user and return as a json object
"""
@app.route("/profile/<user>")
def profile(user):
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (user,))
    details = cursor.fetchone()
    cursor.close()
    if details:
        return jsonify(details), 200
    else:
        return jsonify({"error": "user not found"}), 404

"""
Return graph queries information for given user, as a json object
"""
@app.route("/entries/<uid>")
def entries(uid):
    cursor = db.cursor(dictionary=True)
    query = "SELECT title FROM `graph-entries` WHERE uid = %s"
    cursor.execute(query, (uid,))
    details = cursor.fetchone()
    cursor.close()
    if details:
        return jsonify(details), 200
    else:
        return jsonify({"error": "user not found"}), 404

"""
Call summary function for passed link, return value and write to queries database under the id of this request
If not in graph, ask user to add paper before requesting summary
"""
@app.route("/summary/<path:paper_link>")
def get_summary(paper_link):
    paper_link = urllib.parse.unquote(paper_link)
    cursor = db.cursor(dictionary=True)
    query = "SELECT id FROM `graph-entries` WHERE link = %s"
    cursor.execute(query, (paper_link,))
    eid = cursor.fetchone()
    if eid['id']:
        eid = eid['id']
    else:
        eid = None
    cursor.close()
    
    if eid:
        cursor2 = db.cursor(dictionary=True)
        query = "SELECT summary FROM queries WHERE id = %s"
        cursor2.execute(query, (eid,))
        summary = cursor2.fetchone()
        cursor2.close()
        if summary["summary"] != None:

            return summary['summary'], 200
        else:
            summaryobj = Summary_gen(paper_link)
            summary = summaryobj.fetch_sum()
            print(summary)
            cursor3 = db.cursor()
            query = "UPDATE queries SET summary = %s WHERE id = %s"
            cursor3.execute(query, (summary, eid))
            db.commit()
            cursor3.close()
            return summary, 201
    else:
        return "error: Paper not in Graph", 404
    
"""
Call citation function on passed link, return value and write to queries database under the id of this request
If not in graph, ask user to add paper before requesting citation
"""
@app.route("/citation/<path:paper_link>")
def get_citation(paper_link):
    paper_link = urllib.parse.unquote(paper_link)
    print(paper_link)
    query_type = request.args.get('style')
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM `graph-entries` WHERE link = %s"
    cursor.execute(query, (paper_link,))
    eid = cursor.fetchone()
    print(eid)
    if eid:
        newid = eid["id"]
    cursor.close()
    
    print(newid)
    if newid:
        cursor2 = db.cursor(dictionary=True)
        query = "SELECT * FROM queries WHERE id = %s"
        cursor2.execute(query, (newid,))
        citation = cursor2.fetchone()
        cursor2.close()
        print(citation)
        if citation[query_type] != None:
            return citation[query_type], 200
        else:
            author = ast.literal_eval(eid['authors'])
            aff = ast.literal_eval(eid['affiliations'])
            if aff:
                aff = aff[0]
            else:
                aff = ' '
            if author:
                author = author[0]
            else:
                author = ' '
            paper_attributes = {
                "title": eid['title'],
                "author": author,
                "affiliations": aff,
                "date": eid['publication_date'],
                "journal": eid['journal_name'],
                "issue": eid['journal_volume'],
                "pages": eid['journal_pages'],
                "doi": eid['doi']        
            }
            citationobj = Citation_gen(query_type, paper_link, paper_attributes)
            citation = citationobj.generate_citation()
            print(citation)
            cursor3 = db.cursor()
            query = f"UPDATE queries SET {query_type} = %s WHERE id = %s"
            cursor3.execute(query, (citation, newid))
            db.commit()
            cursor3.close()
            return citation, 201
    else:
        return "error: Paper not in Graph", 404

"""
Create user profile in database if not already written, takes json object in request as user details
"""
@app.route("/create-user", methods=["OPTIONS", "POST"])
def create_user():
    if request.method == "OPTIONS":
        print("OPTION SENT")
        return jsonify({"status": "OK"}), 200
    else:
        try:
            data = request.get_json()
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            pfp = data.get("pfp")

            if not all([username, email, password]):
                return jsonify({"error": "Missing required fields"}), 400

            cursor = db.cursor()

            # Check if the email already exists in the database
            check_query = "SELECT uid FROM users WHERE email = %s"
            cursor.execute(check_query, (email,))
            existing_user = cursor.fetchone()
            print("Existing user:", existing_user)

            if existing_user:
                print("Email already exists")
                cursor.close()
                return jsonify({"error": "Email already exists"}), 409

            # Insert the new user if the email is not found
            print("Inserting new user")
            insert_query = "INSERT INTO users (username, email, password, pfp) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (username, email, password, pfp))
            db.commit()
            cursor.close()
            return jsonify({"message": "User created successfully"}), 201

        except mysql.connector.Error as dberr:
            db.rollback()
            print(f"MySQL Error: {str(dberr)}") 
            return jsonify({"error": str(dberr)}), 500

        except Exception as generalerror:
            print(f"General Error: {str(generalerror)}")  
            return jsonify({"error": str(generalerror)}), 500

"""
If user already in database as above, call the update function to rewrite database fields and update them in the table based on whether the user has modified their creds
"""
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
    