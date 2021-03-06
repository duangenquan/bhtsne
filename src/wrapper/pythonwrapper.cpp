#include <iostream>
#include <boost/python.hpp>
#include <Python.h>

#include <cfloat>
#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <ctime>
#include "../core/tsne.h"

using namespace std;
namespace bp = boost::python;

#define DEBUG


class TSNEWrapper
{
public:
	int Process(char* datapath, char* outputpath, int verbose)
	{
#ifdef DEBUG
		printf("filepath = %s\n", datapath);
#endif
		auto temp = stdout;
		if(!verbose){
			freopen("/dev/null","w",stdout);
		}
			
		// Function that runs the Barnes-Hut implementation of t-SNE
		
		// Define some variables
	    int origN, N, D, no_dims, max_iter, *landmarks;
	    double perc_landmarks;
	    double perplexity, theta, *data;
        int rand_seed = -1;
        TSNE* tsne = new TSNE();

        // Read the parameters and the dataset
	    if(tsne->load_data(&data, &origN, &D, &no_dims, &theta, &perplexity, &rand_seed, &max_iter, datapath)) {

		    // Make dummy landmarks
            N = origN;
            int* landmarks = (int*) malloc(N * sizeof(int));
            if(landmarks == NULL) { printf("Memory allocation failed!\n"); exit(1); }
            for(int n = 0; n < N; n++) landmarks[n] = n;

		    // Now fire up the SNE implementation
		    double* Y = (double*) malloc(N * no_dims * sizeof(double));
		    double* costs = (double*) calloc(N, sizeof(double));
            if(Y == NULL || costs == NULL) { printf("Memory allocation failed!\n"); exit(1); }
		    tsne->run(data, N, D, Y, no_dims, perplexity, theta, rand_seed, false, max_iter);

		    // Save the results
		    tsne->save_data(Y, landmarks, costs, N, no_dims, outputpath);

            // Clean up the memory
		    free(data); data = NULL;
		    free(Y); Y = NULL;
		    free(costs); costs = NULL;
		    free(landmarks); landmarks = NULL;
        }
        delete(tsne);
	
		stdout = temp;

		return 0;
	}

};

BOOST_PYTHON_MODULE(libpytsne)
{
	using namespace boost::python;
	bp::class_<TSNEWrapper>("TSNEWrapper")
		.def("Process", &TSNEWrapper::Process);
}
