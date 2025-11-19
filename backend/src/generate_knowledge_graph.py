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
    
    if not graph_document:
        return None
    
    if not isinstance(graph_document, GraphDocument):
        return None

    net = Network(height="3000px", width="4000px", directed=True,
                     notebook=False, bgcolor="#222222", font_color="white", filter_menu=False, cdn_resources='remote')

    nodes = graph_document.nodes
    relationships = graph_document.relationships

    if not nodes and not relationships:
        return None

    node_dict = cleanNodes(nodes)

    valid_edges = []
    valid_node_ids = set()
    for rel in relationships:
        if hasattr(rel.source, 'id') and hasattr(rel.target, 'id'):
            rel.source.id = cleanUpText(rel.source.id)
            rel.target.id = cleanUpText(rel.target.id)
            if rel.source.id in node_dict and rel.target.id in node_dict:   
                node_dict[rel.target.id].properties['node_weight'] += 1
                node_dict[rel.source.id].properties['edge_weight'] += 1
                valid_edges.append(rel)
                valid_node_ids.update([rel.source.id, rel.target.id])

    for node_id in valid_node_ids:
        node = node_dict[node_id]
        try:
            docString = ""
            for doc in node.properties["document"]:
                docString += doc + ' '
            
            net.add_node(node.id, label=node.id, title=docString, group=node.type, node_weight=node.properties['node_weight'],
                          font={'size': 18, 'face': 'Arial', 'color': 'white', 'strokeWidth': 2, 'strokeColor': '#000000'})
        except Exception as e:
            continue

    for rel in valid_edges:
        try:
            net.add_edge(rel.source.id, rel.target.id, label=rel.type.lower(), edge_weight=node_dict[rel.target.id].properties['edge_weight'],
                          font={'size': 14, 'face': 'Arial', 'color': 'lightgray', 'strokeWidth': 1, 'strokeColor': '#000000'})
        except Exception as e:
            continue

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
    
    net.save_graph("temp_graph.html")
    html_file = Path("temp_graph.html")
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

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
(function(){
  console.log("[CentroidDebug] Script injected.");

  let stabilizationFired = false;
  let periodicViewLogger = null;

  document.addEventListener("DOMContentLoaded", function() {
    console.log("[CentroidDebug] DOMContentLoaded fired.");
    const waitForNetwork = setInterval(() => {
      const netReady = (typeof network !== "undefined");
      const nodesReady = (typeof nodes !== "undefined");
      const edgesReady = (typeof edges !== "undefined");
      console.log("[CentroidDebug] Polling network state:",
        { netReady, nodesReady, edgesReady });

      if (netReady && nodesReady && edgesReady) {
        clearInterval(waitForNetwork);
        console.log("[CentroidDebug] Network, nodes, edges available.");

        // Start periodic view position logging every 5 seconds
        if (!periodicViewLogger) {
          periodicViewLogger = setInterval(() => {
            try {
              const vp = network.getViewPosition();
              const sc = network.getScale();
              console.log("[CentroidDebug] Periodic view position:", vp, "scale:", sc);
            } catch(e) {
              console.log("[CentroidDebug] Error in periodic view logger:", e);
            }
          }, 5000);
        }

        network.once("stabilizationIterationsDone", () => {
          stabilizationFired = true;
          console.log("[CentroidDebug] stabilizationIterationsDone event.");
          computeAndCenterCentroid("stabilizationIterationsDone");
        });

        network.on("stabilized", (params) => {
          console.log("[CentroidDebug] stabilized event.", params);
          if (!stabilizationFired) {
            computeAndCenterCentroid("stabilized-fallback");
          }
        });

        setTimeout(() => {
          if (!stabilizationFired) {
            console.log("[CentroidDebug] Fallback timeout firing centroid compute.");
            computeAndCenterCentroid("timeout-fallback");
          }
        }, 3000);

        initFilterMenu();
      }
    }, 300);
  });

  function computeAndCenterCentroid(triggerSource) {
    console.log("[CentroidDebug] computeAndCenterCentroid called. Trigger:", triggerSource);
    if (typeof network === "undefined" || typeof nodes === "undefined") {
      console.log("[CentroidDebug] Aborting: network or nodes undefined.");
      return;
    }
    const positions = network.getPositions();
    const posKeys = Object.keys(positions);
    console.log("[CentroidDebug] Positions keys count:", posKeys.length);
    let sumX = 0, sumY = 0, count = 0;
    posKeys.forEach(id => {
      const nodeData = nodes.get(id);
      if (!nodeData) {
        console.log("[CentroidDebug] Node id missing in DataSet:", id);
        return;
      }
      if (!nodeData.hidden) {
        const p = positions[id];
        if (!p) {
          console.log("[CentroidDebug] Missing position for id:", id);
          return;
        }
        sumX += p.x;
        sumY += p.y;
        count++;
      }
    });
    console.log("[CentroidDebug] Visible node count for centroid:", count);
    if (count === 0) {
      console.log("[CentroidDebug] No visible nodes; skipping moveTo.");
      return;
    }
    const centerX = sumX / count;
    const centerY = sumY / count;
    window.graphCentroid = { x: centerX, y: centerY };
    console.log("[CentroidDebug] Computed centroid:", window.graphCentroid);
    console.log("[CentroidDebug] Current view position:", network.getViewPosition(), "scale:", network.getScale());
    network.moveTo({
      position: { x: 3036, y: 2620 },
      scale: .50,
      animation: { duration: 800, easingFunction: "easeInOutQuad" }
    });
    setTimeout(() => {
      console.log("[CentroidDebug] New view position (post moveTo):", network.getViewPosition(), "scale:", network.getScale());
    }, 900);
  }

  function initFilterMenu() {
    console.log("[CentroidDebug] initFilterMenu called.");
    // ...existing filter code...
  }
})();
</script>
"""

    network_div_marker = '<div id="mynetwork"'
    if network_div_marker in html_content:
        html_content = html_content.replace(network_div_marker, custom_filter_html + network_div_marker)
    
    body_close_marker = '</body>'
    if body_close_marker in html_content:
        html_content = html_content.replace(body_close_marker, custom_filter_js + body_close_marker)
    
    if html_file.exists():
        os.remove(html_file)
        
    return html_content

async def _save_graph_as(html_filepath: str, file_type: str) -> bytes | None:
    """A helper function to save the HTML graph to a specified format using Playwright."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            await page.goto(f"file://{os.path.abspath(html_filepath)}")
            await page.wait_for_load_state('networkidle')
            
            export_path = f"{Path(html_filepath).stem}.{file_type}"
            
            if file_type == "jpeg":
                bytes_data = await page.screenshot(path=export_path, type="jpeg", quality=100, full_page=True)
            elif file_type == "pdf":
                bytes_data = await page.pdf(path=export_path, format="A4", print_background=True)
            else:
                bytes_data = None
            
            await browser.close()
            
            if bytes_data and Path(export_path).exists():
                with open(export_path, 'rb') as f:
                    file_content = f.read()
                os.remove(export_path)
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
