#!/bin/bash

plot_conf="plot_spec.plt"
outfile="classified.arff"
tmp="tmp"
dir="plot"
percentual=0

function ignore_par(){
	for i in $@; do
		if [ $i != $1 ] && [ $i != $2 ]; then
			ignore="$ignore $i"
		fi
	done
}

function dimensionality(){
	if [ $generalClass_mem_dim == $randomDT_mem_dim ]; then
		generalClass="$generalClass $generalClass_mem"
		randomDT="$randomDT $randomDT_mem"
		memory_dim=$generalClass_mem_dim
	fi

}

# The following executes the algorithms with several percentage of the dataset in cross validation
# with step of 10%
function simulation(){
  while [ "$percentual" -le 100 ]; do
	echo -e "\nTaking the $percentual% of the dataset as training elements"
	
	echo "Executing general classifier algorithm"
	generalClass=`./nukeminer.py -t $1 -a $2 $3 -o $outfile -x $percentual -c generalClass`
        generalClass_out=`echo $generalClass | awk '{print $3} {print $7} {print $11} {print $14} {print $17}'`
	generalClass_mem=`echo $generalClass | awk '{print $20}'`
	generalClass_mem_dim=`echo $generalClass | awk '{print $21}'`
	
	echo "Execution random decision tree algorithm"
	randomDT=`./nukeminer.py -t $1 -a $2 $3 -o $outfile -x $percentual -c randomDT`
	randomDT_out=`echo $randomDT | awk '{print $10} {print $14} {print $18} {print $21} {print $24}'`
	randomDT_mem=`echo $randomDT | awk '{print $27}'`
	randomDT_mem_dim=`echo $randomDT | awk '{print $28}'`
	
	dimensionality
	sed "s/<dimension>/$memory_dim/" $plot_conf > "$dir/$plot_conf"

	generalClass="$generalClass_out $generalClass_mem"
	randomDT="$randomDT_out $randomDT_mem"
	line="$percentual   $generalClass   $randomDT"
	echo $line >> "$dir/$tmp"
	let "percentual += 10"	       
  done
}

function plot(){
	if [ "$dir" != "plot" ]; then
		sed "s/plot\//$dir\//" plot_spec.plt
	fi
	gnuplot "$plot_conf"
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
#rm "$dir/$plot_conf"
rm "$outfile"

exit 0
