set term postscript eps enhanced color "Times-BoldItalic" 22
set xrange [0:100]
set xlabel "Percentage of input dataset as training examples"
set style line 1 lt 1 lw 3
set style line 2 lt 2 lw 3
set style line 3 lt 3 lw 3
set style line 4 lt 8 lw 3

set title "Accuracy <title>"
set ylabel "Probabilitiy"
set output "<plot dir>/accuracy.ps"
plot "<plot dir>/tmp" using 1:2 title "general Classifier" with lines ls 1, "plot/tmp" using 1:8 title "RDT" with linespoints ls 2

set title "Training Time <title>"
set ylabel "Time (s)"
set output "<plot dir>/training.ps"
plot "<plot dir>/tmp" using 1:3 title "general Classifier" with lines ls 1, "plot/tmp" using 1:9 title "RDT" with linespoints ls 2

set title "Classification Time <title>"
set ylabel "Time (s)"
set output "<plot dir>/classification.ps"
plot "<plot dir>/tmp" using 1:4 title "general Classifier" with lines ls 1, "plot/tmp" using 1:10 title "RDT" with linespoints ls 2

set title "Number of Nodes <title>"
set ylabel "Nodes"
set output "<plot dir>/nodes.ps"
plot "<plot dir>/tmp" using 1:5 title "general Classifier total nodes" with lines ls 1, "plot/tmp" using 1:6 title "general Classifier leaves nodes" with lines ls 4, "plot/tmp" using 1:11 title "RDT total nodes" with linespoints ls 2, "plot/tmp" using 1:12 title "RDT leaves nodes" with linespoints ls 3

set title "Memory Usage <title>"
set ylabel "Bytes"
set output "<plot dir>/memory.ps"
plot "<plot dir>/tmp" using 1:7 title "general Classifier" with lines ls 1, "plot/tmp" using 1:13 title "RDT" with linespoints ls 2
