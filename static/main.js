// custom javascript


$(function() {
  console.log('jquery is working!')
  createGraph();
});

function createGraph() {

  // main config
  var width = 960; // chart width
  var height = 700; // chart height
  var format = d3.format(",d");  // convert value to integer
  var color = d3.schemeCategory20b  // create ordial scale with 20 colors
  var sizeOfRadius = d3.scalePow().domain([-100,100]).range([-50,50]);  // https://github.com/mbostock/d3/wiki/Quantitative-Scales#pow

  // bubble config
  var bubble = d3.pack()
    // .sort(null)  // disable sorting, use DOM tree traversal
    .size([width, height])  // chart layout size
    .padding(1)  // padding between circles
    .radius(function(d) { return 20 + (sizeOfRadius(d) * 60); });  // radius for each circle

  // svg config
  var svg = d3.select("#chart").append("svg") // append to DOM
    .attr("width", width)
    .attr("height", height)
    .attr("class", "visual");

  var chart = d3.select("#chart");

  // tooltip config
  var tooltip = d3.select("body")
    .append("div")
    .style("position", "absolute")
    .style("z-index", "10")
    .style("visibility", "hidden")
    .style("color", "white")
    .style("padding", "8px")
    .style("background-color", "rgba(0, 0, 0, 0.75)")
    .style("border-radius", "6px")
    .style("font", "12px sans-serif")
    .text("tooltip");

  // TODO(kjchavez): Use relative path for url.
  var ws = new WebSocket("ws://127.0.0.1:5000/FaceDetection");
  console.log("Hostname is " + window.location.hostname);
  var faces = []
  ws.onmessage = function (event) {
    console.log(typeof(event.data));
    var new_face = jQuery.parseJSON(event.data);
    console.log(faces);
    faces = [new_face];
    render();
  };
  
  function render() {
    var nodes = svg.selectAll('.FaceDetection')
      .data(faces)

    nodes.enter()
        .append('rect')
        .attr('fill-opacity', 0.05)
        .attr('stroke', 'green')
        .attr('stroke-width', '2')
        .attr('class', 'FaceDetection');

    nodes.exit().remove();
    nodes.attr('x', function(d) { return d.bbox.x; })
         .attr('y', function(d) { return d.bbox.y; })
         .attr('width', function(d) { return d.bbox.w; })
         .attr('height', function(d) { return d.bbox.h; })
  }

  // request the data
  /*
  d3.json("/FaceDetection", function(error, faces) {
    console.log(faces)
    if (error) throw error;
    var node = svg.selectAll('.FaceDetection')
      .data([faces])
        .enter()
        .append('rect')
        .attr('x', function(d) { return d.bbox.x; })
        .attr('y', function(d) { return d.bbox.y; })
        .attr('width', function(d) { return d.bbox.w; })
        .attr('height', function(d) { return d.bbox.h; })
        .attr('fill-opacity', 0.05)
        .attr('stroke', 'green')
        .attr('stroke-width', '2')
        .attr('class', 'FaceDetection');
  });
  */
}
