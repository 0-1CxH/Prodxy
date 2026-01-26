import os
import json
import concurrent.futures
import asyncio

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
            self.output_handle = lambda x: print(x)
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
    
    async def __call__(self):
        # use self.args.parallelism to control the max concurrency
        # use self.input_data for each task graph's input
        # run self.graph_callable and collect its trace
        # log task trace and save along with output to self.ouput_handle
        
        # Prepare execution based on parallelism settings
        parallelism = getattr(self.args, 'parallelism', 1)

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(parallelism)

        async def process_item(i, input_item):
            async with semaphore:
                try:
                    # Execute the graph callable
                    result = await self.graph_callable(input_item)

                    # Handle output based on mode
                    if self.output_mode == "null":  
                        self.output_handle(result)
                    elif self.output_mode == "line":
                        self.output_handle(result)
                    elif self.output_mode == "file":
                        self.output_handle(i, result)
                except Exception as e:
                    # Log error but continue processing other items
                    print(f"Error processing input {i}: {e}")

        # Create tasks based on input mode
        tasks = []
        if self.input_mode == "null":
            # Execute graph_callable self.args.input times with no parameters
            for i in range(self.args.input):
                task = asyncio.create_task(process_item(i, None))
                tasks.append(task)
        elif self.input_mode == "file" or self.input_mode == "line":
            # Process each input item
            for i, input_item in enumerate(self.input_data):
                task = asyncio.create_task(process_item(i, input_item))
                tasks.append(task)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)


def parse_input_arg(value):
    """Parse input argument: if it's a number, return int, else return string."""
    try:
        # Try to convert to integer
        return int(value)
    except ValueError:
        # Return as string
        return value


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Execute Prodxy MX graph')
    parser.add_argument('--mx-config', '-m', required=True,
                        help='Path to MX configuration YAML file')
    parser.add_argument('--variant', '-v', required=True,
                        help='Variant name to use')
    parser.add_argument('--input', '-i', required=True, type=parse_input_arg,
                        help='Input: integer for null mode, or path to file/directory')
    parser.add_argument('--output', '-o', default=None,
                        help='Output: path to file (.jsonl) or directory (for .json files)')
    parser.add_argument('--parallelism', '-p', type=int, default=1,
                        help='Maximum parallel executions (default: 1)')

    args = parser.parse_args()

    # Create executor and run
    executor = ProdxyMxExecutor(args)
    asyncio.run(executor())


if __name__ == "__main__":
    main()        