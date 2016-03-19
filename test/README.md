### How to run test cases? ###
-----

#### iotx using python ``unittest`` test framework, there are two ways to run test cases ####

- First way

Executes the specified test suit

    python test_xxx.py

Perform a single test case, we need to modify the test set test_xxx.py


	def suite():
	    ###debug specify case
	    #suite = unittest.TestSuite()
	    #suite.addTest(myTestCases("testcase1"))
	
	    ###run all cases
	    suite = unittest.TestLoader().loadTestsFromTestCase(myTestCases)
	    return suite
	if __name__=="__main__":
	    unittest.main(defaultTest='suite')


To run all cases

    python runAll.py



- Second way

Executes the specified test suit
	
	python -m unittest xxx

To run all cases

	python -m unittest discover


- About debugging

You can open iotx debugging switch by modifying the code below in framework.py

		def serverThread(self):
		    #close log output
		    from tools import log
		    log.logSwitch('close') #you can delete this line to open debug switch
		    ServerClass.instance().run()