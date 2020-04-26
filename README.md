# search-summary
A simple service that allows students to search through coursebooks summaries which would make picking and buying a coursebook, a much better experience for students.

End:Task 1
1. Haven't done the stemming yet. That's one improvement I would like to do to improve the search results.
2. Would move all the configuration related settings to a settings file.
3. TF-IDF is a very simple algorithm to rank results also not the best one out there.Would want to explore more algorithm options to improve search results.

Challenges:
1. Implementing tf-idf was a bit challenging as I didn't have the clear idea of algorithm.
2. Implementing phrase search was a bit challenging as I needed to check for the position as well as existence of the terms searched.



End:Task 2
Improvement:
1. Have tested the search engine manually.Would want to add unit tests for efficient testing.
2. Would use multi-threading for calling author API. Haven't used it right now due to lack of time.
3. Logging is not enabled in django app.Would in fact integrate this with Sentry for bug tracking.

Challenges:
1. Creating a server on top the core functionality was relatively easy as all the core development was already done is Task1.
2. No major challenges faced in this task.