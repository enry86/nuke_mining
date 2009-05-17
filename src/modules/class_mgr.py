class ClassMgr:
    
    def __init__(self, tr_arff, cl_attr, ts_arff, alg, out_arff):
        attrs = tr_arff.get_attributes()
        out_arff.write_headers(attrs)
        data = tr_arff.get_next()
        while (data != None):
            out_arff.write_data(data)
            data = tr_arff.get_next()
        out_arff.store_buffer()

    def perform_test(self):
        print 'ulaula'
