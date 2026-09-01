// Example knowledge-graph queries per team (Neo4j Cypher).
// Adapt the labels if you load the graph into a different store.

// --- Team 1 (Diagnostic): which fault codes exist for a seat's components?
MATCH (s:Seat {node_id:'SEAT:D-AXFB-1K'})-[:HAS_COMPONENT]->(p:Part)<-[:PROBABLE_CAUSE]-(f:FaultCode)
RETURN s.seat_id, p.part_number, f.code, f.label;

// --- Team 2 (NFF evaluator): historic NFF rate for a fault code
MATCH (w:WorkOrder)-[:REPORTED_FAULT]->(f:FaultCode {code:'F-25-2140'})
RETURN f.code,
       count(w) AS total,
       sum(CASE WHEN w.outcome='NFF' THEN 1 ELSE 0 END) AS nff,
       toFloat(sum(CASE WHEN w.outcome='NFF' THEN 1 ELSE 0 END))/count(w) AS nff_rate;

// --- Team 2: what did previous work orders on this exact seat find?
MATCH (s:Seat {node_id:'SEAT:D-AXFB-1K'})-[:HAD_WORK_ORDER]->(w:WorkOrder)-[:REPORTED_FAULT]->(f:FaultCode)
RETURN w.work_order_id, w.opened_at, f.code, w.action, w.outcome, w.cost_eur
ORDER BY w.opened_at DESC;

// --- Team 3 (Planner): which parts and procedure does this fault need,
//     and which stations can do the work?
MATCH (f:FaultCode {code:'F-25-2140'})-[:RESOLVED_BY]->(t:Procedure)-[:CONSUMES]->(p:Part)
RETURN t.task_id, collect(p.part_number) AS parts;

MATCH (st:Station)-[:SERVICED_BY]->(o:Organisation)
WHERE st.line_maintenance = true
RETURN st.iata, st.name, o.name;

// --- Team 4 (Execution): documents to show the technician
MATCH (f:FaultCode {code:'F-25-2140'})-[:ISOLATED_BY|RESOLVED_BY]->(d)
RETURN f.code, labels(d), coalesce(d.doc_id, d.task_id) AS ref;

// --- Team 5 (Improvement): cost by outcome, per fault code
MATCH (w:WorkOrder)-[:REPORTED_FAULT]->(f:FaultCode)
RETURN f.code, w.outcome, count(*) AS n, sum(w.cost_eur) AS cost_eur
ORDER BY cost_eur DESC;

// --- Team 5: write the new outcome back into the graph
MERGE (w:Entity:WorkOrder {node_id:'WO:WO-90001'})
  SET w.work_order_id='WO-90001', w.outcome='CONFIRMED_FAULT', w.cost_eur=980
WITH w
MATCH (s:Seat {node_id:'SEAT:D-AXFB-1K'}), (f:FaultCode {code:'F-25-2140'})
MERGE (s)-[:HAD_WORK_ORDER]->(w)
MERGE (w)-[:REPORTED_FAULT]->(f);
