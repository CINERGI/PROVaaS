// Global Variables to hold the graph.
var nodes = [];
var node_pos = {};
var links = [];
var selected = [];

// Configuration for the edge types, listing them, and defining their directionality.
var edge_defs = {
	"used":{"source":"prov:entity",
			"target":"prov:activity"},
	"wasGeneratedBy":{"source":"prov:activity",
					  "target":"prov:entity"},
	"wasDerivedFrom":{"source":"prov:usedEntity",
					  "target":"prov:generatedEntity"},
	"wasInformedBy":{"source":"prov:informant",
					 "target":"prov:informed"}
};

// SVG and Layout
var width = 600,
    height = 300,
    colors = d3.scale.category10();

var svg = d3.select("div#graph")
	.append("svg")
	.attr("width",width)
	.attr("height",height);

// Force-directed graph.  Because the layout is deterministic, this shouldn't
// affect the positions of and node, but it does make rendering the edges easier.
var force = d3.layout.force()
	.charge(-20)
	.linkDistance(200)
	.size([width,height]);

// URL/CGI parsing.  To load a specific JSON file in for visualization
// pass source=/path/to/file as a URL parameter.  Please study CORS for
// more information on client-side security restrictions, and loading
// data from other domains: 
// http://en.wikipedia.org/wiki/Cross-origin_resource_sharing
var query = {};
var qs = window.location.search.substr(1).split('&')
console.log("qs", qs);

qs.forEach(function (q, i, a) {
	var kv = q.split("=");
	k = kv[0];
	v = kv[1];
	console.log(k,v)
	query[k] = v
});

console.log("query: ",query);
var source = query.source;
source = source || "document.json"; // You can override the default data source HERE

// Retrieve the source data file
d3.json(source,function(d) {
	var startTime = new Date();
	console.log("data loaded:",d, startTime);	

	// Data parsing.  Because of the way JSON interacts with semantic namespaces,
	// this section is very sensitive to the exact keys and value data types in the data.
	// This is a very common limitation of JSON-based apps.  

	// We'll begin by parsing the two node types, activities and entities.
	var node_aliases = {};
	// First parse the activities 
	var group_count = 0;
	var uuid_groups = {};
	var activities = [];
	for (var a in d.activity) {
		d.activity[a]["raw"] = JSON.stringify(d.activity[a],null," ");
		d.activity[a]["id"] = a;
		d.activity[a]["type"] = "activity";
		var t = Date.parse(d.activity[a]["prov:startTime"]);
		console.log(t);
		d.activity[a]["timecode"] = t;
		d.activity[a]["group"] = group_count;
		d.activity[a]["incoming"] = [];
		d.activity[a]["outgoing"] = [];
		d.activity[a]["label"] = d.activity[a]["prov:type"]["$"];

		group_count = (group_count + 1) % 10;
		node_aliases[a] = a;
		activities.push(d.activity[a]);
	}
	// sort activities by startTime
	activities.sort(function(a,b){
		if (a.timecode < b.timecode) return -1;
		if (a.timecode > b.timecode) return 1;
		return 0;
	})
	console.log("activities:", activities);

	// Then parse the entities.
	var entities = [];
	var seen_entities = {};

	for (var e in d.entity) {

		d.entity[e]["raw"] = JSON.stringify(d.entity[e],null," ");
		d.entity[e]["id"] = e;
		d.entity[e]["type"] = "entity";
		var uuid = d.entity[e]["prov:UUID"]["$"];
		var created = Date.parse(d.entity[e]["prov:creationTime"]["$"]);
		var created_date = d.entity[e]["prov:creationTime"]["$"];
		var version = d.entity[e]["prov:version"]["$"];
		d.entity[e].uuid = uuid;
		d.entity[e].created_date = created_date;
		d.entity[e].version = version;
		var uniqueid = uuid + "@" + created;
		
		var group = uuid_groups[uuid];
		if (group === undefined) {
			group = group_count;
			uuid_groups[uuid] = group;
			group_count = (group_count + 1) % 10;
		}
		d.entity[e]["group"] = group;
		d.entity[e]["incoming"] = [];
		d.entity[e]["outgoing"] = [];		

//		var label_comp = d.entity[e]["foundry:label"];
//		var label = label_comp[label_comp.length - 1];
//		d.entity[e]["label"] = label.substring(0,label.length - 1);
		var label_comp = uuid.split("/");
		d.entity[e]["label"] = label_comp[label_comp.length - 1];

		// check if we've seen this entity before, 
		if (seen_entities[uniqueid] === undefined) {
			// if not, add it and log it's id
			entities.push(d.entity[e]);
			seen_entities[uniqueid] = e;
			node_aliases[e] = e;
		} else {
			//otherwise, just log this entity as an alias
			node_aliases[e] = seen_entities[uniqueid];
		}
	}
	
	nodes =  activities.concat(entities);
	console.log("nodes:", nodes)

	var least_time = undefined;

	// After the nodes are parsed, parse the edges, based on the definitions in the
	// edge_defs configuration object (at the top of this file)
    function parse_edges(data) {
  	// loop over each different defined edge type
      for (var e_type in edge_defs) {
  		var t_edges = d[e_type];
//  		console.log(e_type);
  		if (t_edges) {
			for (var e in t_edges) {
				var edge = t_edges[e];
				// get the source and target node id's
				var source = edge[edge_defs[e_type]["source"]];
				var target = edge[edge_defs[e_type]["target"]];
				edge["label"] = e_type;
				var inferred = edge["foundry:inferred"] || false;
				// should check here to make sure they exist.
//				console.log(edge, "source", source, "target",target);

				// check if these are aliased id's
				// should note in the log.
				if (source === undefined  || node_aliases[source] === undefined) {
					console.log("FAILURE: UNRECOGNIZED SOURCE", source, "IN EDGE", edge);
					return 1;
				}
				source = node_aliases[source];
				if (target === undefined || node_aliases[target] === undefined) {
					console.log("FAILURE: UNRECOGNIZED TARGET", target, "IN", e_type, "EDGE", edge);
					return 1;
				}
				target = node_aliases[target];
				// loop over the nodes to resolve the id's to node objects
				var source_node = undefined;
				var target_node = undefined;
				for (var i = 0; i < nodes.length; i++) {
					if (nodes[i].id == source) { 
						source_node = nodes[i];
					}
					else if (nodes[i].id == target) { 
						target_node = nodes[i]
					}
				}
				if (source_node === undefined) {
					console.log("FAILURE; COULD NOT RESOLVE SOURCE", source);
					return 1;
				}
				if (target_node === undefined) {
					console.log("FAILURE; COULD NOT RESOLVE TARGET", target);
					return 1;
				}

				var time = target_node["prov:startTime"] || source_node["prov:endTime"] || source_node["foundry:creationTime"]["$"];
				var seconds = Date.parse(time) * .000001;

				if (least_time === undefined) {
					least_time = seconds;
				}
				if (seconds < least_time) {
					least_time = seconds;
				}

				links.push( {id:e,source:source_node, target: target_node, type:e_type, label:e_type, time:seconds, inferred:inferred} );
				source_node.outgoing.push(target_node);
				target_node.incoming.push(source_node);								
			}
  		}
  	  }
  	  return 0;
    }

    // should check results and halt if error
   	if (parse_edges(d) > 0) return;

    for (var l in links) {
    	console.log("link!",l,links[l],links[l].time, least_time)
    	links[l].elapsedTime = links[l].time - least_time;
    }

	console.log("links", links);

	// Now that we have nodes and edges, we can analyze the graph.

	// First, we need to find our roots and our leaves.
	// We do require that the graph have a single root, which also requires
	// that a non-trivial graph be fully connected.  We do not require a true tree,
	// but cycles will result in abnormal behavior.

	var root = undefined;
	var leaf = undefined;
	var bad_root = false;
	for (var ni in nodes) {
		console.log(nodes[ni].id, "in:",nodes[ni].incoming.length, "out:",nodes[ni].outgoing.length );		
		if (nodes[ni].incoming.length == 0) {
			console.log("ROOT FOUND", nodes[ni])
			if (root === undefined) {
				root = nodes[ni];
			} else {
				console.log("FAILURE: MULTIPLE ROOTS DETECTED");
				bad_root = true;
			}
		}
		if (nodes[ni].outgoing.length == 0) {
			leaf = nodes[ni];
		}
	}
	if (root === undefined) {
		console.log("FAILURE: NO ROOT FOUND");
		bad_root = true;
//		return 2;
	}

	console.log("ROOT", root);

	// Now walk the graph, starting from the root, in a recursive DFS.
	// Annotate each node with "depth" and "breadth" to fix its
	// horizontal and vertical position, respectively.

	// For each child in a node, we layout each of it's children in sequence by recursion.
	// Since each child may be a subtree, we return the maximum depth and maximum breadth of that subtree.
	// We use this to bound the layout of each subsequent child so that it cannot overlap
	// onto its preceding siblings.

	// This algorithm is very conservative, and doesn't use geometric space very efficiently
	// for sparse or unbalanced trees.

	// Tree layout is closely related to some NP-complete problems, so a greedy,
	// conservative, linear-time algorithm is an adequate compromise.

	function annotate_tree(node,depth,breadth) {
		if (node.depth !== undefined) {
			return undefined;
		} else {
			node.depth = depth + 1;
			node.breadth = breadth;
		}
		console.log("WALKING", node, node.depth);
		var max_depth = node.depth;
		var max_breadth = breadth;
		var res = undefined;
		var b = breadth;
		for (var ni in node.outgoing) {
			var n = node.outgoing[ni];
			res = annotate_tree(n, node.depth,b);
			if (res === undefined) {
				continue;
			}
			max_depth = (res.max_depth > max_depth) ? res.max_depth : max_depth;
			max_breadth = (res.max_breadth > max_breadth) ? res.max_breadth : max_breadth;
			b = max_breadth + 1;
		}
		return {"max_depth":max_depth, "max_breadth":max_breadth };
	}

	// with the logical tree positions created by annotate_tree, we can calculate
	// the geometric positions of each node in euclidean space.
	// Edges are handled automatically by the force directed graph.

	function layout_nodes(nodes, max_depth, max_breadth, width, height) {
		var padding = width * 0.05;
		var center = height / 2.0;
		var w_space = width - padding * 2;
		var w_spacing = w_space / max_depth;
		var hpadding = 30;
		var h_space = height - hpadding * 2;		
		var h_spacing = h_space / max_breadth;
		console.log("max_breadth",max_breadth,"h_space",h_space,"h_spacing",h_spacing);
		var max_height = height * 0.9;

		if (h_spacing > max_height) {
		  h_spacing = max_height;
		}

//		var offset = spacing * Math.sqrt(3.0) / 2.0;
		console.log(padding, center, w_spacing,h_spacing);

		for (var ni in nodes) {
			var n = nodes[ni];
			console.log(n);
			n.x = padding + (n.depth * w_spacing);
	  		n.y = hpadding + (n.breadth * h_spacing);
			n.fixed = true;
			console.log("node ",ni, n.x,n.y);
		}
	}

	var res = annotate_tree(root,-1,0);
	console.log(res );
	layout_nodes(nodes,res.max_depth,res.max_breadth,width,height);

	// links.sort(function(a,b) {
	// 	if (a.source.depth < b.source.depth) return 1;
	// 	if (a.source.depth > b.source.depth) return -1;
	// 	return 0;
	// });
	
	// var desc = "";
	// var prev_entity = "";
	// var prev_activity = "";
	// for (var li = 0; li < links.length; li++) {
	// 	var l = links[li];
	// 	if (l.type == "used") {
	// 		console.log("used");
	// 		prev_entity = l.source;
	// 	} else if (l.type == "generatedBy") {
	// 		var activity = l.source;
	// 		var this_entity = l.target;
	// 		if (activity.type == "ingestion") {
	// 			desc += prev_entity["foundry:label"] + " was ingested from " + prev_entity["foundry:sourceId"]["$"] + " into " + this_entity["foundry:label"] + ".  ";
	// 		} else if (prev_entity["foundry:UUID"] == this_entity["foundry:UUID"]) {
	// 			desc += prev_entity["foundry:label"] + " was revised by activity " + activity.type + ".  ";
	// 		} else {
	// 			desc += prev_entity["foundry:label"] + " was transformed by activity " + activity.type + " into " + this_entity["foundry:label"] + ".  ";
	// 		}
	// 	}
	// }
	// console.log("desc", desc)
	// d3.select("#desc-body").text(desc);
	
	force.nodes(nodes).links(links).start();

	// a few obscure SVG pieces.
	
	svg.append('svg:defs').append('svg:marker')
		.attr('id', 'end-arrow')
		.attr('viewBox', '0 -5 10 10')
		.attr('refX', 6)
		.attr('markerWidth', 6)
		.attr('markerHeight', 6)
		.attr('orient', 'auto')
	  .append('svg:path')
		.attr('d', 'M0,-5L10,0L0,5')
		.attr('fill', '#000');
		
	var gradient = svg.select("defs").append("radialGradient")
		.attr("id","selected-gradient")
	gradient.append("stop").attr("offset","65%").attr("stop-color","#F00");
	gradient.append("stop").attr("offset","100%").attr("stop-color","#FFF");

	// Handle clicking on edges.
	function detail_display_link(d) {
		d3.select("#detail-header").text(d.type);
		var table = d3.select("#detail");
		table.selectAll("*").remove();		
		svg.selectAll("#selection").remove();
	}

	var selected = undefined;

	// Test to see if nodes are "alike" for the purpose of multiple selection.
	// Currently a placeholder.
	function like_nodes(a,b) {
		if ( (a.label == "Bob.txt" && b.label == "Anna.txt" ) || (a.label == "Bob_kw.txt" && b.label == "Anna_kw.txt") ) {
			return true;
		}
		return false;
	}


	// Handles clicking on nodes
	function detail_display(d) {

		console.log("DETAIL DISPLAY", d.label,d.id);
		// check for multiple selection.
		var comp_node = undefined;
		var show_comp = false;
		if (selected) {
			comp_node = selected;
			if (like_nodes(d,comp_node)) {
				show_comp = true;
			}
		}

		d3.select("#detail-header").text(d.label);
		var table = d3.select("#detail");
		table.selectAll("*").remove();

		// subroutine to display the right-hand detail table.
		function detail_display_table(d) {

			var attribs = ["uuid","created_date","time","elapsedTime","version","inferred","prov:startTime","prov:endTime","foundry:how","foundry:label","foundry:version"];
			var header_row = table.append("tr");
			var header = header_row.append("th");
			header.attr("colspan",2);			
			var header_text = header.append("h4");
			header_text.attr("class","detail-header");

			header_text.text(d.label);
			for (var a in attribs) {
				var attrib = attribs[a];
				var key = attrib.split(":")[1];
				if (key === undefined) key = attrib;
				if (d[attrib] !== undefined) {
					var row = table.append("tr");
					row.append("td").text(key);
					row.append("td").text(d[attrib]);
				}
			}
		}
		// show the previous and current node in multiple selection.
		if (show_comp) {
			detail_display_table(comp_node);
		}
		detail_display_table(d);

		// move the red "current selection" gradient to the newly selected node.
		svg.selectAll("#selection").remove();

		if (d.type == "entity" || d.type == "activity"){
			if (show_comp) {
				svg.insert("circle",":first-child").attr("r",21).style("fill","url(#selected-gradient)").attr("cx",comp_node.x).attr("cy",comp_node.y).attr("id","selection");
			}
			svg.insert("circle",":first-child").attr("r",21).style("fill","url(#selected-gradient)").attr("cx",d.x).attr("cy",d.y).attr("id","selection");
			selected = d;


			// walk the graph to "highlight" the path from the root to the selected node.
			var visited = [];
			var to_visit = [d];

			// essential utility function.  Why doesn't JS have this?
			function array_contains(the_array,obj) {
				for (var l in the_array) {
					if (the_array[l].id === obj.id) return true;
				}
				return false;
			}

			// clear any prior highlighting.
			console.log("CLEARING");
			for (var l = 0; l < links.length; l++) {
				links[l]["highlight"] = false;
			}

			// append nodes to the to_visit array as we encounter them, 
			// and move them to visited after we enter them.  Do not add a node to 
			// to_visit if is is already visited.

			// Skips edges with inferred = true set in the data.
			while(to_visit.length > 0) {
				console.log(to_visit.length, "to_visit", visited.length,"visited");
				var current = to_visit[0];
				console.log("current",current);
				for (var l = 0; l < links.length; l++) {
					if (links[l]["target"].id == current.id) {
						if (!(links[l].inferred == true) ) {
							console.log("MATCH", links[l],links[l].source.label,links[l].target.label);
							links[l]["highlight"] = true;
							if (!(array_contains(visited,links[l]["source"]) || array_contains(to_visit,links[l]["source"]) ) ){
								console.log("traversing");
								to_visit.push(links[l]["source"]);								
							}
						}
						else {
							console.log("BAD LINK",links[l],links[l].id)
						}
					} 
				}

				visited.push(to_visit.shift());
				console.log("to_visit",to_visit,"visited",visited);
			}

			console.log("incoming", d.incoming);
			var link_updates = svg.selectAll(".link").data(links).style("stroke",function(d) {				
				if (d.highlight) {
					return d3.rgb("red");
				} else {
					return d3.rgb("black");
				}
			});
			console.log("updated:", link_updates);
		}
		else {
			selected = undefined;
		}
	}
	
	var node_updates = svg.selectAll(".node").data(nodes);
	var node_enter = node_updates.enter().append("g").attr("class","node").attr("transform", function(d){return "translate("+d.x+","+d.y+")";});

	// define rendering for nodes
	var circles = node_enter.filter(function(d,i) {return d.type == "activity"}).append("circle").attr("r", 15)
		.style("fill", function(d) { 
			if (d.label.match("q")) {
				return d3.rgb("lightblue");
			} else {
				return d3.rgb("lightgreen");
			}
		})
		.on("click", detail_display);
	var squares = node_enter.filter(function(d,i) {return d.type=="entity"}).append("rect").attr("width",26).attr("height",26)
		.attr("transform","translate(-13,-13)")
		.style("fill", function(d) { 
			if (d.uuid.match("t")) {
				return d3.rgb("lightblue");
			} else {
				return d3.rgb("lightgreen");
			}
		})
		.on("click", detail_display);

	// define rendering for edges.
	var link_updates = svg.selectAll(".link").data(links)
		.enter().append("path").attr("class","link")
		.attr("stroke-dasharray",function(d) {
			if (d.inferred) return "5,5";
			return "";
		})
		.attr("stroke",function(d) {
			if (d.highlight) {
				return d3.rgb("red");
			} else {
				return d3.rgb("black");
			}
		})
		.on("click", detail_display);

	// define rendering for text labels over nodes.		
	var labels = node_enter.append("text").text(function (d) { return d.label;})
		.attr("dy",5).attr("text-anchor","middle").attr("font-weight","100").attr("letter-spacing","1px")
		.attr("pointer-events","none");

	// Force directed graph update functions.  Keeps edges from overlapping circle radius.
	force.on("tick", function() {
		link_updates.attr("d",function(d){
			var deltaX = d.target.x - d.source.x,
				deltaY = d.target.y - d.source.y,
				dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY),
				normX = deltaX / dist,
				normY = deltaY / dist,
				sourcePadding = 15,
				targetPadding = 15,
				sourceX = d.source.x + (sourcePadding * normX),
				sourceY = d.source.y + (sourcePadding * normY),
				targetX = d.target.x - (targetPadding * normX),
				targetY = d.target.y - (targetPadding * normY);
			return 'M' + sourceX + ',' + sourceY + 'L' + targetX + ',' + targetY;
		});
		
		node_updates.attr("transform", function(d){
			return "translate("+d.x+","+d.y+")";
		});
	});

	// Done.  Select the final node by default.
	console.log("selecting last node", nodes[nodes.length - 1] );
	// Print timing data to log.
	var endTime = new Date();
	detail_display(nodes[nodes.length - 1]);
	console.log(endTime);
	console.log("elapsed", endTime - startTime);

});
