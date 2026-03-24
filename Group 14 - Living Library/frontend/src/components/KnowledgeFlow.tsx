import { FileText, Link2, Pill, MessageCircle, Play } from "lucide-react";

interface KnowledgeFlowProps {
  triplesCount?: number;
  documentsProcessed?: number;
}

const KnowledgeFlow = ({ triplesCount = 0, documentsProcessed = 0 }: KnowledgeFlowProps) => {
  const steps = [
    {
      icon: <FileText className="h-6 w-6" />,
      label: `${documentsProcessed || "PDF"}`,
      sublabel: documentsProcessed ? `${documentsProcessed} doc(s) ingested` : "No docs yet",
      color: "border-primary bg-primary/10 text-primary",
    },
    {
      icon: <Link2 className="h-6 w-6" />,
      label: `${triplesCount}`,
      sublabel: `${triplesCount} logic points`,
      color: "border-chart-pink bg-chart-pink/10 text-chart-pink",
    },
    {
      icon: <Pill className="h-6 w-6" />,
      label: "Active",
      sublabel: "Compressed memory",
      color: "border-verified bg-verified/10 text-verified",
    },
    {
      icon: <MessageCircle className="h-6 w-6" />,
      label: "Output",
      sublabel: "Final answer",
      color: "border-warning bg-warning/10 text-warning",
    },
  ];

  const stepLabels = ["Input Source", "Shredded Triples", "Concept Capsule", "Reconstruction"];

  return (
    <div className="rounded-xl border p-6">
      <h2 className="text-xl font-bold">Provenance: Knowledge Flow</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        How your documents became compressed knowledge
      </p>
      <div className="mt-8 flex items-center justify-center gap-2">
        {steps.map((step, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className="flex flex-col items-center gap-2">
              <div
                className={`flex h-20 w-20 flex-col items-center justify-center rounded-xl border-2 ${step.color}`}
              >
                {step.icon}
                <span className="mt-1 text-xs font-bold">{step.label}</span>
              </div>
              <span className="text-xs font-semibold">{stepLabels[i]}</span>
              <span className="text-[10px] text-muted-foreground">{step.sublabel}</span>
            </div>
            {i < steps.length - 1 && (
              <Play className="mx-1 h-4 w-4 shrink-0 fill-primary text-primary" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default KnowledgeFlow;
