set term postscript eps color enh "Times-BoldItalic"

set title "Accuracy"
set output "plot/accuracy.ps"
plot "plot/tmp" using 1:2 title "general Classifier" with lines, "plot/tmp" using 1:5 title "RDT" with linespoints

set title "Training Time"
set output "plot/training.ps"
plot "plot/tmp" using 1:3 title "general Classifier" with lines, "plot/tmp" using 1:6 title "RDT" with linespoints

set title "Classification Time"
set output "plot/classification.ps"
plot "plot/tmp" using 1:4 title "general Classifier" with lines, "plot/tmp" using 1:7 title "RDT" with linespoints


set title "Memory Usage"
set output "plot/memory.ps"
