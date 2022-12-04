# Rush-hour

READ ME: https://github.com/coreycchan/Rush-hour.git

To run the code on different search algorithms
You just need to uncomment whichever one you wish to use and then comment the other in the main

To run different heuristics: 
    I implemented UCS in my A/A* search via a null heuristics therefore it only keeps track of g(h) or cost
    at bfsSearch = 0 for A/A* method, you get UCS

    UNCOMMENT Solver.aStarSearch() and COMMENT Solver.greedySearch()
    change the value of bfsSearch in the main from 0-4 inclusively for A/A*
        Example: bfsSearch = 1 therefore you are using A/A* with h1
        Example: bfsSearch = 0 therefore you are using UCS

    UNCOMMENT Solver.greedySearch() and COMMENT Solver.aStarSearch()
    change the value of bfsSearch in the main from 1-4 inclusively for GBFS
        Example: bfsSearch = 1 therefore you are using GBFS with h1


    Output files for sample input given: 
        UCS.txt
        aStar-h1.txt
        aStar-h2.txt
        aStar-h3.txt
        aStar-h4.txt
        greedy-h1.txt
        greedy-h2.txt
        greedy-h3.txt
        greedy-h4.txt

    Sample file for 50 test cases: samples-test.txt
    Output files for 50 test cases: (did not have time to reformat)
        output-samples-UCS.txt
        output-samples-Astar-h1.txt
        output-samples-Astar-h2.txt
        output-samples-Astar-h3.txt
        output-samples-Astar-h4.txt
        output-samples-GBFS-h1.txt
        output-samples-GBFS-h2.txt
        output-samples-GBFS-h3.txt
        output-samples-GBFS-h4.txt
