import re
import base64

def file_to_b64(filepath):
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

otel_b64 = file_to_b64("assets/icons/opentelemetry.png")
grafana_b64 = file_to_b64("assets/icons/grafana.png")

with open("architecture-target.drawio", "r") as f:
    xml = f.read()

# Fix ic-otel
xml = re.sub(
    r'(<mxCell id="ic-otel".*?image=)data:image/svg\+xml%3Bbase64,[^;]+(;.*?>)',
    r'\g<1>data:image/png;base64,' + otel_b64 + r'\g<2>',
    xml,
    flags=re.DOTALL
)

# Fix ic-grafana
xml = re.sub(
    r'(<mxCell id="ic-grafana".*?image=)data:image/svg\+xml%3Bbase64,[^;]+(;.*?>)',
    r'\g<1>data:image/png;base64,' + grafana_b64 + r'\g<2>',
    xml,
    flags=re.DOTALL
)

# Move step-1 so it doesn't overlap "all signals"
xml = re.sub(
    r'(<mxCell id="step-1".*?<mxGeometry x="270" y=")412(" width="30" height="30" as="geometry"/>)',
    r'\g<1>380\g<2>',
    xml
)

# Move step-2 so it doesn't overlap "sampling + PII..."
# old: x="500" y="585" -> let's move to bottom left of grp-policy: x="330" y="590"
xml = re.sub(
    r'(<mxCell id="step-2".*?<mxGeometry x="500" y=")585(" width="30" height="30" as="geometry"/>)',
    r'\g<1>620\g<2>',
    xml
)

with open("architecture-target.drawio", "w") as f:
    f.write(xml)

with open("diagrams/target-observability-aiops-architecture.drawio", "w") as f:
    f.write(xml)

print("Diagram fixed!")
