#!/bin/bash

ignore=""
trees=""
thresholds=""
plot_conf="plot.plt"
outfile="classified.arff"
tmp="tmp"
dir="plot"
percentual=1
step=10

function ignore_par(){
	for i in $@; do
		if [ ${i:0:2} != "--" ]; then
			if [ $i != $1 ] && [ $i != $2 ]; then
				ignore="$ignore $i"
			fi
		fi
	done
}

# The following executes the algorithms with several percentage of the dataset in cross validation
# with step of 10%
function simulation(){
  while [ "$percentual" -le 100 ]; do
	echo -e "\nTaking the $percentual% of the dataset as training elements"
	
	echo "Executing general classifier algorithm"
	generalClass=`./nukeminer.py -t $1 -a $2 $3 -o $outfile -x $percentual -c generalClass$thresholds`
        generalClass=`echo $generalClass | awk '{print $3} {print $7} {print $11} {print $14} {print $17} {print $20}'`
	
	train_data="cv_train_$percentual.arff"
	test_data="cv_test_$percentual.arff"

	echo "Execution random decision tree algorithm"
	randomDT=`./nukeminer.py -t $train_data -d $test_data -a $2 $3 -o $outfile -x 0 -c randomDT$trees`
	echo "Tree generated = `echo $randomDT | awk '{print $3}'`"
	echo "Tree depth = `echo $randomDT | awk '{print $7}'`"
	randomDT=`echo $randomDT | awk '{print $10} {print $14} {print $18} {print $21} {print $24} {print $27}'`
	
	line="$percentual   $generalClass   $randomDT"
	echo $line >> "$dir/$tmp"
	if [ $percentual -eq 1 ]; then
		let "percentual += 9"	       
	else
		let "percentual += $step"
	fi
  done
}

function plot(){
	if [ "$dir" != "plot" ]; then
		sed "s/plot\//$dir\//" plot_spec.plt > $dir/$plot_conf
	else
		cp plot_spec.plt $dir/$plot_conf
	fi
	gnuplot $dir/$plot_conf
}

# Check presence of at least two arguments
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

# Parse parameters in order to gather the "Number of Trees for RandomDT" and "Number of threshold for generalClassifier"
for i in $@;  do
	if [ ${i:0:2} == "--" ]; then
		parameter=${i#--}
		parameter=${parameter%=*}
		value=${i##*=}
		if [ $parameter == "trees" ]; then
			trees=",$value"
		fi
		if [ $parameter == "thresholds" ]; then
			thresholds=",$value"
		fi
	fi
done

# Modify the Text of each graphs


# Recall simulation function passing the two input arguments
echo "Starting evaluation of algorithms:"
ignore_par $@
if [ "$ignore" == "" ]; then
	simulation $1 $2
else
	simulation $1 $2 "-i $ignore"
fi

plot

rm $dir/$tmp
rm $outfile
rm cv_train*
rm cv_test*
rm $dir/$plot_conf

exit 0
