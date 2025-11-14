import asyncio
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import statistics

from src.llm_config import get_llm
from src.associational_algorithm import AssociationalOntologyCreator
from src.generate_knowledge_graph import visualize_graph

from src.file_reader import read_text_file, read_csv_file, read_pdf_file, read_doc_file


# Track and report performance metrics for the knowledge graph pipeline
class PerformanceBenchmark:

    def __init__(self):
        self.metrics = {}
        self.start_times = {}

    def start_timer(self, operation: str):
        self.start_times[operation] = time.time()
  
    def end_timer(self, operation: str) -> float:
        if operation not in self.start_times:
            raise ValueError(f"Timer for '{operation}' was never started")
        
        elapsed = time.time() - self.start_times[operation]
        
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(elapsed)
        
        return elapsed
    
    def get_summary(self) -> Dict[str, Any]:
        summary = {}
        
        for operation, times in self.metrics.items():
            summary[operation] = {
                "total_runs": len(times),
                "total_time_seconds": sum(times),
                "average_time_seconds": statistics.mean(times),
                "min_time_seconds": min(times),
                "max_time_seconds": max(times),
                "median_time_seconds": statistics.median(times),
            }
            
            if len(times) > 1:
                summary[operation]["std_dev_seconds"] = statistics.stdev(times)
        
        return summary
    
    def print_report(self):
        summary = self.get_summary()
        
        print("\n" + "="*80)
        print("KNOWLEDGE GRAPH GENERATOR - PERFORMANCE BENCHMARK REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        total_pipeline_time = 0
        if "total_pipeline" in summary:
            total_pipeline_time = summary["total_pipeline"]["total_time_seconds"]
        
        for operation, stats in summary.items():
            print(f"\n{operation.upper().replace('_', ' ')}")
            print("-" * 80)
            print(f"  Total Runs:        {stats['total_runs']}")
            print(f"  Total Time:        {stats['total_time_seconds']:.3f} seconds")
            print(f"  Average Time:      {stats['average_time_seconds']:.3f} seconds")
            print(f"  Min Time:          {stats['min_time_seconds']:.3f} seconds")
            print(f"  Max Time:          {stats['max_time_seconds']:.3f} seconds")
            print(f"  Median Time:       {stats['median_time_seconds']:.3f} seconds")
            
            if 'std_dev_seconds' in stats:
                print(f"  Std Deviation:     {stats['std_dev_seconds']:.3f} seconds")
            
            if total_pipeline_time > 0 and operation != "total_pipeline":
                percentage = (stats['total_time_seconds'] / total_pipeline_time) * 100
                print(f"  % of Pipeline:     {percentage:.1f}%")
        
        print("\n" + "="*80)


# STEP 2: Replace single file reading with multi-file reading
async def benchmark_file_reading(benchmark: PerformanceBenchmark, file_paths: List[Path]) -> List[Dict]:
    """
    Read multiple files and return them in the same format as app.py.
    Returns a list of dicts with 'name' and 'content' keys.
    """
    benchmark.start_timer("file_reading")
    
    text_entries = []
    total_chars = 0
    
    try:
        for file_path in file_paths:
            file_extension = file_path.suffix.lower()
            
            try:
                if file_extension == ".txt":
                    content = read_text_file(file_path)
                    text_entries.append({"name": file_path.name, "content": content})
                    total_chars += len(content)
                    
                elif file_extension == ".csv":
                    # For CSV, read_csv_file returns a DataFrame
                    with open(file_path, 'rb') as f:
                        df = read_csv_file(f)
                        if df is not None:
                            content = df.to_string()
                            text_entries.append({"name": file_path.name, "content": content})
                            total_chars += len(content)
                        
                elif file_extension == ".pdf":
                    with open(file_path, 'rb') as f:
                        content = read_pdf_file(f)
                        text_entries.append({"name": file_path.name, "content": content})
                        total_chars += len(content)
                        
                elif file_extension == ".docx":
                    with open(file_path, 'rb') as f:
                        content = read_doc_file(f)
                        text_entries.append({"name": file_path.name, "content": content})
                        total_chars += len(content)
                else:
                    print(f"Warning: Unsupported file type: {file_path.name}")
                    
            except Exception as e:
                print(f"Error reading file {file_path.name}: {e}")
                continue
        
        elapsed = benchmark.end_timer("file_reading")
        print(f"File reading completed in {elapsed:.3f} seconds")
        print(f"  - Files read: {len(text_entries)}")
        print(f"  - Total size: {total_chars:,} characters")
        
        return text_entries
        
    except Exception as e:
        benchmark.end_timer("file_reading")
        print(f"File reading failed: {e}")
        raise


# STEP 4: Update LLM processing to use create_associational_ontology like app.py
async def benchmark_llm_processing(benchmark: PerformanceBenchmark, creator: AssociationalOntologyCreator, text_entries: List[Dict]) -> Any:
    """
    Process all text entries using create_associational_ontology, matching app.py behavior.
    """
    benchmark.start_timer("llm_processing")
    
    # Use the same method as app.py
    graph_document = await creator.create_associational_ontology(text_entries)
    
    elapsed = benchmark.end_timer("llm_processing")
    
    # Calculate statistics
    total_chars = sum(len(entry['content']) if isinstance(entry['content'], str) else len(str(entry['content'])) 
                     for entry in text_entries)
    
    print(f"LLM processing completed in {elapsed:.3f} seconds")
    print(f"  - Processed {len(text_entries)} documents")
    print(f"  - Total content size: {total_chars:,} characters")
    
    return graph_document


# STEP 6: Update visualization to work with GraphDocument instead of list
async def benchmark_graph_visualization(benchmark: PerformanceBenchmark, graph_document):
    benchmark.start_timer("graph_visualization")
    
    html_output = visualize_graph(graph_document)
    
    elapsed = benchmark.end_timer("graph_visualization")
    print(f"Graph visualization completed in {elapsed:.3f} seconds")
    print(f"  - HTML size: {len(html_output):,} characters")
    print(f"  - Total nodes: {len(graph_document.nodes)}")
    print(f"  - Total relationships: {len(graph_document.relationships)}")
    
    return html_output


# STEP 7: Update main benchmark function
async def run_full_benchmark(file_paths: List[str]):
    benchmark = PerformanceBenchmark()
    
    print("\n" + "=" * 80)
    print("STARTING MULTI-FILE BENCHMARK")
    print("=" * 80)
    print(f"Processing {len(file_paths)} file(s):")
    for fp in file_paths:
        print(f"  - {fp}")
    print("=" * 80)
    
    benchmark.start_timer("total_pipeline")
    
    # Convert string paths to Path objects
    path_objects = [Path(fp) for fp in file_paths]
    
    # Read all files
    print("\n[1/4] Reading files...")
    text_entries = await benchmark_file_reading(benchmark, path_objects)
    
    if not text_entries:
        print("No valid files were read. Exiting.")
        benchmark.end_timer("total_pipeline")
        return
    
    # Initialize creator
    print("\n[2/4] Initializing ontology creator...")
    init_start = time.time()
    creator = AssociationalOntologyCreator()
    init_time = time.time() - init_start
    print(f"Initialization completed in {init_time:.3f} seconds")
    
    # Process all documents with LLM (includes splitting, processing, and merging)
    print("\n[3/4] Processing documents with LLM...")
    print("  (This includes text splitting, chunk processing, and graph merging)")
    graph_document = await benchmark_llm_processing(benchmark, creator, text_entries)
    
    if not graph_document or not graph_document.nodes:
        print("No valid graph was generated. Skipping visualization.")
        benchmark.end_timer("total_pipeline")
        return
    
    # Generate visualization
    print("\n[4/4] Generating graph visualization...")
    html_output = await benchmark_graph_visualization(benchmark, graph_document)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output = output_dir / "test.html"
    
    output.write_text(html_output, encoding='utf-8')
    print(f"\nOutput saved to: {output}")
    
    elapsed = benchmark.end_timer("total_pipeline")
    print(f"\n{'=' * 80}")
    print(f"TOTAL PIPELINE TIME: {elapsed:.3f} seconds")
    print(f"{'=' * 80}")
    
    # Print final report
    benchmark.print_report()


# NEW: Simplified function for backend use
async def generate_knowledge_graph_html(
    file_paths: List[str],
    output_path: str
) -> bool:
    """
    Simplified function to generate a knowledge graph HTML file from input files.
    Perfect for using as a backend function.
    
    Args:
        file_paths: List of file paths to process
        output_path: Path where the HTML file should be saved
    
    Returns:
        Boolean indicating success
    
    Example:
        >>> success = await generate_knowledge_graph_html(
        ...     file_paths=['doc1.txt', 'doc2.pdf'],
        ...     output_path='output/my_graph.html'
        ... )
        >>> if success:
        ...     print("Graph generated successfully!")
    """
    result = await run_full_benchmark(
        file_paths=file_paths,
        output_path=output_path,
        print_report=False  # Don't print report for backend use
    )
    return result['success']