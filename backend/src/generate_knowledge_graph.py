import asyncio
import os
import traceback
from typing import List

from langchain_community.graphs.graph_document import GraphDocument
from pyvis.network import Network
from playwright.async_api import async_playwright
from pathlib import Path


def visualize_graph(graph_document: GraphDocument) -> str | None:
    """
    Visualizes a knowledge graph using PyVis based on the extracted graph documents.
    This function now expects to receive already processed GraphDocument objects.
    """
    #Might want to change input from a list to a dictionary
    #write function to format nodes and relationships so it isn't case sensitive



    # print("These are the nodes received: ", graph_document.nodes)
    # print("These are the relationships recieved: ", graph_document.relationships)
    
    if not graph_document:
        print("DEBUG: visualize_graph: No graph documents provided. Returning None.")
        return None
    
    # Check if the first item in graph_documents is valid before accessing attributes
    if not isinstance(graph_document, GraphDocument):
        print(f"DEBUG ERROR: visualize_graph: Expected GraphDocument, but received type: {type(graph_document)}. Content: {graph_document}")
        return None

    # MODIFIED: Set a large fixed width AND height for the PyVis network
    # This forces the iframe to expand correctly and display the graph without squishing.
    net = Network(height="3000px", width="4000px", directed=True, # Increased fixed width and height
                     notebook=False, bgcolor="#222222", font_color="white", filter_menu=False, cdn_resources='remote')

    nodes = graph_document.nodes
    relationships = graph_document.relationships

    print(f"DEBUG: visualize_graph: Nodes received: {len(nodes) if nodes else 0}")
    print(f"DEBUG: visualize_graph: Relationships received: {len(relationships) if relationships else 0}")

    if not nodes and not relationships:
        print("DEBUG: visualize_graph: No nodes or relationships extracted. Cannot create graph.")
        return None

    node_dict = cleanNodes(nodes)

    # print("Nodes after cleanup: ", node_dict)

    valid_edges = []
    valid_node_ids = set()
    for rel in relationships:
        # Ensure rel.source and rel.target are Node objects before accessing .id
        if hasattr(rel.source, 'id') and hasattr(rel.target, 'id'):
            rel.source.id = cleanUpText(rel.source.id)
            rel.target.id = cleanUpText(rel.target.id)
            if rel.source.id in node_dict and rel.target.id in node_dict:   
                node_dict[rel.target.id].properties['node_weight'] += 1
                node_dict[rel.source.id].properties['edge_weight'] += 1
                valid_edges.append(rel)
                valid_node_ids.update([rel.source.id, rel.target.id])
                if node_dict[rel.source.id].properties['document'] != node_dict[rel.target.id].properties['document']:
                    print("Different documents linked: ", rel)
                # print("Cleaned up relationship: ", rel)
                # print("New weights: ", node_dict[rel.target.id])
            else:
                print(f"DEBUG WARNING: visualize_graph: Relationship {rel.source.id}-{rel.type}->{rel.target.id} has missing source/target node in node_dict. Skipping.")
        else:
            print(f"DEBUG WARNING: visualize_graph: Relationship object is missing 'source' or 'target' id attribute. Relationship: {rel}. Skipping.")


    for node_id in valid_node_ids:
        node = node_dict[node_id]
        try:
            # need to create a string of the papers it is from
            docString = ""
            for doc in node.properties["document"]:
                docString += doc + ' '
            
            net.add_node(node.id, label=node.id, title=docString, group=node.type, node_weight=node.properties['node_weight'],
                          # Font options for better readability
                          font={'size': 18, 'face': 'Arial', 'color': 'white', 'strokeWidth': 2, 'strokeColor': '#000000'})
        except Exception as e:
            print(f"DEBUG ERROR: visualize_graph: Error adding node {node.id}: {e}")
            traceback.print_exc() # Print full traceback for node errors
            continue

    for rel in valid_edges:
        try:
            net.add_edge(rel.source.id, rel.target.id, label=rel.type.lower(), edge_weight=node_dict[rel.target.id].properties['edge_weight'],
                          # Font options for better readability on edges
                          font={'size': 14, 'face': 'Arial', 'color': 'lightgray', 'strokeWidth': 1, 'strokeColor': '#000000'})
        except Exception as e:
            print(f"DEBUG ERROR: visualize_graph: Error adding edge between {rel.source.id} and {rel.target.id}: {e}")
            traceback.print_exc() # Print full traceback for edge errors
            continue

    # Add 'interaction' options for zoom and navigation
    net.set_options("""
        {
            "physics": {
                "enabled": true,
                "solver": "forceAtlas2Based",
                "stabilization": {
                "enabled": true,
                "iterations": 150,
                "updateInterval": 25
                },
                "minVelocity": 0.1
            },
            "interaction": {
                "navigationButtons": true,
                "keyboard": true,
                "zoomView": true,
                "dragView": true
            },
            "nodes": {
                "shape": "dot",
                "size": 20,
                "font": {
                    "face": "Arial",
                    "color": "white",
                    "strokeWidth": 2,
                    "strokeColor": "#000000",
                    "multi": "html",
                    "vadjust": 0
                }
            },
            "edges": {
                "font": {
                    "face": "Arial",
                    "color": "lightgray",
                    "size": 14,
                    "strokeWidth": 1,
                    "strokeColor": "#000000",
                    "align": "middle"
                },
                "arrows": "to",
                "smooth": {
                    "enabled": true,
                    "type": "dynamic"
                }
            }
        }
    """)
    
    # Save to a temp file and return the HTML content
    net.save_graph("temp_graph.html")
    html_file = Path("temp_graph.html")
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Add custom filter HTML and JavaScript
    custom_filter_html = """
    <div class="card" style="width: 100%; margin-bottom: 10px;">
        <div class="card-header" style="background-color: #333; padding: 15px;">
            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                <select id="filterItem" style="padding: 8px; min-width: 150px;">
                    <option value="node" selected>Node</option>
                    <option value="edge">Edge</option>
                </select>
                <select id="filterProperty" style="padding: 8px; min-width: 150px;">
                    <option value="">Select Property</option>
                </select>
                <select id="filterValue" multiple style="padding: 8px; min-width: 200px; height: 100px;">
                    <option value="">Select a property first</option>
                </select>
                <button onclick="addCurrentFilter()" style="padding: 8px 20px; background-color: #007bff; color: white; border: none; cursor: pointer; border-radius: 4px;">Add Filter</button>
                <button onclick="resetAllFilters()" style="padding: 8px 20px; background-color: #6c757d; color: white; border: none; cursor: pointer; border-radius: 4px;">Reset</button>
            </div>
            <div id="active-filters" style="margin-top:10px; color:white;"></div>
        </div>
    </div>
"""
    
    custom_filter_js = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    // Wait for PyVis to load its global data
    const waitForNetwork = setInterval(() => {
        if (typeof network !== "undefined" && typeof nodes !== "undefined" && typeof edges !== "undefined") {
            clearInterval(waitForNetwork);

            // GLOBAL FIX: Always enable arrows once when network loads
            network.setOptions({
                edges: {
                    arrows: { to: { enabled: true } }
                }
            });
            network.redraw();

            initFilterMenu();
        }
    }, 300);
});

function initFilterMenu() {
    let filters = [];
    let filter = { item: 'node', property: '', value: [] };

    document.getElementById('filterItem').addEventListener('change', function() {
        filter.item = this.value;
        rebuildPropertyOptions();
    });

    document.getElementById('filterProperty').addEventListener('change', function() {
        filter.property = this.value;
        const valueSelect = document.getElementById('filterValue');
        valueSelect.innerHTML = '<option value="">Loading...</option>';

        if (!filter.property) {
            valueSelect.innerHTML = '<option value="">Select a property first</option>';
            return;
        }

        const allItems = (filter.item === 'node') ? nodes.get() : edges.get();
        const uniqueValues = new Set();
        allItems.forEach(item => {
            const val = item[filter.property];
            if (val !== undefined && val !== null) uniqueValues.add(String(val));
        });

        const sortedValues = Array.from(uniqueValues).sort((a, b) => {
            const numA = parseFloat(a), numB = parseFloat(b);
            if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
            return a.localeCompare(b);
        });

        valueSelect.innerHTML = '';
        sortedValues.forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            valueSelect.appendChild(option);
        });

    });

    function rebuildPropertyOptions() {
        const propertySelect = document.getElementById('filterProperty');
        propertySelect.innerHTML = '<option value="">Select Property</option>';
        const sample = (filter.item === 'node') ? nodes.get()[0] : edges.get()[0];
        if (!sample) return;
        Object.keys(sample).forEach(key => {
            const opt = document.createElement('option');
            opt.value = key;
            opt.textContent = key;
            propertySelect.appendChild(opt);
        });
    }

    window.addCurrentFilter = function() {
        const valueSelect = document.getElementById('filterValue');
        filter.value = Array.from(valueSelect.selectedOptions).map(opt => opt.value);
        if (!filter.property || filter.value.length === 0) {
            alert('Please select a property and at least one value.');
            return;
        }

        filters.push({ item: filter.item, property: filter.property, value: [...filter.value] });
        applyFilters();
        renderActiveFilters();
    }

    function applyFilters() {
        const allNodes = nodes.get({ returnType: "Object" });
        const allEdges = edges.get({ returnType: "Object" });

        let visibleNodes = new Set(Object.keys(allNodes));
        let visibleEdges = new Set(Object.keys(allEdges));

        filters.forEach(f => {
            const passingNodes = new Set();
            const passingEdges = new Set();

            if (f.item === 'node') {
                for (let id in allNodes) {
                    const val = allNodes[id][f.property];
                    if (val !== undefined && f.value.includes(String(val))) {
                        passingNodes.add(id);
                    }
                }
            } else if (f.item === 'edge') {
                for (let id in allEdges) {
                    const val = allEdges[id][f.property];
                    if (val !== undefined && f.value.includes(String(val))) {
                        passingEdges.add(id);
                        passingNodes.add(allEdges[id].from);
                        passingNodes.add(allEdges[id].to);
                    }
                }
            }

            visibleNodes = new Set([...visibleNodes].filter(id => passingNodes.has(id)));
            visibleEdges = new Set([...visibleEdges].filter(id => passingEdges.has(id)));
        });

        const updateNodeArray = [];
        for (let id in allNodes) {
            allNodes[id].hidden = filters.length > 0 && !visibleNodes.has(id);
            updateNodeArray.push(allNodes[id]);
        }
        nodes.update(updateNodeArray);

        const updateEdgeArray = [];
        for (let id in allEdges) {
            const e = allEdges[id];
            const bothVisible = visibleNodes.has(e.from) && visibleNodes.has(e.to);
            const shouldShow =
                filters.length === 0 ||
                visibleEdges.has(id) ||
                bothVisible;

            updateEdgeArray.push({
                ...e,
                hidden: !shouldShow
            });
        }
        edges.update(updateEdgeArray);
    }

    window.resetAllFilters = function() {
        filters = [];
        const allNodes = nodes.get({ returnType: "Object" });
        const allEdges = edges.get({ returnType: "Object" });
        const nodeUpdates = Object.values(allNodes).map(n => ({ ...n, hidden: false }));
        const edgeUpdates = Object.values(allEdges).map(e => ({ ...e, hidden: false }));
        nodes.update(nodeUpdates);
        edges.update(edgeUpdates);
        renderActiveFilters();
    }

    function renderActiveFilters() {
        const container = document.getElementById('active-filters');
        if (filters.length === 0) {
            container.innerHTML = "<i>No active filters</i>";
            return;
        }

        container.innerHTML = filters.map((f, i) =>
            `<span style="color:white; background:#555; padding:3px 6px; border-radius:4px; margin-right:5px;">
                ${f.item}.${f.property}: ${f.value.join(', ')}
                <button onclick='removeFilter(${i})' style='margin-left:5px; background:red; color:white; border:none; border-radius:3px; cursor:pointer;'>×</button>
            </span>`
        ).join('');
    }

    window.removeFilter = function(index) {
        filters.splice(index, 1);
        applyFilters();
        renderActiveFilters();
    }

    rebuildPropertyOptions();
}
</script>
"""
    
    # Insert custom filter before the network div
    network_div_marker = '<div id="mynetwork"'
    if network_div_marker in html_content:
        html_content = html_content.replace(network_div_marker, custom_filter_html + network_div_marker)
        print("Custom filter HTML successfully injected.")
    
    # Insert custom filter JS before closing body tag
    body_close_marker = '</body>'
    if body_close_marker in html_content:
        html_content = html_content.replace(body_close_marker, custom_filter_js + body_close_marker)
        print("Custom filter JS successfully injected.")

    
    
    # Clean up the temp file
    if html_file.exists():
        os.remove(html_file)
        
    print("DEBUG: visualize_graph: PyVis Network object created. Returning HTML content.")
    return html_content

async def _save_graph_as(html_filepath: str, file_type: str) -> bytes | None:
    """A helper function to save the HTML graph to a specified format using Playwright."""
    try:
        async with async_playwright() as p:
            # We use Chromium as it's the most reliable for our use case.
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Load the local HTML file
            await page.goto(f"file://{os.path.abspath(html_filepath)}")
            
            # Wait for the network to be idle to ensure all PyVis physics calculations are complete
            await page.wait_for_load_state('networkidle')
            
            # Define the export path
            export_path = f"{Path(html_filepath).stem}.{file_type}"
            
            # Take a screenshot and return the bytes
            if file_type == "jpeg":
                bytes_data = await page.screenshot(path=export_path, type="jpeg", quality=100, full_page=True)
            elif file_type == "pdf":
                bytes_data = await page.pdf(path=export_path, format="A4", print_background=True)
            else:
                print(f"DEBUG: Unsupported file type for export: {file_type}")
                bytes_data = None
            
            await browser.close()
            
            # Read the generated file and return its content
            if bytes_data and Path(export_path).exists():
                with open(export_path, 'rb') as f:
                    file_content = f.read()
                os.remove(export_path) # Clean up the exported file
                return file_content
            else:
                return None
    except Exception as e:
        print(f"DEBUG: Error in _save_graph_as: {e}")
        traceback.print_exc()
        return None

def save_graph_as_pdf(html_filepath: str) -> bytes | None:
    """Public function to save the graph as a PDF."""
    try:
        # We need to run the async function in a synchronous context
        return asyncio.run(_save_graph_as(html_filepath, "pdf"))
    except Exception as e:
        print(f"DEBUG: Error saving PDF: {e}")
        traceback.print_exc()
        return None
        
def save_graph_as_jpeg(html_filepath: str) -> bytes | None:
    """Public function to save the graph as a JPEG."""
    try:
        # We need to run the async function in a synchronous context
        return asyncio.run(_save_graph_as(html_filepath, "jpeg"))
    except Exception as e:
        print(f"DEBUG: Error saving JPEG: {e}")
        traceback.print_exc()
        return None
    
def cleanUpText(string):
    if not isinstance(string, str):
        string = str(string)

    cap = True
    newString = ""


    for i in string:
        if i in {" ", "_"}:
            newString += " "
            cap = True
        elif i.isalpha():
            if cap:
                newString += i.upper()
                cap = False
            else:
                newString += i.lower()
        else:
            newString += i
        
    return newString.strip()

def cleanNodes(nodeList):

    nodeDict = {}
    
    for node in nodeList:
        node.id = cleanUpText(node.id)
        node.properties["node_weight"] = 0
        node.properties["edge_weight"] = 0
        nodeDict[node.id] = node

    return nodeDict
