// Example Plotly code
var data = [{
    x: [1, 2, 3, 4, 5],
    y: [10, 11, 12, 13, 14],
    type: 'scatter'
}];

var layout = {
    title: 'Flask Interactive Graph'
};

Plotly.newPlot('graph', data, layout,{displaylogo: false});
