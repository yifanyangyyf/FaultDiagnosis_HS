# coding=UTF-8
import numpy as np
import random
import MySQLdb
import time



class MainBlock(object):
	"""docstring for MainBlock"""
	def __init__(self):
		super(MainBlock, self).__init__()

		self._29 = list();
		self._30 = list();

		self._output = list();

###########################################################
# 01-Process the data
###########################################################
	def LoadData(self,feature,name,startTime,endTime):
		database = MySQLdb.connect('localhost','root','qwert','FaultDiagnosis');
		with database:
			cursor = database.cursor();
			cursor.execute('SELECT PublicationDate,{0} FROM Status_sensor WHERE id >= \'{1}\' AND id <= \'{2}\''.format(name,startTime,endTime));
			data = cursor.fetchall();
			for datum in data:
				feature.append([datum[0],float(datum[1])]);
			cursor.close();
		database.close();


	def outputReport(self,threshold,startTime):
		# analyze feature
		for index in xrange(len(self._29)):
			if self._29[index][1] > threshold['Turbid']:
				self._output.append([self._29[index][0],1,'油中混水','油质污染','油中混水超标']);
			elif self._30[index][1] > threshold['Impurity']:
				self._output.append([self._29[index][0],1,'杂质颗粒度过多','油质污染','杂质颗粒度过多']);
			else:
				self._output.append([self._29[index][0],0,'正常','油质污染','无']);

		# print self._output


		# edit log
		log_record = list();
		for index in xrange(len(self._output)):
			if index == 0:
				continue;

			if self._output[index][1] == 1 and self._output[index-1][1] == 0:
				log_record.append([self._output[index][0],self._output[index][2],self._output[index][3],self._output[index][4]]);
			elif self._output[index][1] == 1 and self._output[index-1][1] == 1 and self._output[index][2] != self._output[index-1][2]:
				log_record.append([self._output[index][0],self._output[index][2],self._output[index][3],self._output[index][4]]);

		# input log
		database = MySQLdb.connect('localhost','root','qwert','FaultDiagnosis');
		with database:
			cursor = database.cursor();
			for index in xrange(len(log_record)):
				cursor.execute('INSERT into Status_log(PublicationDate,LogInformation,ErrorEquipment,Reason) values(\'{0}\',\'{1}\',\'{2}\',\'{3}\')'.format(log_record[index][0],log_record[index][1],log_record[index][2],log_record[index][3]));
				database.commit();
			cursor.close();
		database.close();


		# input analysis
		database = MySQLdb.connect('localhost','root','qwert','FaultDiagnosis');
		with database:
			cursor = database.cursor();
			for x in xrange(len(self._output)):
				cursor.execute('INSERT into Status_prediction(id,PublicationDate,YouZhiWuRan_7) values(\'{0}\',\'{1}\',\'{2}\')'.format(x+startTime,self._output[x][0],self._output[x][1]));
				database.commit();
			cursor.close();
		database.close();

		


def main():
	# initialize
	startTime = 1501;
	endTime = startTime+99;
	threshold = {'Turbid':0.5,'Impurity':0.7};

	task = MainBlock();

	variableName = ['TurbidWaterSignal_29','ImpurityParticlesSignal_30'];
	variable = [task._29,task._30];
	for index in range(len(variable)):
		task.LoadData(variable[index],variableName[index],startTime,endTime);

	task.outputReport(threshold,startTime);




if __name__ == '__main__': main();