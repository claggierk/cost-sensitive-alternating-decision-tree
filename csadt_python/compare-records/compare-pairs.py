import sys
import os
import copy
import string
import re
import math
import pickle
import levenshtein
import adt_infrastructure

global trainingDataSet

def Usage():
	print "**************************************************"
	print "Usage  : python %s [text (.txt) input file] [text (.txt) output file]" % sys.argv[0]
	print "Example: python %s Data.txt ComparisonRecords.txt" % sys.argv[0]
	print "**************************************************"

def PopulateConditions(conditions_file):
	conditions_list = []
	conditions_file_handler = open(conditions_file, 'r')
	for line in conditions_file_handler:
		line = line.strip()
		conditions_list.append(line)
	conditions_file_handler.close()
	print "##### conditions_list: %s" % conditions_list
	return conditions_list

def main():
	global trainingDataSet
	for i, arg in enumerate(sys.argv):
		print "arg: %s: %s" % (i, arg) 
	argc = len(sys.argv)
	
	if argc != 3:
		Usage()
		return
	
	input_file = sys.argv[1]
	output_file = sys.argv[2]
	
	if os.path.exists(input_file):
		(records, keys) = adt_infrastructure.BuildDataStructure(input_file)
		trainingDataSet = {}
		
		#    n!
		#------------- = number of unique combinations
		#(n - r)! * r!
		
		num_records = len(records)
		print " ***** Number of records     : %s" % num_records
		
		print " Computing number of combinations..."
		num_combinations = math.factorial(num_records) / ( math.factorial(num_records - 2) * math.factorial(2) )
		print " ***** Number of combinations: %s" % num_combinations
		
		# test unique combinations for record linkage (duplicates)
		combination_pairs = []
		total_processed = 0
		number_of_matches = 0
		number_of_nonmatches = 0
		for combination_1 in range(num_records):
			total_processed = total_processed + (num_records - combination_1) - 1
			percent_complete = float(total_processed) / float(num_combinations) * 100
			print " ***** %.2f%% complete ----- total processed: %s" % (percent_complete, total_processed)
			for combination_2 in range(combination_1+1, num_records):
				tempDictionary = {}
				#import pdb; pdb.set_trace()
				if levenshtein.Compute_Levenshtein_Distance(records[combination_1]["eDuplicateID"], records[combination_2]["eDuplicateID"]) == 0:
					tempDictionary['class'] = 'SAME'
					number_of_matches += 1
				else:
					tempDictionary['class'] = 'DIFFERENT'
					number_of_nonmatches += 1
				for key in keys:
					levenshtein_distance = levenshtein.Compute_Levenshtein_Distance(records[combination_1][key], records[combination_2][key])
					tempDictionary[key] = levenshtein_distance
				
				combination_pair = str(combination_1) + '-' + str(combination_2)
				combination_pairs.append(combination_pair)

				# must have a similar name to be considered...
				#if tempDictionary["eLastName"] < 2 or tempDictionary["eFirstName"] < 2:
				#######print "%s %s %s" % (tempDictionary["eLastName"], tempDictionary["eFirstName"], tempDictionary["eNameTitle"])
				trainingDataSet[combination_pair] = tempDictionary

		print " ********** Running CSADT on %s combination pairs..." % len(trainingDataSet)
		#keys.remove("ID") # need to remove the key "ID" since it has no bearing anymore (and is not a key in the trainingDataSet dictionary)
		adt_infrastructure.OutputRecordsToFile(trainingDataSet, output_file, combination_pairs, keys, number_of_matches, number_of_nonmatches)
	else:
		Usage()
		return
	
if __name__ == "__main__":
	main()
