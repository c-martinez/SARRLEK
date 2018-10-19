# Notes on loading RadLex in virtuoso

Start by downloading the OWL file from http://bioportal.bioontology.org/ontologies/RADLEX

We assume you have [docker installed](https://docs.docker.com/install/) and working.

# Use virtuoso to load RDF data
First, start by creating a temporary directory where virtuoso db will be stored. This can be removed when you don't need virtuoso any more.

```
mkdir dbdir
```

We will now import the OWL file into virtuoso (assuming the OWL file is saved on the `$PWD/Data` directory):

```
docker run --rm \
    -v $PWD/dbdir:/var/lib/virtuoso-opensource-7 \
    -v $PWD/Data:/import:ro \
    joernhees/virtuoso import 'http://www.radlex.org/RID/'
```

Now we start virtuoso:
```
docker run --name sarrlek-virtuoso -d --rm \
        -v $PWD/dbdir:/var/lib/virtuoso-opensource-7 \
        -p 8890:8890 \
        -e "NumberOfBuffers=$((32*85000))" \
        joernhees/virtuoso
```

If everything goes as expected, virtuoso should be running on your computer and you should be able to see virtuoso SPARQL query editor by going to http://localhost:8890/sparql

You can run any query for testing. For instance, the following query for counting the number of meta class subtypes in RadLex

```
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX radlex: <http://www.radlex.org/RID/#>

SELECT ?mclass ?label ?name (COUNT(?subtype) as ?nsubs)
WHERE
{
  ?mclass rdf:type radlex:radlex_metaclass .
  ?mclass rdfs:label ?label .
  ?mclass radlex:Preferred_name ?name

  OPTIONAL {
    ?mclass ?Has_Subtype ?subtype
  }

}
GROUP BY ?mclass ?label ?name
ORDER BY DESC (?nsubs)
```
