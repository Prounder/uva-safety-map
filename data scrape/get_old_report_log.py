import timing
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import re #for data parsing

##########Functions##########

count = 0
def counter(inc, printInc):
	global count
	if printInc == 0:
		count = 0
		#print(count)
	else:
		count += inc
		#if count%(printInc) == 0:
			#print(count)
	return count

def parse_log_data(log):
	data = log
	#if data[0].split(" ")[0] == "DAILY": #section header
		#date = "*" + data[1]
	if len(data) != 4:
		date, time, desc, loc = "*", "x", "x", "x"
	else:
		date, time = parse_date_time(data[2])
		desc, loc = parse_description(data[0])
	return [date, time, desc, loc]

def parse_date_time(datetime):
	#data = datetime.split(" ")
	data = re.split("[\s]+", datetime)
	#print(data)
	#date, time = "x", "x"
	date = data[2].strip()
	time = data[1].strip()
	return [date, time] #date, time

def parse_description(rawdata):
	#print(rawdata)
	data = re.split("[\–\-]", rawdata)
	#data = re.split("[^a-zA-Z0-9'\s]+", rawdata) #alphanumeric
	#print(data)
	if len(data) <= 1: return ["x", "x"]

	desc = data[0].strip()
	loc = find_address(data)
	return [desc, loc] #desc, location

def find_address(datalist):
	locdata = ""
	for string in datalist:
		string = string.strip()
		if re.match(r".*[0-9]$", string) != None:
			locdata = string
			#print(locdata)
			break
	if locdata == "": return "X"

	locdata = locdata.split()
	loc = " ".join(locdata[:-1]).strip()
	return loc

##########Code##########

driver = webdriver.Chrome()

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
years = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017"]

for year in years:
	raw_data_filename = year + "-raw.txt"
	parsed_data_filename = year + "-parsed.txt"

	raw_data_file = open(str(raw_data_filename), "w")
	parsed_data_file = open(str(parsed_data_filename), "w")

	raw_data_file.write("Crime Log: " + year + "\n")
	#parsed_data_file.write("Crime Log: "  + month + " " + year + "\n")
	parsed_data_file.write("Date\tTime\tLocation\tDescription\n")

	for month in months:
		driver.get("http://uvapolice.virginia.edu/crime-log-" + month + "-" + year)

		#Print all logs for month in year
		print("Printing logs for " + month + " " + year + "...")
		try:
			section = driver.find_element_by_class_name("field-type-text-with-summary")
			scraped_logs = section.find_elements_by_xpath(".//div/div/div")
			
			#Scrape logs into list
			log_list = [[]]
			counter(0, 0)
			for log in scraped_logs:
				line = log.text
				if line == " ": #indicator to begin new log
					log = []
					log_list.append(log)
					counter(1, 1)
				else: #add to current log
					log_list[-1].append(line) 

			print("Total sections scraped: " + str(count))

			#Print into output file
			counter(0, 0)
			for log in log_list:
				#for line in log:
					#raw_data_file.write(line + "\n")

				data = parse_log_data(log)
				date, time, desc, loc = data
				if date[0] != "*": # '*' indicating day header log entry
					parsed_data_file.write(date+"\t" + time+"\t" + loc+"\t" +desc + "\n")
					counter(1, 1) 

				raw_data_file.write("\n")

			print("Total logs printed: " + str(count))

		except NoSuchElementException:
			print("No logs found for " + month + " " + year)
			raw_data_file.write("No logs found for " + month + " " + year)

	raw_data_file.close()
	parsed_data_file.close()

driver.close()

