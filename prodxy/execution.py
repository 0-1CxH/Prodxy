import os
import json
import concurrent.futures

from prodxy.graph import ProdxyMxBuilder

class ProdxyMxExecutor:
    def __init__(self, args):
        self.args = args
        self._load_input_data()
        self._prepare_output_handle()
        self._build_mx()
    
    def _load_input_data(self):
        if isinstance(self.args.input, int):
            self.input_mode = "null"
            self.input_data = None
        elif isinstance(self.args.input, str):
            self.input_data = []
            if os.path.isdir(self.args.input):
                self.input_mode = "file"
                for file in os.listdir(self.args.input):
                    if file.endswith(".json"):
                        with open(os.path.join(self.args.input, file), 'r') as f:
                            self.input_data.append(json.load(f))
            elif os.path.isfile(self.args.input) and self.args.input.endswith(".jsonl"):
                self.input_mode = "line"
                with open(self.args.input, 'r') as f:
                    for line in f:
                        self.input_data.append(json.loads(line))
            else:
                raise ValueError(f"unknown input: {self.args.input}")
        else:
            raise ValueError(f"unknown input mode: {self.args.input}")
    
    def _prepare_output_handle(self):
        if not self.args.output:
            self.output_mode = "null"
            self.output_handle = lambda x: None
        elif isinstance(self.args.output, str):
            if self.args.output.endswith(".jsonl"):
                self.output_mode = "line"
                # create file if not exists
                os.makedirs(os.path.dirname(self.args.output), exist_ok=True)
                # append to file
                self.output_handle = lambda x: open(self.args.output, 'a').write(json.dumps(x) + "\n")
            else:
                self.output_mode = "file"
                # create folder if not exists
                os.makedirs(self.args.output, exist_ok=True)
                # create new file by id and write
                self.output_handle = lambda i,x: open(os.path.join(self.args.output, f"{i}.json"), 'w').write(json.dumps(x))
        else:
            raise ValueError(f"unknown output: {self.args.output}")
    
    def _build_mx(self):
        self.mx = ProdxyMxBuilder.load_from_yaml(self.args.mx_config)
        self.graph_callable = self.mx(self.args.variant)
    
    def __call__(self):
        # use self.args.parallelism and self.args.threading for process/thread pool workers
        # use self.input_data for each task graph's input
        # run self.graph_callable and collect its trace
        # log task trace and save along with output to self.ouput_handle

        # Prepare execution based on parallelism settings
        max_workers = getattr(self.args, 'parallelism', 1)
        use_threads = getattr(self.args, 'threading', False)

        # Create executor
        if use_threads:
            executor_cls = concurrent.futures.ThreadPoolExecutor
        else:
            executor_cls = concurrent.futures.ProcessPoolExecutor

        # Execute tasks
        with executor_cls(max_workers=max_workers) as executor:
            if self.input_mode == "null":
                # Execute graph_callable self.args.input times with no parameters
                futures = []
                for i in range(self.args.input):
                    future = executor.submit(self.graph_callable, None)
                    futures.append((i, future))

                # Collect results
                for i, future in futures:
                    try:
                        result = future.result()
                        if self.output_mode == "null":
                            print(result)
                        elif self.output_mode == "line":
                            self.output_handle(result)
                        elif self.output_mode == "file":
                            self.output_handle((i, result))
                    except Exception as e:
                        # Log error but continue processing other items
                        print(f"Error processing null input {i}: {e}")
                        continue

            elif self.input_mode == "file" or self.input_mode == "line":
                # Process each input item
                futures = []
                for i, input_item in enumerate(self.input_data):
                    future = executor.submit(self.graph_callable, input_item)
                    futures.append((i, future))

                # Collect results
                for i, future in futures:
                    try:
                        result = future.result()
                        if self.output_mode == "null":
                            continue
                        elif self.output_mode == "line":
                            self.output_handle(result)
                        elif self.output_mode == "file":
                            self.output_handle((i, result))
                    except Exception as e:
                        # Log error but continue processing other items
                        print(f"Error processing input {i}: {e}")
                        continue

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Execute Prodxy MX workflow")
    parser.add_argument("--input", required=True,
                        help="Input specification: integer for null input count, directory path for JSON files, or .jsonl file path")
    parser.add_argument("--output",
                        help="Output specification: .jsonl file path for line output, directory path for file output, or omit for no output")
    parser.add_argument("--mx-config", required=True, dest="mx_config",
                        help="Path to MX configuration YAML file")
    parser.add_argument("--variant", default="default",
                        help="Variant name to use from MX configuration (default: default)")
    parser.add_argument("--parallelism", type=int, default=1,
                        help="Number of parallel workers (default: 1)")
    parser.add_argument("--threading", action="store_true",
                        help="Use threading instead of multiprocessing")

    args = parser.parse_args()

    # Convert input to appropriate type
    try:
        # Try to parse as integer first (for null input mode)
        args.input = int(args.input)
    except ValueError:
        # Keep as string for file/directory paths
        pass

    executor = ProdxyMxExecutor(args)
    executor()
