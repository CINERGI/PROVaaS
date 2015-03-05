var nodes=[],node_pos={},links=[],edge_defs={used:{source:"prov:entity",target:"prov:activity"},wasGeneratedBy:{source:"prov:activity",target:"prov:entity"},wasDerivedFrom:{source:"prov:usedEntity",target:"prov:generatedEntity"},wasInformedBy:{source:"prov:informant",target:"prov:informed"}},width=400,height=200,colors=d3.scale.category10(),svg=d3.select("div#graph").append("svg").attr("width",width).attr("height",height),force=d3.layout.force().charge(-20).linkDistance(120).size([width,height]),
query={},qs=window.location.search.substr(1).split("&");console.log("qs",qs);qs.forEach(function(b,t,x){b=b.split("=");k=b[0];v=b[1];console.log(k,v);query[k]=v});console.log("query: ",query);var source=query.source,source=source||"document.json";
d3.json(source,function(b){function t(a,b){if(void 0!=a.depth)return a.depth;a.depth="entity"==a.type?Math.floor(b+1):b+.5;console.log("WALKING",a,a.depth);var l=a.depth,f;for(f in a.incoming)var e=t(a.incoming[f],a.depth),l=e>l?e:l;return l}function x(a,b,l,f){var e=.18*l,d=f/2,c=l-2*e;l=c/b;f*=.8;l>f&&(l=f);f=l*Math.sqrt(3)/2;console.log(e,d,c,l,f);for(var g in a)c=a[g],c.x=e+(b-c.depth)*l,c.y="entity"==c.type?d-f/2:d+f/2,c.fixed=!0}function A(a){d3.select("#detail-header").text(a.type);d3.select("#detail").selectAll("*").remove();
svg.selectAll("#selection").remove()}function u(a){d3.select("#detail-header").text(a.label);var b=d3.select("#detail");b.selectAll("*").remove();var e="foundry:UUID foundry:creationTime prov:startTime prov:endTime foundry:how foundry:label foundry:version".split(" "),f;for(f in e){var c=e[f],d=c.split(":")[1];if(void 0!=a[c]){var g=b.append("tr");g.append("td").text(d);g.append("td").text(a[c])}}svg.selectAll("#selection").remove();svg.insert("circle",":first-child").attr("r",21).style("fill","url(#selected-gradient)").attr("cx",
a.x).attr("cy",a.y).attr("id","selection")}console.log("data loaded:",b);var m={},g=0,y={},q=[],e;for(e in b.activity){b.activity[e].raw=JSON.stringify(b.activity[e],null," ");b.activity[e].id=e;b.activity[e].type="activity";var p=Date.parse(b.activity[e]["prov:startTime"]);b.activity[e].timecode=p;b.activity[e].group=g;b.activity[e].incoming=[];b.activity[e].outgoing=[];b.activity[e].label=b.activity[e]["prov:type"].$;g=(g+1)%10;m[e]=e;q.push(b.activity[e])}q.sort(function(a,b){return a.timecode<
b.timecode?-1:a.timecode>b.timecode?1:0});console.log("activities:",q);e=[];var p={},d;for(d in b.entity){b.entity[d].raw=JSON.stringify(b.entity[d],null," ");b.entity[d].id=d;b.entity[d].type="entity";var h=b.entity[d]["foundry:UUID"],w=h+"@"+b.entity[d]["foundry:creationTime"],r=y[h];void 0==r&&(r=g,y[h]=r,g=(g+1)%10);b.entity[d].group=r;b.entity[d].incoming=[];b.entity[d].outgoing=[];h=b.entity[d]["foundry:label"].split("/");h=h[h.length-1];b.entity[d].label=h.substring(0,h.length-1);void 0==p[w]?
(e.push(b.entity[d]),p[w]=d,m[d]=d):m[d]=p[w]}nodes=q.concat(e);console.log("nodes:",nodes);if(!(0<function(a){for(var c in edge_defs)if(a=b[c])for(var e in a){var f=a[e],d=f[edge_defs[c].source],g=f[edge_defs[c].target];if(void 0==d||void 0==m[d])return console.log("FAILURE: UNRECOGNIZED SOURCE",d,"IN EDGE",f),1;d=m[d];if(void 0==g||void 0==m[g])return console.log("FAILURE: UNRECOGNIZED TARGET",g,"IN",c,"EDGE",f),1;for(var g=m[g],h=f=void 0,n=0;n<nodes.length;n++)nodes[n].id==d?f=nodes[n]:nodes[n].id==
g&&(h=nodes[n]);if(void 0==f)return console.log("FAILURE; COULD NOT RESOLVE SOURCE",d),1;if(void 0==h)return console.log("FAILURE; COULD NOT RESOLVE TARGET",g),1;links.push({source:f,target:h,type:c});f.outgoing.push(h);h.incoming.push(f)}return 0}(b))){console.log("links",links);var g=void 0,c;for(c in nodes)if(console.log(nodes[c].id,"in:",nodes[c].incoming.length,"out:",nodes[c].outgoing.length),0==nodes[c].outgoing.length)if(console.log("ROOT FOUND",nodes[c]),void 0==g)g=nodes[c];else return console.log("FAILURE: MULTIPLE ROOTS DETECTED"),
2;if(void 0==g)return console.log("FAILURE: NO ROOT FOUND"),2;console.log("ROOT",g);c=t(g,-1);console.log("MAX_DEPTH",c);x(nodes,c,width,.5*width);force.nodes(nodes).links(links).start();svg.append("svg:defs").append("svg:marker").attr("id","end-arrow").attr("viewBox","0 -5 10 10").attr("refX",6).attr("markerWidth",6).attr("markerHeight",6).attr("orient","auto").append("svg:path").attr("d","M0,-5L10,0L0,5").attr("fill","#000");c=svg.select("defs").append("radialGradient").attr("id","selected-gradient");
c.append("stop").attr("offset","65%").attr("stop-color","#F00");c.append("stop").attr("offset","100%").attr("stop-color","#FFF");var z=svg.selectAll(".node").data(nodes);c=z.enter().append("g").attr("class","node").attr("transform",function(a){return"translate("+a.x+","+a.y+")"});c.filter(function(a,b){return"activity"==a.type}).append("circle").attr("r",15).style("fill",function(a){return colors(a.group)}).on("mouseover",u);c.filter(function(a,b){return"entity"==a.type}).append("rect").attr("width",
26).attr("height",26).attr("transform","translate(-13,-13)").style("fill",function(a){return colors(a.group)}).on("mouseover",u);c.append("text").text(function(a){return a.label}).attr("dy",function(a){return"entity"==a.type?-19:27}).attr("text-anchor","middle").attr("font-weight","100").attr("letter-spacing","1px");var B=svg.selectAll(".link").data(links).enter().append("path").attr("class","link").attr("stroke-dasharray",function(a){return"wasDerivedFrom"==a.type?"5,5":""}).attr("marker-end","url(#end-arrow)").on("mouseover",
A);force.on("tick",function(){B.attr("d",function(a){var b=a.target.x-a.source.x,c=a.target.y-a.source.y,d=Math.sqrt(b*b+c*c),b=b/d,c=c/d;return"M"+(a.source.x+15*b)+","+(a.source.y+15*c)+"L"+(a.target.x-17*b)+","+(a.target.y-17*c)});z.attr("transform",function(a){return"translate("+a.x+","+a.y+")"})});console.log("selecting last entity",nodes[nodes.length-1]);u(nodes[nodes.length-1])}});