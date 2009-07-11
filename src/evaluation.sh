#!/bin/bash

outfile="classified.arff"
tmp="tmp"
dir="plot"
percentual=10

function ignore_par(){
	for i in $@; do
		if [ $i != $1 ] && [ $i != $2 ]; then
			ignore="$ignore $i"
		fi
	done
}

function simulation(){
  while [ "$percentual" -ne 100 ]; do
	echo -e "\nTaking the $percentual% of the dataset as training elements"
	#echo "Executing general classifier algorithm"
	#generalClass=`./nukeminer.py -t $1 -a $2 $3 -o $outfile -x $percentual`
        #generalClass=`echo $generalClass | awk '{print $1} {print $2} {print $3}'`
	echo "Execution random decision tree algorithm"
	randomDT=`./nukeminer.py -t $1 -a $2 $3 -o $outfile -x $percentual -c randomDT`
	randomDT=`echo $randomDT | awk '{print $1} {print $2} {print $3}'`
	line="$percentual   $generalClass   $randomDT"
	echo $line >> "$dir/$tmp"
	let "percentual += 10"	       
  done
}

function plot(){
	if [ "$dir" != "plot" ]; then
		sed "s/plot\//$dir\//" plot_spec.plt
	fi
	gnuplot plot_spec.plt
}

# Check presence of two arguments
if [ "$#" -lt "2" ]; then
	echo "Two arguments required"
	echo "Syntax is: $0 <dataset> <classifying attribute> [<list ignoring attributes>]" 
	exit 1
fi

# Create plot's directory 
cd $dir
if [ $? -ne 0 ]; then
	mkdir $dir;
else
	cd ..;
fi

# Recall simulation function passing the two input arguments
echo "Starting evaluation of algorithms:"
ignore_par $@
if [ $# -eq 2 ]; then
	simulation $1 $2 " "
else
	simulation $1 $2 "-i $ignore"
fi

plot

rm "$dir/$tmp"
rm "$outfile"

exit 0
