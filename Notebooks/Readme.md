## Working with CLEVER

In this I have tried to create a dictionary out of CLEVER terminologies so it can be more easily managed.

## Working with RADLEX

In this I have tried to develop an algorithm which given a term tries to retrieve all instances of the keyword occourance. And for each hit, it tries to look into 3 levels below in the graph and tries to obtain the name and synonym.

To use this notebook, download the .xref (RDF / XML) file from http://bioportal.bioontology.org/ontologies/RADLEX

In this we initially load the data into a ConjunctiveGraph() and on this we run the SPARQL query to get all the terms.

On these terms we use a filter to get only the concepts we are intrested in, in this scenario "Lung"

Once we have all the terms we are intrested we look upto 3 levels below the current level to check for related terms and synonyms

Once we have all the data we convert them into Pandas and further create a list of all the words obtained so that it can be more easily managed.

In this I have tried to retrieve all the data for lung, if one is interested in getting data for terms, in the SPARQL code search for filter and replace lung with the word you want to retrieve data for.
