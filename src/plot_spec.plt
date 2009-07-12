set term postscript eps enhanced color "Times-BoldItalic"
set xrange [0:100]
set xlabel "Percentage of input dataset as training examples"

set title "Accuracy <title>"
set ylabel "Probabilitiy"
set output "<plot dir>/accuracy.ps"
plot "<plot dir>/tmp" using 1:2 title "general Classifier" with lines, "plot/tmp" using 1:8 title "RDT" with linespoints

set title "Training Time <title>"
set ylabel "Time (s)"
set output "<plot dir>/training.ps"
plot "<plot dir>/tmp" using 1:3 title "general Classifier" with lines, "plot/tmp" using 1:9 title "RDT" with linespoints

set title "Classification Time <title>"
set ylabel "Time (s)"
set output "<plot dir>/classification.ps"
plot "<plot dir>/tmp" using 1:4 title "general Classifier" with lines, "plot/tmp" using 1:10 title "RDT" with linespoints

set title "Number of Nodes <title>"
set ylabel "Nodes"
set output "<plot dir>/nodes.ps"
plot "<plot dir>/tmp" using 1:5 title "general Classifier total nodes" with lines, "plot/tmp" using 1:6 title "general Classifier leaves nodes" with lines, "plot/tmp" using 1:11 title "RDT total nodes" with linespoints, "plot/tmp" using 1:12 title "RDT leaves nodes" with linespoints

set title "Memory Usage <title>"
set ylabel "Bytes"
set output "<plot dir>/memory.ps"
plot "<plot dir>/tmp" using 1:7 title "general Classifier" with lines, "plot/tmp" using 1:13 title "RDT" with linespoints
