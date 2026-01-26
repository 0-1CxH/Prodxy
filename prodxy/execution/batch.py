from prodxy.graph import ProdxyMxBuilder


class ProdxyMxBatchExecutor:
    def __init__(self, args):
        self.args = args
        self._load_input_data()
        self._prepare_output_data()
    
    

