from lab6_search import Retriever, show_hits
records = [
    {"id":"printer:blank","device":"printer","text":"For blank printer pages: 1. Check ink level. 2. Run the printer cleaning utility. 3. Print a test page. Follow the device manual."},
    {"id":"scanner:blank","device":"scanner","text":"For a blank scanner image, check document placement and select the correct scanning source."}
]
show_hits(Retriever(records).search("blank pages", k=1, filters={"device":"printer"}))
