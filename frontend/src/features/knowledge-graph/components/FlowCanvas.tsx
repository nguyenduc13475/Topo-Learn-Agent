"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
  Node,
  Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "@dagrejs/dagre";
import { ConceptNode } from "./ConceptNode";
import { apiClient } from "@/lib/api-client";
import { Loader2 } from "lucide-react";
import { Position } from "@xyflow/react";

interface FlowCanvasProps {
  documentId: number;
}

// Implemented Dagre for automatic directed acyclic graph (DAG) layouting
const getLayoutedElements = (
  nodes: Node[],
  edges: Edge[],
  direction = "TB",
) => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  const nodeWidth = 250; // Match actual Tailwind classes safely
  const nodeHeight = 100;

  // align: 'UL' to prevent isolated nodes from floating randomly
  dagreGraph.setGraph({
    rankdir: direction,
    nodesep: 60,
    ranksep: 120,
    align: "UL",
  });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: Position.Top,
      sourcePosition: Position.Bottom,
      position: {
        x: nodeWithPosition
          ? nodeWithPosition.x - nodeWidth / 2
          : Math.random() * 200,
        y: nodeWithPosition
          ? nodeWithPosition.y - nodeHeight / 2
          : Math.random() * 200,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};

export function FlowCanvas({ documentId }: FlowCanvasProps) {
  const router = useRouter();
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [isLoading, setIsLoading] = useState(true);

  const nodeTypes = useMemo(() => ({ concept: ConceptNode }), []);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const data = await apiClient<{ nodes: Node[]; edges: Edge[] }>(
          `/graph/${documentId}/flow`,
        );
        // Apply Dagre layout
        const { nodes: layoutedNodes, edges: layoutedEdges } =
          getLayoutedElements(data.nodes, data.edges);

        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
      } catch (error) {
        console.error("[FlowCanvas] Failed to load graph", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchGraph();
  }, [documentId, setNodes, setEdges]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (node.data.status !== "locked") {
        router.push(`/learn/${node.id}`);
      }
    },
    [router],
  );

  if (isLoading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-secondary/10">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="w-full h-full min-h-150 border border-border rounded-xl overflow-hidden bg-background shadow-sm">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        nodesConnectable={false}
        elementsSelectable={true}
        className="bg-secondary/10 cursor-default"
      >
        <Controls className="bg-background border-border shadow-md" />
        <MiniMap
          nodeStrokeColor={(n) => {
            if (n.data.status === "completed") return "#22c55e"; // green
            if (n.data.status === "current") return "hsl(var(--primary))";
            return "#888"; // locked
          }}
          nodeColor={(n) => {
            if (n.data.status === "completed") return "#22c55e20";
            if (n.data.status === "current") return "hsl(var(--primary) / 0.2)";
            return "hsl(var(--muted))";
          }}
          className="bg-background border border-border rounded-lg shadow-sm"
        />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}
