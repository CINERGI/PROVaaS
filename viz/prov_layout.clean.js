var nodes = [];
var node_pos = {};
var links = [];

var edge_defs = {
	"used":{"source":"prov:entity",
			"target":"prov:activity",},
	"wasGeneratedBy":{"source":"prov:activity",
					  "target":"prov:entity",},
	"wasDerivedFrom":{"source":"prov:usedEntity",
					  "target":"prov:generatedEntity",},
	"wasInformedBy":{"source":"prov:informant",
					 "target":"prov:informed",},
};

var width = 400,
    height = 200,
    colors = d3.scale.category10();

var svg = d3.select("div#graph")
	.append("svg")
	.attr("width",width)
	.attr("height",height);	

var force = d3.layout.force()
	.charge(-20)
	.linkDistance(120)
	.size([width,height]);

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
var source = query.source
source = source || "document.json";

d3.json(source,function(d) {
	console.log("data loaded:",d);	

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
		d.activity[a]["timecode"] = t;
		d.activity[a]["group"] = group_count;
		d.activity[a]["incoming"] = [];
		d.activity[a]["outgoing"] = [];		
		d.activity[a]["label"] = d.activity[a]["prov:type"]["$"];

		group_count = (group_count + 1) % 10;
		node_aliases[a] = a;
		activities.push(d.activity[a]);
	}
	activities.sort(function(a,b){
		if (a.timecode < b.timecode) return -1;
		if (a.timecode > b.timecode) return 1;
		return 0;
	})
	console.log("activities:", activities);

	// Then the entities
	var entities = [];
	var seen_entities = {};

	for (var e in d.entity) {

		d.entity[e]["raw"] = JSON.stringify(d.entity[e],null," ");
		d.entity[e]["id"] = e;
		d.entity[e]["type"] = "entity";
		var uuid = d.entity[e]["foundry:UUID"];
		var created = d.entity[e]["foundry:creationTime"];
		var uniqueid = uuid + "@" + created;
		
		var group = uuid_groups[uuid];
		if (group == undefined) {
			group = group_count;
			uuid_groups[uuid] = group;
			group_count = (group_count + 1) % 10;
		}
		d.entity[e]["group"] = group;
		d.entity[e]["incoming"] = [];
		d.entity[e]["outgoing"] = [];		
		
		var label_comp = d.entity[e]["foundry:label"].split("/");
		var label = label_comp[label_comp.length - 1];
		d.entity[e]["label"] = label.substring(0,label.length - 1);
		
		// check if we've seen this entity before, 
		if (seen_entities[uniqueid] == undefined) {
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
				// should check here to make sure they exist.
//				console.log(edge, "source", source, "target",target);

				// check if these are aliased id's
				// should note in the log.
				if (source == undefined  || node_aliases[source] == undefined) {
					console.log("FAILURE: UNRECOGNIZED SOURCE", source, "IN EDGE", edge);
					return 1;
				}
				source = node_aliases[source];
				if (target == undefined || node_aliases[target] == undefined) {
					console.log("FAILURE: UNRECOGNIZED TARGET", target, "IN", e_type, "EDGE", edge);
					return 1;
				}
				target = node_aliases[target];
				if (target == undefined) {

				}
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
				if (source_node == undefined) {
					console.log("FAILURE; COULD NOT RESOLVE SOURCE", source);
					return 1;
				}
				if (target_node == undefined) {
					console.log("FAILURE; COULD NOT RESOLVE TARGET", target);
					return 1;
				}
				links.push( {source:source_node, target: target_node, type:e_type} );
				source_node.outgoing.push(target_node);
				target_node.incoming.push(source_node);								
			}
  		}
  	  }
  	  return 0;
    }

    // should check results and halt if error
   	if (parse_edges(d) > 0) return;

	console.log("links", links);

	var root = undefined;
	var leaf = undefined;
	for (var ni in nodes) {
		console.log(nodes[ni].id, "in:",nodes[ni].incoming.length, "out:",nodes[ni].outgoing.length );		
		if (nodes[ni].outgoing.length == 0) {
				console.log("ROOT FOUND", nodes[ni])
			if (root == undefined) {
				root = nodes[ni];
			} else {
				console.log("FAILURE: MULTIPLE ROOTS DETECTED");
				return 2;
			}
		}
		if (nodes[ni].incoming.length == 0) {
			leaf = nodes[ni];

		}
	}
	if (root == undefined) {
		console.log("FAILURE: NO ROOT FOUND");
		return 2;
	}

	console.log("ROOT", root);

	function annotate_tree(node,depth) {
		if (node.depth != undefined) {
			return node.depth;
		} else {
			if (node.type == "entity") {
				node.depth = Math.floor(depth + 1.0);
			} else {
				node.depth = depth + 0.5;
			}
		}
		console.log("WALKING", node, node.depth);
		var max = node.depth;
		for (var ni in node.incoming) {
			var n = node.incoming[ni];
			var r = annotate_tree(n, node.depth);
			max = (r > max) ? r : max;
		}
		return max;
	}

	function layout_nodes(nodes, max_depth, width, height) {
		var padding = width * 0.18;
		var center = height / 2.0;
		var space = width - padding * 2;
		var spacing = space / max_depth;
	var max_height = height * 0.8;
	if (spacing > max_height) {
	  spacing = max_height;
	}
		var offset = spacing * Math.sqrt(3.0) / 2.0;
		console.log(padding, center, space,spacing, offset);

		for (var ni in nodes) {
			var n = nodes[ni];
			n.x = padding + (max_depth - n.depth) * spacing;
			if (n.type == "entity") {
	  		n.y = center - (offset / 2.0);
			} else {
				n.y = center + (offset / 2.0);
			}
			n.fixed = true;
		}
	}

	var max_depth = annotate_tree(root,-1);
	console.log("MAX_DEPTH", max_depth);
	layout_nodes(nodes,max_depth,width,0.5*width);

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

	function detail_display_link(d) {
		d3.select("#detail-header").text(d.type);
		var table = d3.select("#detail");
		table.selectAll("*").remove();		
		svg.selectAll("#selection").remove();
	}

	function detail_display(d) {
		d3.select("#detail-header").text(d.label);
		var table = d3.select("#detail");
		table.selectAll("*").remove();
		var attribs = ["foundry:UUID","foundry:creationTime","prov:startTime","prov:endTime","foundry:how","foundry:label","foundry:version"];
		for (var a in attribs) {
			var attrib = attribs[a];
			var key = attrib.split(":")[1];
			if (d[attrib] != undefined) {
				var row = table.append("tr");
				row.append("td").text(key);
				row.append("td").text(d[attrib]);
			}
		}
		svg.selectAll("#selection").remove();
		svg.insert("circle",":first-child").attr("r",21).style("fill","url(#selected-gradient)").attr("cx",d.x).attr("cy",d.y).attr("id","selection");
	}
	
	var node_updates = svg.selectAll(".node").data(nodes);
	var node_enter = node_updates.enter().append("g").attr("class","node").attr("transform", function(d){return "translate("+d.x+","+d.y+")";});

	var circles = node_enter.filter(function(d,i) {return d.type == "activity"}).append("circle").attr("r", 15)
		.style("fill", function(d) { return colors(d.group); })
		.on("mouseover", detail_display);
	var squares = node_enter.filter(function(d,i) {return d.type=="entity"}).append("rect").attr("width",26).attr("height",26)
		.attr("transform","translate(-13,-13)")
		.style("fill", function(d) { return colors(d.group); })
		.on("mouseover", detail_display);

	var labels = node_enter.append("text").text(function (d) { return d.label;})
	.attr("dy",function(d) {
		if (d.type == "entity") return -19;
		return 27;	
	}).attr("text-anchor","middle").attr("font-weight","100").attr("letter-spacing","1px");
	
	var link_updates = svg.selectAll(".link").data(links)
		.enter().append("path").attr("class","link")
		.attr("stroke-dasharray",function(d) {
			if (d.type=="wasDerivedFrom") return "5,5";
			return "";
		}).attr("marker-end", 'url(#end-arrow)')
		.on("mouseover", detail_display_link);
		
//		.on("mouseover", function(d) {
//			d3.select("#detail").text(d.type);
//		});
	
	force.on("tick", function() {
	link_updates.attr("d",function(d){
		var deltaX = d.target.x - d.source.x,
			deltaY = d.target.y - d.source.y,
			dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY),
			normX = deltaX / dist,
			normY = deltaY / dist,
			sourcePadding = 15,
			targetPadding = 17,
			sourceX = d.source.x + (sourcePadding * normX),
			sourceY = d.source.y + (sourcePadding * normY),
			targetX = d.target.x - (targetPadding * normX),
			targetY = d.target.y - (targetPadding * normY);
		return 'M' + sourceX + ',' + sourceY + 'L' + targetX + ',' + targetY;
	});
	
	node_updates.attr("transform", function(d){return "translate("+d.x+","+d.y+")";});
//    node_updates.attr("cx", function(d) { return d.x; })
//        .attr("cy", function(d) { return d.y; });
//  detail_display(entities[entities.length - 1]);
  });

  console.log("selecting last entity", nodes[nodes.length - 1]);
  detail_display(nodes[nodes.length - 1]);

});
