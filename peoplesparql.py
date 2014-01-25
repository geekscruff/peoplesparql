__author__ = 'geekscruff'

from flask import Flask, render_template, request, session
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

#Show the home page as the root
@app.route('/')
def index():
    return render_template('index.html')

#Query page
@app.route('/query', methods=['GET', 'POST'])
def query():
    #destroy the existing query session on page load
    session.pop('q', None)
    #if the query button is clicked, replace it with the sparql query result
    #TODO error handling
    if request.method == 'POST':
        sparql = SPARQLWrapper("http://collection.britishmuseum.org/sparql")
        sparql.setQuery("""
        PREFIX crm: <http://erlangen-crm.org/current/>

        SELECT DISTINCT ?obj
        { ?obj crm:P102_has_title ?title } LIMIT 10
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        s = "<p>QUERY (example from British Museum sparql endpoint)</p><p>PREFIX crm: <http://erlangen-crm.org/current/><br /><br />SELECT DISTINCT ?obj<br />{ ?obj crm:P102_has_title ?title } LIMIT 10</p>"
        s += "<p>RESULTS</p>"

        for result in results["results"]["bindings"]:
            #only doing one
            s += "<p>" + result["obj"]["value"] + "</p>"
        s += "<p>FULL RESULT " + str(results) + "</p>"
        session['q'] = s
    return render_template('query.html')

# this is taken from the example code, see doco for generating a new key, need this for sessions
# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.debug = True
    app.run()
