import { type TripleInfo } from "@/lib/api";

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  size: number;
}

interface Edge {
  from: string;
  to: string;
  label: string;
}

function buildGraph(triples: TripleInfo[]): { nodes: Node[]; edges: Edge[] } {
  const entitySet = new Set<string>();
  const edgeList: Edge[] = [];

  triples.forEach((t) => {
    entitySet.add(t.subject);
    entitySet.add(t.object);
    edgeList.push({ from: t.subject, to: t.object, label: t.relation });
  });

  const entities = Array.from(entitySet);
  // Lay out nodes in a circle
  const cx = 200, cy = 180, radius = 140;
  const nodes: Node[] = entities.map((label, i) => {
    const angle = (2 * Math.PI * i) / entities.length - Math.PI / 2;
    return {
      id: label,
      label,
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
      size: 16,
    };
  });

  return { nodes, edges: edgeList };
}

interface KnowledgeGraphProps {
  triples?: TripleInfo[];
}

const KnowledgeGraph = ({ triples = [] }: KnowledgeGraphProps) => {
  const { nodes, edges } = triples.length > 0
    ? buildGraph(triples.slice(0, 20))
    : { nodes: [], edges: [] };

  const getNode = (id: string) => nodes.find((n) => n.id === id);

  return (
    <div className="rounded-xl border p-6">
      <h2 className="text-xl font-bold">Knowledge Graph: Memory Map</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        {triples.length > 0
          ? `Showing ${Math.min(triples.length, 20)} triples as a graph`
          : "Ingest a document to see the graph"}
      </p>
      <div className="mt-4 flex justify-center">
        {nodes.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
            No triples available yet
          </div>
        ) : (
          <svg width="400" height="360" viewBox="0 0 400 360">
            {edges.map((edge, i) => {
              const from = getNode(edge.from);
              const to = getNode(edge.to);
              if (!from || !to) return null;
              return (
                <line
                  key={i}
                  x1={from.x}
                  y1={from.y}
                  x2={to.x}
                  y2={to.y}
                  stroke="hsl(var(--border))"
                  strokeWidth={1.5}
                />
              );
            })}
            {nodes.map((node) => (
              <g key={node.id}>
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={node.size}
                  fill="hsl(var(--primary))"
                />
                <text
                  x={node.x}
                  y={node.y + node.size + 14}
                  textAnchor="middle"
                  className="text-[10px] fill-current text-muted-foreground"
                >
                  {node.label.length > 12 ? node.label.slice(0, 12) + "…" : node.label}
                </text>
              </g>
            ))}
          </svg>
        )}
      </div>
    </div>
  );
};

export default KnowledgeGraph;
