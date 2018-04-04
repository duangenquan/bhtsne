from common import *
from libpytsne import TSNEWrapper

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__
    
def read_unpack(fmt, fh):
    return unpack(fmt, fh.read(calcsize(fmt)))    

def bh_tsne(workdir, verbose=False):
    tsnewrapper = TSNEWrapper()

    if not verbose:
        blockPrint()

    # Call bh_tsne and let it do its thing
    inputfile = path_join(workdir, 'data.dat')
    outputfile = path_join(workdir, 'result.dat')
    
    tsnewrapper.Process(inputfile, outputfile)

    if not verbose:
        enablePrint()

    # Read and pass on the results
    with open(outputfile, 'rb') as output_file:
        # The first two integers are just the number of samples and the
        #   dimensionality
        result_samples, result_dims = read_unpack('ii', output_file)
        # Collect the results, but they may be out of order
        results = [read_unpack('{}d'.format(result_dims), output_file)
            for _ in range(result_samples)]
        # Now collect the landmark data so that we can return the data in
        #   the order it arrived
        results = [(read_unpack('i', output_file), e) for e in results]
        # Put the results in order and yield it
        results.sort()
        for _, result in results:
            yield result
        # The last piece of data is the cost for each sample, we ignore it
        #read_unpack('{}d'.format(sample_count), output_file)


def run_bh_tsne(data, no_dims=2, perplexity=50, theta=0.5, randseed=-1, verbose=False, initial_dims=50, use_pca=True, max_iter=1000):
    '''
    Run TSNE based on the Barnes-HT algorithm

    Parameters:
    ----------
    data: file or numpy.array
        The data used to run TSNE, one sample per row
    no_dims: int
    perplexity: int
    randseed: int
    theta: float
    initial_dims: int
    verbose: boolean
    use_pca: boolean
    max_iter: int
    '''

    # bh_tsne works with fixed input and output paths, give it a temporary
    #   directory to work in so we don't clutter the filesystem
    tmp_dir_path = mkdtemp()
    
    print("Initializing...")
    init_bh_tsne(data, tmp_dir_path, no_dims=no_dims, perplexity=perplexity, theta=theta, randseed=randseed,verbose=verbose, initial_dims=initial_dims, use_pca=use_pca, max_iter=max_iter)

    print("Initialized...")
    
    res = []
    for result in bh_tsne(tmp_dir_path, verbose):
        sample_res = []
        for r in result:
            sample_res.append(r)
        res.append(sample_res)
    rmtree(tmp_dir_path)
    return np.asarray(res, dtype='float64')


def main(args):
    parser = argparse()

    if len(args) <= 1:
        print(parser.print_help())
        return 

    argp = parser.parse_args(args[1:])
    
    for result in run_bh_tsne(argp.input, no_dims=argp.no_dims, perplexity=argp.perplexity, theta=argp.theta, randseed=argp.randseed,
            verbose=argp.verbose, initial_dims=argp.initial_dims, use_pca=argp.use_pca, max_iter=argp.max_iter):
        fmt = ''
        for i in range(1, len(result)):
            fmt = fmt + '{}\t'
        fmt = fmt + '{}\n'
        argp.output.write(fmt.format(*result))

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
