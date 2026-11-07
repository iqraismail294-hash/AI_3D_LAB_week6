from lab6_search import Retriever, show_hits
records = [
    {"id":"remote:staff","audience":"employee","text":"Employees may request remote work with manager approval."},
    {"id":"remote:contractor","audience":"contractor","text":"Contractors may work remotely only when the signed contract explicitly permits remote work."}
]
show_hits(Retriever(records).search("remote work", k=1, filters={"audience":"contractor"}))
